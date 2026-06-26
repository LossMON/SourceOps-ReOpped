import bpy
from .. utils import common

class SOURCEOPS_OT_PreviewVMT(bpy.types.Operator):
    bl_idname = 'sourceops.preview_vmt'
    bl_options = {'REGISTER', 'UNDO'}
    bl_label = 'Preview / Edit VMT'
    bl_description = 'Opens the VMT code in a Text Editor. The Text Editor has absolute priority unless you explicitly toggle UI checkboxes.'

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
            
        mat_subfolder = model.material_folder_items[0].name.replace('\\', '/').strip('/') if len(model.material_folder_items) > 0 else ''
        basetexture_path = f"{mat_subfolder}/{mat_clean}" if mat_subfolder else mat_clean
        
        text_name = f"VMT_{mat_clean}.vmt"
        existing_text = bpy.data.texts.get(text_name)
        
        shader = getattr(config, "vmt_shader", "VertexLitGeneric")
        generate_normal = getattr(config, "vtf_normal_map", False)
        vmt_trans = getattr(config, "vmt_translucent", False)
        vmt_alpha = getattr(config, "vmt_alphatest", False)
        
        current_state = {
            "bumpmap": generate_normal,
            "translucent": vmt_trans,
            "alphatest": vmt_alpha,
            "nocull": getattr(config, "vmt_nocull", False),
            "envmap": getattr(config, "vmt_envmap", False)
        }
        
        groups = {
            "basetexture": [("$basetexture", f'    "$basetexture" "{basetexture_path}"')],
            "bumpmap": [("$bumpmap", f'    "$bumpmap" "{basetexture_path}_normalmap"')],
            "surfaceprop": [("$surfaceprop", f'    "$surfaceprop" "{model.surface}"')],
            "model": [("$model", '    "$model" 1')],
            "translucent": [("$translucent", '    "$translucent" 1')],
            "alphatest": [("$alphatest", '    "$alphatest" 1')],
            "nocull": [("$nocull", '    "$nocull" 1')],
            "envmap": [
                ("$envmap", f'    "$envmap" "{basetexture_path}_normalmap"' if generate_normal else '    "$envmap" "env_cubemap"'),
                ("$normalmapalphaenvmapmask", '    "$normalmapalphaenvmapmask" 1'),
                ("$envmaptint", '    "$envmaptint" "[.3 .3 .3]"'),
                ("$reflectivity", '    "$reflectivity" "[1 1 1]"'),
                ("$envmapblur", '    "$envmapblur" "1"')
            ]
        }
        
        controlled_keys = [k for grp in groups.values() for k, d in grp]
        
        custom_lines = []
        user_overrides = {}
        
        # Gather what the user wrote in the Text Editor
        if existing_text and len(existing_text.lines) > 0:
            brace_level = 0
            first_brace_seen = False
            for line in existing_text.lines:
                raw_line = line.body
                stripped = raw_line.strip()
                
                if stripped.startswith("// [SourceOps_State]"):
                    continue
                    
                if not first_brace_seen:
                    clean_shader = stripped.replace('"', '').lower()
                    if clean_shader in ["vertexlitgeneric", "unlitgeneric", "lightmappedgeneric"]: 
                        continue
                    if clean_shader in ["vertexlitgeneric {", "unlitgeneric {", "lightmappedgeneric {", "vertexlitgeneric{", "unlitgeneric{", "lightmappedgeneric{"]:
                        first_brace_seen = True
                        continue
                    if stripped == "{":
                        first_brace_seen = True
                        continue
                else:
                    if stripped == "{":
                        brace_level += 1
                    elif stripped == "}":
                        if brace_level == 0:
                            continue
                        brace_level -= 1
                        
                is_controlled = False
                if stripped and stripped != "{" and stripped != "}" and brace_level == 0:
                    first_word = stripped.replace('"', '').split()[0].lower()
                    if first_word in controlled_keys:
                        user_overrides[first_word] = raw_line.rstrip('\n')
                        is_controlled = True
                        
                if not is_controlled:
                    custom_lines.append(raw_line.rstrip('\n'))
                    
            while custom_lines and not custom_lines[0].strip(): custom_lines.pop(0)
            while custom_lines and not custom_lines[-1].strip(): custom_lines.pop()

        # Track UI changes invisibly inside Blender's metadata (NO comments in the text)
        previous_state = {}
        if existing_text and "sourceops_state" in existing_text:
            state_str = existing_text["sourceops_state"]
            for pair in state_str.split(","):
                if ":" in pair:
                    k, v = pair.split(":")
                    previous_state[k] = (v == "1")

        vmt_lines = [f'"{shader}"', '{']
        
        for grp_name, grp_items in groups.items():
            is_toggled_group = grp_name in current_state
            changed = False
            turned_on = False
            
            if is_toggled_group:
                prev_val = previous_state.get(grp_name, None)
                curr_val = current_state[grp_name]
                if prev_val is not None and prev_val != curr_val:
                    changed = True
                    turned_on = curr_val
                    
            if changed:
                if turned_on:
                    for k, default_str in grp_items:
                        vmt_lines.append(default_str)
            else:
                for k, default_str in grp_items:
                    if k in user_overrides:
                        val = user_overrides[k]
                        if not val.startswith(' ') and not val.startswith('\t'):
                            vmt_lines.append(f'    {val}')
                        else:
                            vmt_lines.append(val)
                    else:
                        if not previous_state:
                            if (is_toggled_group and current_state[grp_name]) or (not is_toggled_group):
                                vmt_lines.append(default_str)

        if custom_lines:
            vmt_lines.append('')
            for cl in custom_lines:
                if cl.strip():
                    if not cl.startswith(' ') and not cl.startswith('\t'): 
                        vmt_lines.append(f'    {cl}')
                    else: 
                        vmt_lines.append(cl)
                else:
                    vmt_lines.append('')
                    
        vmt_lines.append('}')
        vmt_content = "\n".join(vmt_lines) + "\n"
        
        if not existing_text:
            existing_text = bpy.data.texts.new(text_name)
            
        existing_text.clear()
        existing_text.write(vmt_content)
        
        state_str = ",".join([f"{k}:{'1' if v else '0'}" for k, v in current_state.items()])
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
            if "sourceops_state" in existing_text:
                del existing_text["sourceops_state"]
                
            mat_subfolder = model.material_folder_items[0].name.replace('\\', '/').strip('/') if len(model.material_folder_items) > 0 else ''
            basetexture_path = f"{mat_subfolder}/{mat_clean}" if mat_subfolder else mat_clean
            
            vmt_lines = [
                '"VertexLitGeneric"',
                '{',
                f'    "$basetexture" "{basetexture_path}"',
                f'    "$surfaceprop" "{model.surface}"',
                '    "$model" 1',
                '}'
            ]
            existing_text.write("\n".join(vmt_lines) + "\n")
            
            current_state = {"bumpmap": False, "translucent": False, "alphatest": False, "nocull": False, "envmap": False}
            state_str = ",".join([f"{k}:{'1' if v else '0'}" for k, v in current_state.items()])
            existing_text["sourceops_state"] = state_str

        self.report({'INFO'}, f"Reset VMT checkboxes and text editor for {mat_clean}!")
        return {'FINISHED'}