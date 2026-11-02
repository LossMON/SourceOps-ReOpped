import bpy
import re
from pathlib import Path
from .. utils import common

class SOURCEOPS_OT_PreviewVMT(bpy.types.Operator):
    bl_idname = 'sourceops.preview_vmt'
    bl_options = {'REGISTER', 'UNDO'}
    bl_label = 'Preview / Edit VMT'
    bl_description = 'Opens the VMT code in a Text Editor. The Text Editor has absolute priority unless you explicitly toggle UI checkboxes.'

    item_type: bpy.props.StringProperty()
    is_global: bpy.props.BoolProperty(default=False)

    def execute(self, context):
        prefs = common.get_prefs(context)
        game = common.get_game(prefs)
        sourceops = common.get_globals(context)
        model = common.get_model(sourceops)
        
        addon_name = common.clean_filename(Path(model.name).stem)
        
        if self.is_global:
            config = model
            mat_clean = f"GLOBAL_{addon_name}"
        elif self.item_type == 'SKIN':
            skin_item = model.skin_items[model.skin_index]
            mat_clean = skin_item.name
            mat_config = next((m for m in model.material_items if m.name == mat_clean), None)
            config = mat_config if mat_config else model
        else:
            config = model.material_items[model.material_index]
            mat_clean = config.name
            
        mat_raw = model.material_folder_items[0].name.replace('\\', '/').strip('/') if len(model.material_folder_items) > 0 else ''
        
        mat_qc_path = mat_raw
        while mat_qc_path.lower().startswith('materials/'):
            mat_qc_path = mat_qc_path[10:]
            
        basetexture_path = f"{mat_qc_path}/{mat_clean}" if mat_qc_path else mat_clean
        surface_prop = model.surface if hasattr(model, 'surface') else 'default'
        
        create_material_folder = getattr(sourceops, 'auto_create_material_folder', True)
        use_addon_folder = getattr(sourceops, 'auto_use_addon_folder', True)
        create_folders_alone = getattr(sourceops, 'auto_create_folders_alone', False)
        
        if game and getattr(game, 'models', ''):
            models_path = Path(game.models)
            if models_path.name.lower() == 'models':
                out_root = models_path.parent
            else:
                out_root = models_path
                
            if create_folders_alone:
                target_dir = out_root.joinpath('materials', mat_qc_path)
            elif create_material_folder:
                if use_addon_folder:
                    target_dir = out_root.joinpath(addon_name, 'materials', mat_qc_path)
                else:
                    target_dir = out_root.joinpath('materials', mat_qc_path)
            else:
                if use_addon_folder:
                    target_dir = out_root.joinpath(addon_name, mat_raw)
                else:
                    target_dir = out_root.joinpath(mat_raw)
                    
            vmt_path = target_dir.joinpath(f"{mat_clean}.vmt")
        else:
            vmt_path = Path(f"{mat_clean}.vmt")
        
        text_name = f"VMT_{mat_clean}.vmt"
        existing_text = bpy.data.texts.get(text_name)
        
        shader = getattr(config, "vmt_shader", "VertexLitGeneric")
        assigned_norm = getattr(config, "normal_map", "").strip()
        generate_normal = getattr(config, "vtf_normal_map", False)
        has_normal = generate_normal or bool(assigned_norm)
        vmt_trans = getattr(config, "vmt_translucent", False)
        vmt_alpha = getattr(config, "vmt_alphatest", False)
        
        if self.is_global:
            basetexture_display = "(DO NOT CHANGE THIS - APPLIES IT GLOBALLY)"
        else:
            basetexture_display = basetexture_path
        
        do_not_sort = getattr(config, "do_not_sort_vmts", False) or getattr(model, "do_not_sort_vmts", False)

        # -------------------------------------------------------------
        # 1. TRUE MANUAL OVERRIDE (DO NOT SORT VMTS)
        # -------------------------------------------------------------
        if do_not_sort:
            raw_lines = []
            if existing_text and len(existing_text.lines) > 0:
                raw_lines = [line.body for line in existing_text.lines]
            elif vmt_path and vmt_path.is_file():
                try:
                    with open(vmt_path, 'r') as f:
                        lines = f.read().splitlines()
                    raw_lines = [l for l in lines if not l.strip().startswith("// [SourceOps_State]")]
                except:
                    pass
            
            if not raw_lines:
                raw_lines = [
                    f'"{shader}"',
                    '{',
                    f'    "$basetexture" "{basetexture_display}"',
                    f'    "$surfaceprop" "{surface_prop}"',
                    '}'
                ]
            else:
                new_raw = []
                for l in raw_lines:
                    if not self.is_global:
                        if "(DO NOT CHANGE THIS - APPLIES IT GLOBALLY)" in l:
                            l = l.replace('"(DO NOT CHANGE THIS - APPLIES IT GLOBALLY)"', f'"{basetexture_path}"')
                            l = l.replace("(DO NOT CHANGE THIS - APPLIES IT GLOBALLY)", basetexture_path)
                    new_raw.append(l)
                raw_lines = new_raw

            final_lines = raw_lines

            if not existing_text:
                existing_text = bpy.data.texts.new(text_name)
            existing_text.clear()
            if self.is_global and not any("DO NOT CHANGE THIS - THE $basetexture APPLIES GLOBALLY" in l for l in final_lines):
                final_lines.insert(2, '    // (DO NOT CHANGE THIS - THE $basetexture APPLIES GLOBALLY, WILL BE REPLACED PER-MATERIAL ON EXPORT)')
            existing_text.write("\n".join(final_lines) + "\n")
            self._open_text_editor(context, existing_text, text_name)
            return {'FINISHED'}

        # -------------------------------------------------------------
        # 2. NORMAL VMT GENERATION (LIVE UI CONTROL)
        # -------------------------------------------------------------
        lines_to_parse = []
        if existing_text and len(existing_text.lines) > 0:
            lines_to_parse = [line.body for line in existing_text.lines]
        elif vmt_path and vmt_path.is_file():
            try:
                with open(vmt_path, 'r') as f:
                    lines_to_parse = f.read().splitlines()
            except:
                pass

        lines_to_parse = [l for l in lines_to_parse if not l.strip().startswith("// [SourceOps_State]")]
        custom_lines = []

        controlled_keys = [
            "$basetexture", "$bumpmap", "$surfaceprop", "$model", "$translucent", "$alphatest", "$nocull",
            "$envmap", "$envmaptint", "$envmapfresnel", "$normalmapalphaenvmapmask", "$basealphaenvmapmask",
            "$phong", "$phongboost", "$phongexponent", "$phongtint", "$phongalbedotint",
            "$phongfresnelranges", "$basemapalphaphongmask", "$reflectivity", "$envmapblur"
        ]

        if lines_to_parse:
            for raw_line in lines_to_parse:
                stripped = raw_line.strip()
                if not stripped: continue
                if "DO NOT CHANGE THIS - THE $basetexture APPLIES GLOBALLY" in stripped: continue
                lower_line = stripped.lower().replace('"', '')
                if lower_line in ["vertexlitgeneric", "unlitgeneric", "lightmappedgeneric"]: continue
                if lower_line in ["vertexlitgeneric {", "unlitgeneric {", "lightmappedgeneric {"]: continue
                if stripped in ("{", "}"): continue

                is_controlled = any(stripped.lower().startswith(c_key) or stripped.lower().startswith(f'"{c_key}"') for c_key in controlled_keys)
                if not is_controlled:
                    custom_lines.append(raw_line.rstrip('\n'))

        vmt_lines = [f'"{shader}"', '{']
        if self.is_global:
            vmt_lines.append('    // (DO NOT CHANGE THIS - THE $basetexture APPLIES GLOBALLY, WILL BE REPLACED PER-MATERIAL ON EXPORT)')

        vmt_lines.append(f'    "$basetexture" "{basetexture_display}"')
        
        # Bumpmap resolution
        bump_active = (has_normal or getattr(config, "vmt_phong", False))
        if has_normal:
            bump_val = "(DO NOT CHANGE THIS - APPLIES IT GLOBALLY)_normalmap" if self.is_global else f"{basetexture_path}_normalmap"
        else:
            bump_val = "dev/flat_normal"
            
        if bump_active:
            vmt_lines.append(f'    "$bumpmap" "{bump_val}"')
            
        vmt_lines.append(f'    "$surfaceprop" "{surface_prop}"')
        vmt_lines.append('    "$model" 1')

        if vmt_trans: vmt_lines.append('    "$translucent" 1')
        if vmt_alpha: vmt_lines.append('    "$alphatest" 1')
        if getattr(config, "vmt_nocull", False): vmt_lines.append('    "$nocull" 1')

        # Live Phong Specular ($phong) from UI
        if getattr(config, "vmt_phong", False):
            vmt_lines.append('    "$phong" "1"')
            vmt_lines.append(f'    "$phongboost" "{getattr(config, "vmt_phongboost", 1.0):.2f}"')
            vmt_lines.append(f'    "$phongexponent" "{getattr(config, "vmt_phongexponent", 25)}"')
            vmt_lines.append(f'    "$phongfresnelranges" "{getattr(config, "vmt_phongfresnelranges", "[0.05 0.5 1]")}"')
            if getattr(config, "vmt_phongalbedotint", False):
                vmt_lines.append('    "$phongalbedotint" "1"')
            else:
                pt = getattr(config, "vmt_phongtint", (1.0, 1.0, 1.0))
                if not (abs(pt[0] - 1.0) < 0.01 and abs(pt[1] - 1.0) < 0.01 and abs(pt[2] - 1.0) < 0.01):
                    vmt_lines.append(f'    "$phongtint" "[{pt[0]:.2f} {pt[1]:.2f} {pt[2]:.2f}]"')
            if getattr(config, "vmt_phongmask_source", "NORMAL_ALPHA") == "BASE_ALPHA":
                vmt_lines.append('    "$basemapalphaphongmask" "1"')

        # Live Cubemap Reflection ($envmap) from UI
        if getattr(config, "vmt_envmap", False):
            vmt_lines.append('    "$envmap" "env_cubemap"')
            et = getattr(config, "vmt_envmaptint", (0.3, 0.3, 0.3))
            vmt_lines.append(f'    "$envmaptint" "[{et[0]:.2f} {et[1]:.2f} {et[2]:.2f}]"')
            if getattr(config, "vmt_envmapfresnel", False):
                vmt_lines.append('    "$envmapfresnel" "1"')
            mask_src = getattr(config, "vmt_envmapmask_source", "NORMAL_ALPHA")
            if mask_src == "NORMAL_ALPHA" and bump_active:
                vmt_lines.append('    "$normalmapalphaenvmapmask" 1')
            elif mask_src == "BASE_ALPHA":
                vmt_lines.append('    "$basealphaenvmapmask" 1')

        if custom_lines:
            vmt_lines.append('')
            for cl in custom_lines:
                vmt_lines.append(cl)

        vmt_lines.append('}')
        vmt_content_ui = "\n".join(vmt_lines) + "\n"

        if not existing_text:
            existing_text = bpy.data.texts.new(text_name)
        existing_text.clear()
        existing_text.write(vmt_content_ui)

        self._open_text_editor(context, existing_text, text_name)
        return {'FINISHED'}

    def _open_text_editor(self, context, existing_text, text_name):
        existing_text.cursor_set(0, character=0)
        bpy.ops.wm.window_new()
        new_window = context.window_manager.windows[-1]
        area = new_window.screen.areas[0]
        area.type = 'TEXT_EDITOR'
        area.spaces.active.text = existing_text
        try:
            area.spaces.active.top = 0
        except:
            pass
        self.report({'INFO'}, f"Opened {text_name} in Text Editor!")


class SOURCEOPS_OT_ResetVMT(bpy.types.Operator):
    bl_idname = 'sourceops.reset_vmt'
    bl_options = {'REGISTER', 'UNDO'}
    bl_label = 'Reset VMT'
    bl_description = 'Resets the VMT UI checkboxes and generates a clean VMT text block.'

    item_type: bpy.props.StringProperty()
    is_global: bpy.props.BoolProperty(default=False)

    def execute(self, context):
        sourceops = common.get_globals(context)
        model = common.get_model(sourceops)
        addon_name = common.clean_filename(Path(model.name).stem)
        
        if self.is_global:
            config = model
            mat_clean = f"GLOBAL_{addon_name}"
        elif self.item_type == 'SKIN':
            skin_item = model.skin_items[model.skin_index]
            mat_clean = skin_item.name
            mat_config = next((m for m in model.material_items if m.name == mat_clean), None)
            config = mat_config if mat_config else model
        else:
            config = model.material_items[model.material_index]
            mat_clean = config.name
            
        config.vmt_shader = 'VertexLitGeneric'
        config.vmt_translucent = False
        config.vmt_alphatest = False
        config.vmt_nocull = False
        config.vmt_envmap = False
        config.vmt_envmaptint = (0.3, 0.3, 0.3)
        config.vmt_envmapfresnel = False
        config.vmt_envmapmask_source = 'NORMAL_ALPHA'
        config.vmt_phong = False
        config.vmt_phongboost = 1.0
        config.vmt_phongexponent = 25
        config.vmt_phongtint = (1.0, 1.0, 1.0)
        config.vmt_phongalbedotint = False
        config.vmt_phongfresnelranges = "[0.05 0.5 1]"
        config.vmt_phongmask_source = 'NORMAL_ALPHA'
        config.vtf_normal_map = False
        config.do_not_sort_vmts = False
        
        text_name = f"VMT_{mat_clean}.vmt"
        existing_text = bpy.data.texts.get(text_name)
        if not existing_text:
            existing_text = bpy.data.texts.new(text_name)
            
        existing_text.clear()
        
        mat_raw = model.material_folder_items[0].name.replace('\\', '/').strip('/') if len(model.material_folder_items) > 0 else ''
        mat_qc_path = mat_raw
        while mat_qc_path.lower().startswith('materials/'):
            mat_qc_path = mat_qc_path[10:]
            
        basetexture_path = f"{mat_qc_path}/{mat_clean}" if mat_qc_path else mat_clean
        surface_prop = model.surface if hasattr(model, 'surface') else 'default'
        basetexture_display = "(DO NOT CHANGE THIS - APPLIES IT GLOBALLY)" if self.is_global else basetexture_path
        
        vmt_lines = ['"VertexLitGeneric"', '{']
        if self.is_global:
            vmt_lines.append('    // (DO NOT CHANGE THIS - THE $basetexture APPLIES GLOBALLY, WILL BE REPLACED PER-MATERIAL ON EXPORT)')
        
        vmt_lines.append(f'    "$basetexture" "{basetexture_display}"')
        vmt_lines.append(f'    "$surfaceprop" "{surface_prop}"')
        vmt_lines.append('    "$model" 1')
        vmt_lines.append('}')
        
        existing_text.write("\n".join(vmt_lines) + "\n")
        self.report({'INFO'}, f"Reset VMT to clean defaults for {mat_clean}!")
        return {'FINISHED'}