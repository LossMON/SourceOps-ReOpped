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
        
        # QC Engine Path (Strips 'materials/')
        mat_qc_path = mat_raw
        while mat_qc_path.lower().startswith('materials/'):
            mat_qc_path = mat_qc_path[10:]
            
        basetexture_path = f"{mat_qc_path}/{mat_clean}" if mat_qc_path else mat_clean
        surface_prop = model.surface if hasattr(model, 'surface') else 'default'
        
        create_material_folder = getattr(sourceops, 'auto_create_material_folder', True)
        use_addon_folder = getattr(sourceops, 'auto_use_addon_folder', True)
        
        if game and getattr(game, 'models', ''):
            models_path = Path(game.models)
            
            # Base output path to prevent duplicate directories
            if models_path.name.lower() == 'models':
                out_root = models_path.parent
            else:
                out_root = models_path
                
            # Smart Pathing Output resolution
            if create_material_folder:
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
        generate_normal = getattr(config, "vtf_normal_map", False)
        vmt_trans = getattr(config, "vmt_translucent", False)
        vmt_alpha = getattr(config, "vmt_alphatest", False)
        
        if self.is_global:
            basetexture_display = "(DO NOT CHANGE THIS - APPLIES IT GLOBALLY)"
        else:
            basetexture_display = basetexture_path
        
        current_state = {
            "basetexture": basetexture_path,
            "bumpmap": "1" if generate_normal else "0",
            "surfaceprop": surface_prop,
            "translucent": "1" if vmt_trans else "0",
            "alphatest": "1" if vmt_alpha else "0",
            "nocull": "1" if getattr(config, "vmt_nocull", False) else "0",
            "envmap": "1" if getattr(config, "vmt_envmap", False) else "0",
            "is_global": "1" if self.is_global else "0"
        }

        do_not_sort = getattr(config, "do_not_sort_vmts", False) or getattr(model, "do_not_sort_vmts", False)

        # -------------------------------------------------------------
        # IF "DO NOT SORT" IS ENABLED: SMART PARSING
        # -------------------------------------------------------------
        if do_not_sort:
            raw_lines = []
            if existing_text and len(existing_text.lines) > 0:
                raw_lines = [line.body for line in existing_text.lines]
            elif vmt_path and vmt_path.is_file():
                try:
                    with open(vmt_path, 'r') as f:
                        lines = f.read().splitlines()
                    
                    is_disk_global = False
                    for line in reversed(lines):
                        if line.strip().startswith("// [SourceOps_State]"):
                            state_str_old = line.split("// [SourceOps_State]")[1].strip()
                            for pair in state_str_old.split("|"):
                                if ":" in pair and pair.split(":")[0] == "is_global":
                                    is_disk_global = (pair.split(":")[1] == "1")
                            break
                            
                    if not self.is_global and is_disk_global:
                        lines = []
                        
                    raw_lines = [l for l in lines if not l.strip().startswith("// [SourceOps_State]")]
                    raw_lines = [l for l in raw_lines if "DO NOT CHANGE THIS - THE $basetexture APPLIES GLOBALLY" not in l]
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
            
            # 1. Strip OFF properties from the text to keep it perfectly synced
            cleaned_lines = []
            for l in raw_lines:
                lower_l = l.strip().lower()
                if current_state["translucent"] == "0" and lower_l.startswith('"$translucent"'): continue
                if current_state["alphatest"] == "0" and lower_l.startswith('"$alphatest"'): continue
                if current_state["nocull"] == "0" and lower_l.startswith('"$nocull"'): continue
                if current_state["bumpmap"] == "0" and lower_l.startswith('"$bumpmap"'): continue
                if current_state["envmap"] == "0" and lower_l.startswith('"$envmap"'): continue
                if current_state["envmap"] == "0" and lower_l.startswith('"$envmaptint"'): continue
                if current_state["envmap"] == "0" and lower_l.startswith('"$reflectivity"'): continue
                if current_state["envmap"] == "0" and lower_l.startswith('"$envmapblur"'): continue
                if current_state["envmap"] == "0" and lower_l.startswith('"$normalmapalphaenvmapmask"'): continue
                cleaned_lines.append(l)

            # 2. Inject ON properties strictly under $surfaceprop
            final_lines = []
            injected = False
            
            def inject_properties(target_list):
                if current_state["translucent"] == "1" and not any('"$translucent"' in xl.lower() for xl in cleaned_lines):
                    target_list.append('    "$translucent" 1')
                if current_state["alphatest"] == "1" and not any('"$alphatest"' in xl.lower() for xl in cleaned_lines):
                    target_list.append('    "$alphatest" 1')
                if current_state["nocull"] == "1" and not any('"$nocull"' in xl.lower() for xl in cleaned_lines):
                    target_list.append('    "$nocull" 1')
                if current_state["bumpmap"] == "1" and not any('"$bumpmap"' in xl.lower() for xl in cleaned_lines):
                    bump_val = "(DO NOT CHANGE THIS - APPLIES IT GLOBALLY)_normalmap" if self.is_global else f"{basetexture_path}_normalmap"
                    target_list.append(f'    "$bumpmap" "{bump_val}"')
                if current_state["envmap"] == "1" and not any('"$envmap"' in xl.lower() for xl in cleaned_lines):
                    target_list.append('    "$envmap" "env_cubemap"')
                    target_list.append('    "$envmaptint" "[.3 .3 .3]"')
                    target_list.append('    "$reflectivity" "[1 1 1]"')
                    target_list.append('    "$envmapblur" "1"')
                    if current_state["bumpmap"] == "1" and not any('"$normalmapalphaenvmapmask"' in xl.lower() for xl in cleaned_lines):
                        target_list.append('    "$normalmapalphaenvmapmask" 1')
                        
            for l in cleaned_lines:
                if l.strip() == "}" and not injected:
                    inject_properties(final_lines)
                    injected = True
                    
                final_lines.append(l)
                
                # The exact spot to inject!
                if not injected and "$surfaceprop" in l.lower():
                    inject_properties(final_lines)
                    injected = True
                    
            if not injected:
                inject_properties(final_lines)
                
            if not existing_text:
                existing_text = bpy.data.texts.new(text_name)
            
            existing_text.clear()
            
            if self.is_global and not any("DO NOT CHANGE THIS - THE $basetexture APPLIES GLOBALLY" in l for l in final_lines):
                # Ensure the global comment stays attached at the top of the file
                final_lines.insert(2, '    // (DO NOT CHANGE THIS - THE $basetexture APPLIES GLOBALLY, WILL BE REPLACED PER-MATERIAL ON EXPORT)')
                
            existing_text.write("\n".join(final_lines) + "\n")
            state_str = "|".join([f"{k}:{v}" for k, v in current_state.items()])
            existing_text["sourceops_state"] = state_str
            
            self._open_text_editor(context, existing_text, text_name)
            return {'FINISHED'}

        # -------------------------------------------------------------
        # --- NORMAL PARSING LOGIC (DO NOT SORT IS FALSE) ---
        # -------------------------------------------------------------
        lines_to_parse = []
        previous_state = {}
        
        if existing_text and len(existing_text.lines) > 0:
            lines_to_parse = [line.body for line in existing_text.lines]
            state_str = existing_text.get("sourceops_state", "")
            for pair in state_str.split("|"):
                if ":" in pair:
                    k, v = pair.split(":", 1)
                    previous_state[k] = v
        elif vmt_path and vmt_path.is_file():
            try:
                with open(vmt_path, 'r') as f:
                    lines_to_parse = f.read().splitlines()
            except:
                pass
                
        for line in reversed(lines_to_parse):
            if line.strip().startswith("// [SourceOps_State]"):
                state_str_old = line.split("// [SourceOps_State]")[1].strip()
                for pair in state_str_old.split("|"):
                    if ":" in pair:
                        k, v = pair.split(":", 1)
                        previous_state[k] = v
                break

        # SHIELD SPECIFIC MATERIALS FROM INHERITING GLOBAL VMT EDITS FOUND IN THE DISK FILE
        if not self.is_global and previous_state.get("is_global") == "1":
            lines_to_parse = []
            previous_state = {}
                
        lines_to_parse = [l for l in lines_to_parse if not l.strip().startswith("// [SourceOps_State]")]
        
        controlled_keys = {
            "$basetexture", "$bumpmap", "$surfaceprop", "$model",
            "$translucent", "$alphatest", "$nocull", "$envmap",
            "$normalmapalphaenvmapmask", "$envmaptint", "$reflectivity", "$envmapblur"
        }
        
        user_overrides = {}
        custom_lines = []
        
        if lines_to_parse:
            for raw_line in lines_to_parse:
                stripped = raw_line.strip()
                if not stripped: continue
                
                # CLEAN IT OUT completely if a global template somehow made it in here
                if "DO NOT CHANGE THIS - THE $basetexture APPLIES GLOBALLY" in stripped: continue
                
                lower_line = stripped.lower().replace('"', '')
                if lower_line in ["vertexlitgeneric", "unlitgeneric", "lightmappedgeneric"]: continue
                if lower_line in ["vertexlitgeneric {", "unlitgeneric {", "lightmappedgeneric {"]: continue
                if stripped == "{" or stripped == "}": continue
                    
                is_controlled = False
                for c_key in controlled_keys:
                    if stripped.lower().startswith(c_key) or stripped.lower().startswith(f'"{c_key}"'):
                        user_overrides[c_key] = raw_line.rstrip('\n')
                        is_controlled = True
                        break
                        
                if not is_controlled:
                    custom_lines.append(raw_line.rstrip('\n'))

        vmt_lines = [f'"{shader}"', '{']
        
        if self.is_global:
            vmt_lines.append('    // (DO NOT CHANGE THIS - THE $basetexture APPLIES GLOBALLY, WILL BE REPLACED PER-MATERIAL ON EXPORT)')
            
        is_first_gen = not previous_state
        
        def process_key(key, ui_value, default_str):
            prop_name = key[1:] # e.g. "$basetexture" -> "basetexture"
            ui_changed = is_first_gen or (current_state.get(prop_name) != previous_state.get(prop_name))
            
            # Absolute foolproof safety net: force it to append if missing from memory entirely
            if ui_changed or key not in user_overrides:
                if ui_value:
                    vmt_lines.append(default_str)
            else:
                vmt_lines.append(user_overrides[key])

        process_key("$basetexture", True, f'    "$basetexture" "{basetexture_display}"')
        process_key("$surfaceprop", True, f'    "$surfaceprop" "{surface_prop}"')
        process_key("$model", True, '    "$model" 1')
        
        bump_val = "(DO NOT CHANGE THIS - APPLIES IT GLOBALLY)_normalmap" if self.is_global else f"{basetexture_path}_normalmap"
        process_key("$bumpmap", current_state["bumpmap"] == "1", f'    "$bumpmap" "{bump_val}"')
        
        process_key("$translucent", current_state["translucent"] == "1", '    "$translucent" 1')
        process_key("$alphatest", current_state["alphatest"] == "1", '    "$alphatest" 1')
        process_key("$nocull", current_state["nocull"] == "1", '    "$nocull" 1')
        
        ui_changed_envmap = is_first_gen or (current_state.get("envmap") != previous_state.get("envmap"))
        if ui_changed_envmap or "$envmap" not in user_overrides:
            if current_state["envmap"] == "1":
                vmt_lines.append('    "$envmap" "env_cubemap"')
                if current_state["bumpmap"] == "1":
                    vmt_lines.append('    "$normalmapalphaenvmapmask" 1')
                vmt_lines.append('    "$envmaptint" "[.3 .3 .3]"')
                vmt_lines.append('    "$reflectivity" "[1 1 1]"')
                vmt_lines.append('    "$envmapblur" "1"')
        else:
            for k in ["$envmap", "$normalmapalphaenvmapmask", "$envmaptint", "$reflectivity", "$envmapblur"]:
                if k in user_overrides:
                    vmt_lines.append(user_overrides[k])

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
        state_str = "|".join([f"{k}:{v}" for k, v in current_state.items()])
        existing_text["sourceops_state"] = state_str
        
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
    bl_description = 'Resets the VMT UI checkboxes and wipes the custom text block entirely.'

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
            
        # RESET UI CHECKBOXES
        config.vmt_shader = 'VertexLitGeneric'
        config.vmt_translucent = False
        config.vmt_alphatest = False
        config.vmt_nocull = False
        config.vmt_envmap = False
        config.vtf_normal_map = False
        
        text_name = f"VMT_{mat_clean}.vmt"
        existing_text = bpy.data.texts.get(text_name)
        
        if existing_text:
            existing_text.clear()
            mat_raw = model.material_folder_items[0].name.replace('\\', '/').strip('/') if len(model.material_folder_items) > 0 else ''
            mat_qc_path = mat_raw
            
            while mat_qc_path.lower().startswith('materials/'):
                mat_qc_path = mat_qc_path[10:]
                
            basetexture_path = f"{mat_qc_path}/{mat_clean}" if mat_qc_path else mat_clean
            
            if self.is_global:
                basetexture_display = "(DO NOT CHANGE THIS - APPLIES IT GLOBALLY)"
            else:
                basetexture_display = basetexture_path

            current_state = {
                "basetexture": basetexture_path, "bumpmap": "0",
                "surfaceprop": model.surface if hasattr(model, 'surface') else 'default',
                "translucent": "0", "alphatest": "0", "nocull": "0", "envmap": "0",
                "is_global": "1" if self.is_global else "0"
            }
            state_str = "|".join([f"{k}:{v}" for k, v in current_state.items()])
            sp = model.surface if hasattr(model, 'surface') else 'default'
            
            vmt_lines = [
                '"VertexLitGeneric"', '{'
            ]
            if self.is_global:
                vmt_lines.append('    // (DO NOT CHANGE THIS - THE $basetexture APPLIES GLOBALLY, WILL BE REPLACED PER-MATERIAL ON EXPORT)')
                
            vmt_lines.extend([
                f'    "$basetexture" "{basetexture_display}"',
                f'    "$surfaceprop" "{sp}"',
                '    "$model" 1', '}'
            ])
            existing_text.write("\n".join(vmt_lines) + "\n")
            existing_text["sourceops_state"] = state_str

        self.report({'INFO'}, f"Reset VMT checkboxes and text editor for {mat_clean}!")
        return {'FINISHED'}