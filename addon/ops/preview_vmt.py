import bpy
from .. utils import common

class SOURCEOPS_OT_PreviewVMT(bpy.types.Operator):
    bl_idname = 'sourceops.preview_vmt'
    bl_options = {'REGISTER', 'UNDO'}
    bl_label = 'Preview / Edit VMT'
    bl_description = 'Generates the VMT code and opens it in a Text Editor. Your manual edits and UI changes are intelligently combined!'

    item_type: bpy.props.StringProperty()

    def execute(self, context):
        sourceops = common.get_globals(context)
        model = common.get_model(sourceops)
        
        # It now natively defaults back to proper material properties
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
        
        # --- SMART MERGER: Extract User's Custom Lines & Edits ---
        custom_lines = []
        user_overrides = {}
        
        if existing_text:
            controlled_keys = ["$basetexture", "$bumpmap", "$surfaceprop", "$model", "$translucent", "$alphatest", "$nocull", "$envmap", "$normalmapalphaenvmapmask", "$envmaptint", "$reflectivity", "$envmapblur"]
            
            for line in existing_text.lines:
                raw_line = line.body
                stripped = raw_line.strip()
                
                if stripped == "{" or stripped == "}": 
                    continue
                    
                clean_shader = stripped.replace('"', '').lower()
                if clean_shader in ["vertexlitgeneric", "unlitgeneric", "lightmappedgeneric"]: 
                    continue
                        
                is_controlled = False
                if stripped:
                    # Get the first word (the VMT parameter key) and lower it
                    first_word = stripped.replace('"', '').split()[0].lower()
                    if first_word in controlled_keys:
                        # User edited a UI-controlled line. Save their exact text!
                        user_overrides[first_word] = raw_line.rstrip('\n')
                        is_controlled = True
                        
                if not is_controlled:
                    custom_lines.append(raw_line.rstrip('\n'))
                    
            while custom_lines and not custom_lines[0].strip(): custom_lines.pop(0)
            while custom_lines and not custom_lines[-1].strip(): custom_lines.pop()

        # Helper function to inject user edits or fallback to default
        def get_line(key, default_str):
            if key in user_overrides:
                val = user_overrides[key]
                # Ensure the user's line has proper formatting if they forgot to tab it
                if not val.startswith(' ') and not val.startswith('\t'):
                    return f'    {val}'
                return val
            return default_str

        # --- GENERATE FRESH VMT FROM UI ---
        shader = getattr(config, "vmt_shader", "VertexLitGeneric")
        generate_normal = getattr(config, "vtf_normal_map", False)

        vmt_lines = [
            f'"{shader}"',
            '{',
            get_line("$basetexture", f'    "$basetexture" "{basetexture_path}"'),
        ]
        
        if generate_normal:
            vmt_lines.append(get_line("$bumpmap", f'    "$bumpmap" "{basetexture_path}_normalmap"'))
        
        vmt_lines.append(get_line("$surfaceprop", f'    "$surfaceprop" "{model.surface}"'))
        vmt_lines.append(get_line("$model", '    "$model" 1'))
        
        vmt_trans = getattr(config, "vmt_translucent", False)
        vmt_alpha = getattr(config, "vmt_alphatest", False)
        
        if vmt_trans: vmt_lines.append(get_line("$translucent", '    "$translucent" 1'))
        if vmt_alpha: vmt_lines.append(get_line("$alphatest", '    "$alphatest" 1'))
            
        if getattr(config, "vmt_nocull", False):
            vmt_lines.append(get_line("$nocull", '    "$nocull" 1'))
        
        # If envmap is checked, it tries to use your custom values, or defaults if none exist
        if getattr(config, "vmt_envmap", False):
            if generate_normal:
                vmt_lines.append(get_line("$envmap", f'    "$envmap" "{basetexture_path}_normalmap"'))
            else:
                vmt_lines.append(get_line("$envmap", '    "$envmap" "env_cubemap"'))
            vmt_lines.append(get_line("$normalmapalphaenvmapmask", '    "$normalmapalphaenvmapmask" 1'))
            vmt_lines.append(get_line("$envmaptint", '    "$envmaptint" "[.3 .3 .3]"'))
            vmt_lines.append(get_line("$reflectivity", '    "$reflectivity" "[1 1 1]"'))
            vmt_lines.append(get_line("$envmapblur", '    "$envmapblur" "1"'))
            
        # Inject the preserved custom lines seamlessly
        if custom_lines:
            vmt_lines.append('')
            for cl in custom_lines:
                if cl.strip():
                    if not cl.startswith(' ') and not cl.startswith('\t'): vmt_lines.append(f'    {cl}')
                    else: vmt_lines.append(cl)
                else:
                    vmt_lines.append('')
                
        vmt_lines.append('}\n')
        vmt_content = "\n".join(vmt_lines)
        
        # --- WRITE AND OPEN IN TEXT EDITOR ---
        if not existing_text:
            existing_text = bpy.data.texts.new(text_name)
            
        existing_text.clear()
        existing_text.write(vmt_content)
        
        # Force cursor back to the absolute top
        existing_text.cursor_set(0, character=0)
        
        bpy.ops.wm.window_new()
        new_window = context.window_manager.windows[-1]
        area = new_window.screen.areas[0]
        area.type = 'TEXT_EDITOR'
        area.spaces.active.text = existing_text
        
        # Double safety to force view scrolling to the top
        try:
            area.spaces.active.top = 0
        except:
            pass
        
        self.report({'INFO'}, f"Opened {text_name} in Text Editor!")
        return {'FINISHED'}