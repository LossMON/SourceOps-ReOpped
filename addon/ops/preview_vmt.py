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

    def execute(self, context):
        prefs = common.get_prefs(context)
        game = common.get_game(prefs)
        sourceops = common.get_globals(context)
        model = common.get_model(sourceops)
        
        if self.item_type == 'SKIN':
            skin_item = model.skin_items[model.skin_index]
            mat_clean = skin_item.name
            mat_config = next((m for m in model.material_items if m.name == mat_clean), None)
            config = mat_config if mat_config else model
        else:
            config = model.material_items[model.material_index]
            mat_clean = config.name
            
        mat_subfolder = model.material_folder_items[0].name.replace('\\', '/').strip('/') if len(model.material_folder_items) > 0 else ''
        basetexture_path = f"{mat_subfolder}/{mat_clean}" if mat_subfolder else mat_clean
        surface_prop = model.surface if hasattr(model, 'surface') else 'default'
        
        # Resolve target directory to read VMT from disk if missing
        addon_name = common.clean_filename(Path(model.name).stem)
        create_material_folder = getattr(sourceops, 'auto_create_material_folder', True)
        use_addon_folder = getattr(sourceops, 'auto_use_addon_folder', True)
        
        if game and getattr(game, 'models', ''):
            models_path = Path(game.models)
            if create_material_folder:
                if use_addon_folder:
                    target_dir = models_path.joinpath(addon_name, 'materials', mat_subfolder)
                else:
                    if models_path.name.lower() == 'models':
                        target_dir = models_path.parent.joinpath('materials', mat_subfolder)
                    else:
                        target_dir = models_path.joinpath('materials', mat_subfolder)
            else:
                if use_addon_folder:
                    target_dir = models_path.joinpath(addon_name, 'models', mat_subfolder)
                else:
                    target_dir = models_path.joinpath(mat_subfolder)
                    
            vmt_path = target_dir.joinpath(f"{mat_clean}.vmt")
        else:
            vmt_path = Path(f"{mat_clean}.vmt")
        
        text_name = f"VMT_{mat_clean}.vmt"
        existing_text = bpy.data.texts.get(text_name)
        
        shader = getattr(config, "vmt_shader", "VertexLitGeneric")
        generate_normal = getattr(config, "vtf_normal_map", False)
        vmt_trans = getattr(config, "vmt_translucent", False)
        vmt_alpha = getattr(config, "vmt_alphatest", False)
        
        current_state = {
            "basetexture": basetexture_path,
            "bumpmap": "1" if generate_normal else "0",
            "surfaceprop": surface_prop,
            "translucent": "1" if vmt_trans else "0",
            "alphatest": "1" if vmt_alpha else "0",
            "nocull": "1" if getattr(config, "vmt_nocull", False) else "0",
            "envmap": "1" if getattr(config, "vmt_envmap", False) else "0"
        }
        
        lines_to_parse = []
        previous_state = {}
        
        # Read from Text Editor OR Disk
        if existing_text and len(existing_text.lines) > 0:
            lines_to_parse = [line.body for line in existing_text.lines]
            state_str = existing_text.get("sourceops_state", "")
            for pair in state_str.split("|"):
                if ":" in pair:
                    k, v = pair.split(":", 1)
                    previous_state[k] = v
        elif vmt_path.is_file():
            try:
                with open(vmt_path, 'r') as f:
                    lines_to_parse = f.read().splitlines()
            except:
                pass
                
        # Extract the saved state comment from the disk file to preserve cross-session edits
        for line in reversed(lines_to_parse):
            if line.strip().startswith("// [SourceOps_State]"):
                state_str_old = line.split("// [SourceOps_State]")[1].strip()
                for pair in state_str_old.split("|"):
                    if ":" in pair:
                        k, v = pair.split(":", 1)
                        previous_state[k] = v
                break
                
        # Strip the state comments so they are hidden from the text editor completely
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
                
                # Use bulletproof string matching instead of checking { brackets which breaks parsing
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
        is_first_gen = not previous_state
        
        def process_key(key, ui_value, default_str):
            prop_name = key[1:] # e.g. "$basetexture" -> "basetexture"
            
            # Check if the UI actively changed since last save, or if it's the very first generation
            ui_changed = is_first_gen or (current_state.get(prop_name) != previous_state.get(prop_name))
            
            if ui_changed:
                if ui_value:
                    vmt_lines.append(default_str)
            else:
                # The UI didn't change! We trust the user's manual edits.
                # If it's in user_overrides, append it. If they deleted it, we append nothing!
                if key in user_overrides:
                    vmt_lines.append(user_overrides[key])

        # Core properties guaranteed to force if UI changed
        process_key("$basetexture", True, f'    "$basetexture" "{basetexture_path}"')
        process_key("$surfaceprop", True, f'    "$surfaceprop" "{surface_prop}"')
        process_key("$model", True, '    "$model" 1')
        
        # Toggle properties
        process_key("$bumpmap", current_state["bumpmap"] == "1", f'    "$bumpmap" "{basetexture_path}_normalmap"')
        process_key("$translucent", current_state["translucent"] == "1", '    "$translucent" 1')
        process_key("$alphatest", current_state["alphatest"] == "1", '    "$alphatest" 1')
        process_key("$nocull", current_state["nocull"] == "1", '    "$nocull" 1')
        
        # Environment Map Block
        ui_changed_envmap = is_first_gen or (current_state.get("envmap") != previous_state.get("envmap"))
        if ui_changed_envmap:
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
                vmt_lines.append(cl) # Keep exactly as user formatted
                    
        vmt_lines.append('}')
        
        # Create the UI version (NO COMMENT AT THE BOTTOM)
        vmt_content_ui = "\n".join(vmt_lines) + "\n"
        
        if not existing_text:
            existing_text = bpy.data.texts.new(text_name)
            
        # Update Text Editor (Clean, no comment)
        existing_text.clear()
        existing_text.write(vmt_content_ui)
        
        # Write state memory to custom invisible properties
        state_str = "|".join([f"{k}:{v}" for k, v in current_state.items()])
        existing_text["sourceops_state"] = state_str
        
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
        return {'FINISHED'}


class SOURCEOPS_OT_ResetVMT(bpy.types.Operator):
    bl_idname = 'sourceops.reset_vmt'
    bl_options = {'REGISTER', 'UNDO'}
    bl_label = 'Reset VMT'
    bl_description = 'Resets the VMT UI checkboxes and wipes the custom text block entirely.'

    item_type: bpy.props.StringProperty()

    def execute(self, context):
        sourceops = common.get_globals(context)
        model = common.get_model(sourceops)
        
        if self.item_type == 'SKIN':
            skin_item = model.skin_items[model.skin_index]
            mat_clean = skin_item.name
            mat_config = next((m for m in model.material_items if m.name == mat_clean), None)
            config = mat_config if mat_config else model
        else:
            config = model.material_items[model.material_index]
            mat_clean = config.name
            
        # 1. Reset UI Checkmarks
        config.vmt_shader = 'VertexLitGeneric'
        config.vmt_translucent = False
        config.vmt_alphatest = False
        config.vmt_nocull = False
        config.vmt_envmap = False
        config.vtf_normal_map = False
        
        text_name = f"VMT_{mat_clean}.vmt"
        existing_text = bpy.data.texts.get(text_name)
        
        # 2. Reset Text Editor in the background
        if existing_text:
            existing_text.clear()
                
            mat_subfolder = model.material_folder_items[0].name.replace('\\', '/').strip('/') if len(model.material_folder_items) > 0 else ''
            basetexture_path = f"{mat_subfolder}/{mat_clean}" if mat_subfolder else mat_clean
            
            current_state = {
                "basetexture": basetexture_path,
                "bumpmap": "0",
                "surfaceprop": model.surface if hasattr(model, 'surface') else 'default',
                "translucent": "0",
                "alphatest": "0",
                "nocull": "0",
                "envmap": "0"
            }
            state_str = "|".join([f"{k}:{v}" for k, v in current_state.items()])
            
            vmt_lines = [
                '"VertexLitGeneric"',
                '{',
                f'    "$basetexture" "{basetexture_path}"',
                f'    "$surfaceprop" "{model.surface if hasattr(model, "surface") else "default"}"',
                '    "$model" 1',
                '}'
            ]
            existing_text.write("\n".join(vmt_lines) + "\n")
            
            # Save empty state invisibly
            existing_text["sourceops_state"] = state_str

        self.report({'INFO'}, f"Reset VMT checkboxes and text editor for {mat_clean}!")
        return {'FINISHED'}