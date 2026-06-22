import bpy
from .. utils import common
from .. import icons


class SOURCEOPS_PT_MainPanel(bpy.types.Panel):
    bl_idname = 'SOURCEOPS_PT_MainPanel'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'SourceOps'
    bl_label = f'SourceOps ReOpped    -    {common.get_version()}'

    def draw(self, context):
        layout = self.layout

        prefs = common.get_prefs(context)
        game = common.get_game(prefs)
        sourceops = common.get_globals(context)
        model = common.get_model(sourceops)
        material_folder = common.get_material_folder(model)
        skin = common.get_skin(model)
        sequence = common.get_sequence(model)
        event = common.get_event(sequence)
        attachment = common.get_attachment(model)
        particle = common.get_particle(model)
        map_props = common.get_map(sourceops)

        if sourceops:
            box = layout.box()
            row = box.row()
            row.scale_x = row.scale_y = 1.5
            row.label(text='Panel')
            row = row.row(align=True)
            row.alignment = 'RIGHT'
            row.prop(sourceops, 'panel', expand=True, icon_only=True)

        if prefs and sourceops.panel == 'GAMES':
            box = layout.box()
            row = box.row()
            row.alignment = 'CENTER'
            row.label(text='Games')

            row = box.row()
            row.template_list('SOURCEOPS_UL_GameList', '', prefs, 'game_items', prefs, 'game_index', rows=5)
            col = row.column(align=True)
            self.draw_list_buttons(col, 'GAMES')

            if game:
                col = common.split_column(box)
                col.prop(game, 'name')
                col.prop(game, 'game')
                col.prop(game, 'bin')
                col.prop(game, 'modelsrc')
                col.prop(game, 'models')
                col.prop(game, 'mapsrc')
                col.prop(game, 'hlmvplusplus')
                col.prop(game, 'mesh_type')

        elif sourceops and sourceops.panel == 'MODELS':
            box = layout.box()
            row = box.row()
            row.alignment = 'CENTER'
            row.label(text='Models')

            row = box.row()
            row.template_list('SOURCEOPS_UL_ModelList', '', sourceops, 'model_items', sourceops, 'model_index', rows=5)
            col = row.column(align=True)
            self.draw_list_buttons(col, 'MODELS')
            
            row = box.row(align=True)
            row.operator('sourceops.add_selected_collections', text='Add Collections', icon='OUTLINER_COLLECTION')
            row.operator('sourceops.add_selected_collections_skins', text='+ Skins', icon='MATERIAL')
            
            box.separator()
            row = box.row(align=True)
            row.prop(sourceops, 'default_surface', text='')
            row.operator('sourceops.apply_surface_prop', text='Apply to Checked', icon='CHECKMARK')

            if model:
                col = common.split_column(box)
                col.prop(model, 'name')
                col.prop(model, 'armature')
                col.prop(model, 'reference')
                col.prop(model, 'collision')
                
                col.prop(model, 'lod_1_collection')
                if model.lod_1_collection:
                    col.prop(model, 'lod_1_distance')
                    col.separator(factor=0.5)

                col.prop(model, 'lod_2_collection')
                if model.lod_2_collection:
                    col.prop(model, 'lod_2_distance')
                    col.separator(factor=0.5)

                col.prop(model, 'lod_3_collection')
                if model.lod_3_collection:
                    col.prop(model, 'lod_3_distance')
                    col.separator(factor=0.5)

                col.prop(model, 'lod_4_collection')
                if model.lod_4_collection:
                    col.prop(model, 'lod_4_distance')
                    col.separator(factor=0.5)

                col.prop(model, 'lod_5_collection')
                if model.lod_5_collection:
                    col.prop(model, 'lod_5_distance')
                    col.separator(factor=0.5)

                col.prop(model, 'lod_6_collection')
                if model.lod_6_collection:
                    col.prop(model, 'lod_6_distance')
                    col.separator(factor=0.5)

                col.prop(model, 'bodygroups')
                col.prop(model, 'stacking')
                
                # --- MODEL GLOBAL TEXTURE SETTINGS ---
                box.separator()
                box.label(text='Model Default Textures:', icon='TEXTURE')
                col = common.split_column(box)
                col.prop(model, 'vtf_format')
                col.prop(model, 'vtf_alphaformat')
                
                box.separator()
                box.label(text='Mipmaps:', icon='IMAGE_ZDEPTH')
                col = common.split_column(box)
                col.prop(model, 'vtf_nomipmaps')
                if not model.vtf_nomipmaps:
                    col.prop(model, 'vtf_mfilter')
                    col.prop(model, 'vtf_msharpen')
                    
                box.separator()
                box.label(text='Resize (-resize):', icon='FULLSCREEN_ENTER')
                col = common.split_column(box)
                col.prop(model, 'vtf_resize')
                if model.vtf_resize:
                    col.prop(model, 'vtf_rmethod')
                    col.prop(model, 'vtf_rfilter')
                    col.prop(model, 'vtf_rsharpen')
                    col.prop(model, 'vtf_rwidth')
                    col.prop(model, 'vtf_rheight')
                    col.prop(model, 'vtf_rclampwidth')
                    col.prop(model, 'vtf_rclampheight')

                box.separator()
                box.label(text='Normal Maps (-normal):', icon='MATFLUID')
                col = common.split_column(box)
                col.prop(model, 'vtf_normal_map')
                if model.vtf_normal_map:
                    col.prop(model, 'vtf_nkernel')
                    col.prop(model, 'vtf_nheight')
                    col.prop(model, 'vtf_nalpha')
                    col.prop(model, 'vtf_nscale')
                    col.prop(model, 'vtf_nwrap')

                box.separator()
                box.label(text='Extras:', icon='MODIFIER')
                col = common.split_column(box)
                col.prop(model, 'vtf_gamma')
                if model.vtf_gamma:
                    col.prop(model, 'vtf_gcorrection')
                col.prop(model, 'vtf_bumpscale')
                col.prop(model, 'vtf_nothumbnail')
                col.prop(model, 'vtf_noreflectivity')

                box.separator()
                flags_box = box.box()
                flags_box.label(text="Flags (-flag)", icon='BOOKMARKS')
                flags_row = flags_box.row()
                f_col1 = flags_row.column()
                f_col2 = flags_row.column()
                
                flags =["POINTSAMPLE", "TRILINEAR", "CLAMPS", "CLAMPT", "ANISOTROPIC", "HINT_DXT5", "NORMAL", "NOMIP", "NOLOD", "MINMIP", "PROCEDURAL", "RENDERTARGET", "DEPTHRENDERTARGET", "NODEBUGOVERRIDE", "SINGLECOPY", "NODEPTHBUFFER", "CLAMPU", "VERTEXTEXTURE", "SSBUMP", "BORDER"]
                
                for i, flag in enumerate(flags):
                    if i < 10: f_col1.prop(model, f"vtf_flag_{flag}")
                    else: f_col2.prop(model, f"vtf_flag_{flag}")
                    
                box.separator()
                box.label(text='VMT Material Setup:', icon='SHADING_RENDERED')
                col = common.split_column(box)
                col.prop(model, 'vmt_shader')
                col.prop(model, 'vmt_translucent')
                col.prop(model, 'vmt_alphatest')
                col.prop(model, 'vmt_nocull')
                col.prop(model, 'vmt_envmap')

        elif model and sourceops.panel == 'MODEL_OPTIONS':
            box = layout.box()
            row = box.row()
            row.alignment = 'CENTER'
            row.label(text='Model Options')

            col = common.split_column(box)
            col.prop(model, 'surface')
            col.prop(model, 'glass')
            col.prop(model, 'static')
            col.prop(model, 'rename_material')
            row = col.row()
            row.enabled = model.static
            row.prop(model, 'static_prop_combine')
            col.prop(model, 'joints')
            col.prop(model, 'mass')

            box = layout.box()
            row = box.row()
            row.alignment = 'CENTER'
            row.label(text='Transform Options')

            col = common.split_column(box)
            col.prop(model, 'prepend_armature')
            col.prop(model, 'ignore_transforms')

            sub = col.column()
            sub.enabled = not (model.static and model.static_prop_combine)
            sub.prop(model, 'origin_source')

            if model.origin_source == 'OBJECT':
                sub.prop(model, 'origin_object')

            else:
                align = sub.column(align=True)
                align.prop(model, 'origin_x', text='Origin X')
                align.prop(model, 'origin_y', text='Y')
                align.prop(model, 'origin_z', text='Z')

                sub.prop(model, 'rotation')

            col.prop(model, 'scale')

        elif model and sourceops.panel == 'TEXTURES':
            box = layout.box()
            row = box.row()
            row.alignment = 'CENTER'
            row.label(text='Model Folders')

            row = box.row()
            row.template_list('SOURCEOPS_UL_ModelFolderList', '', model, 'model_folder_items', model, 'model_folder_index', rows=3)
            col = row.column(align=True)
            self.draw_list_buttons(col, 'MODEL_FOLDERS')

            model_folder = model.model_folder_items[model.model_folder_index] if len(model.model_folder_items) > 0 else None
            if model_folder:
                col = common.split_column(box)
                col.prop(model_folder, 'name')

            box = layout.box()
            row = box.row()
            row.alignment = 'CENTER'
            row.label(text='Material Folders')

            row = box.row()
            row.template_list('SOURCEOPS_UL_MaterialFolderList', '', model, 'material_folder_items', model, 'material_folder_index', rows=3)
            col = row.column(align=True)
            self.draw_list_buttons(col, 'MATERIAL_FOLDERS')

            if material_folder:
                col = common.split_column(box)
                col.prop(material_folder, 'name')

            # --- MATERIAL PROPERTIES LIST ---
            box = layout.box()
            row = box.row()
            row.alignment = 'CENTER'
            row.label(text='Material Properties')

            row = box.row()
            row.template_list('SOURCEOPS_UL_MaterialList', '', model, 'material_items', model, 'material_index', rows=4)
            col = row.column(align=True)
            self.draw_list_buttons(col, 'MATERIALS')
            
            material_item = model.material_items[model.material_index] if len(model.material_items) > 0 else None
            if material_item:
                self.draw_texture_settings(box, material_item, 'MATERIAL')

            # --- SKINS (OVERRIDES) LIST ---
            box = layout.box()
            row = box.row()
            row.alignment = 'CENTER'
            row.label(text='Skins (Overrides)')

            row = box.row()
            row.template_list('SOURCEOPS_UL_SkinList', '', model, 'skin_items', model, 'skin_index', rows=4)
            col = row.column(align=True)
            self.draw_list_buttons(col, 'SKINS')

            if skin:
                col = common.split_column(box)
                col.prop(skin, 'name')
                col.prop(skin, 'linked_materials', text="Linked Mats (Space Separated)")

        elif model and sourceops.panel == 'SEQUENCES':
            box = layout.box()
            row = box.row()
            row.alignment = 'CENTER'
            row.label(text='Sequences')

            row = box.row()
            row.template_list('SOURCEOPS_UL_SequenceList', '', model, 'sequence_items', model, 'sequence_index', rows=5)
            col = row.column(align=True)
            self.draw_list_buttons(col, 'SEQUENCES')

            if sequence:
                col = common.split_column(box)
                col.prop(sequence, 'name')
                col.prop(sequence, 'action')

                col.prop(sequence, 'use_framerate')
                sub = col.column()
                sub.enabled = sequence.use_framerate
                sub.prop(sequence, 'framerate')

                col.prop(sequence, 'use_range')
                sub = col.column()
                sub.enabled = sequence.use_range
                sub.prop(sequence, 'start')
                sub.prop(sequence, 'end')

                col.prop(sequence, 'activity')
                col.prop(sequence, 'weight')
                col.prop(sequence, 'snap')
                col.prop(sequence, 'loop')

        elif sequence and sourceops.panel == 'EVENTS':
            box = layout.box()
            row = box.row()
            row.alignment = 'CENTER'
            row.label(text='Events')

            row = box.row()
            row.template_list('SOURCEOPS_UL_EventList', '', sequence, 'event_items', sequence, 'event_index', rows=5)
            col = row.column(align=True)
            self.draw_list_buttons(col, 'EVENTS')

            if event:
                col = common.split_column(box)
                col.prop(event, 'name')
                col.prop(event, 'event')
                col.prop(event, 'frame')
                col.prop(event, 'value')

        elif model and sourceops.panel == 'PARTICLES':
            box = layout.box()
            row = box.row()
            row.alignment = 'CENTER'
            row.label(text='Particles')
            
            row = box.row()
            row.template_list('SOURCEOPS_UL_ParticleList', '', model, 'particle_items', model, 'particle_index', rows=5)
            col = row.column(align=True)
            self.draw_list_buttons(col, 'PARTICLES')

            if particle:
                col = common.split_column(box)
                col.prop(particle, 'name')
                col.prop(particle, 'attachment_type')
                col.prop(particle, 'attachment_point')

        elif model and sourceops.panel == 'ATTACHMENTS':
            box = layout.box()
            row = box.row()
            row.alignment = 'CENTER'
            row.label(text='Attachments')

            row = box.row()
            row.template_list('SOURCEOPS_UL_AttachmentList', '', model, 'attachment_items', model, 'attachment_index', rows=5)
            col = row.column(align=True)
            self.draw_list_buttons(col, 'ATTACHMENTS')

            if attachment:
                col = common.split_column(box)
                col.prop(attachment, 'name')

                armature = model.armature
                if armature and armature.data:
                    col.prop_search(attachment, 'bone', armature.data, 'bones')

                col.prop(attachment, 'offset')
                col.prop(attachment, 'rotation')
                col.prop(attachment, 'absolute')
                col.prop(attachment, 'rigid')

        if sourceops.panel in {'GAMES', 'MODELS', 'MODEL_OPTIONS', 'TEXTURES', 'SEQUENCES', 'EVENTS', 'ATTACHMENTS', 'PARTICLES'}:
            box = layout.box()
            row = box.row()
            row.scale_x = row.scale_y = 1.5
            row.label(text='Export')
            row = row.row(align=True)
            row.alignment = 'RIGHT'

            row.operator('sourceops.open_folder', text='', icon='FILEBROWSER')
            row.operator('sourceops.spawn_info_player', text='', icon_value=icons.id('info_playerstart'))
            row.operator('sourceops.export_meshes', text='', icon_value=icons.id('smd'))
            row.operator('sourceops.generate_qc', text='', icon_value=icons.id('qc'))
            row.operator('sourceops.compile_qc', text='', icon_value=icons.id('mdl'))
            row.operator('sourceops.view_model', text='', icon_value=icons.id('hlmv'))
            row.operator('sourceops.view_model_plusplus', text='', icon_value=icons.id('hlmvplusplus'))
            
            op = row.operator('sourceops.export_auto', text='', icon='AUTO')

        if sourceops and sourceops.panel == 'MAPS':
            box = layout.box()
            row = box.row()
            row.alignment = 'CENTER'
            row.label(text='Maps')

            row = box.row()
            row.template_list('SOURCEOPS_UL_MapList', '', sourceops, 'map_items', sourceops, 'map_index', rows=5)
            col = row.column(align=True)
            self.draw_list_buttons(col, 'MAPS')

            if map_props:
                col = common.split_column(box)
                col.prop(map_props, 'name')
                col.prop(map_props, 'brush_collection')
                col.prop(map_props, 'disp_collection')
                col.prop(map_props, 'geometry_scale')
                col.prop(map_props, 'texture_scale')
                col.prop(map_props, 'lightmap_scale')
                col.prop(map_props, 'allow_skewed_textures')
                col.prop(map_props, 'align_to_grid')

            box = layout.box()
            row = box.row()
            row.scale_x = row.scale_y = 1.5
            row.label(text='Export')
            row = row.row(align=True)
            row.alignment = 'RIGHT'

            row.operator('sourceops.export_vmf', text='', icon_value=icons.id('vmf'))

        if sourceops and sourceops.panel == 'SIMULATION':
            box = layout.box()
            row = box.row()
            row.alignment = 'CENTER'
            row.label(text='Simulation')

            col = common.split_column(box)
            col.prop(sourceops, 'simulation_input')
            col.prop(sourceops, 'simulation_output')
            box.operator('sourceops.rig_simulation', text='Rig Simulation')

        if sourceops and sourceops.panel == 'MISC':
            box = layout.box()

            row = box.row()
            row.alignment = 'CENTER'
            row.label(text='Misc')

            col = box.column()
            col.operator('sourceops.weighted_normal')
            col.operator('sourceops.triangulate')
            col.operator('sourceops.pose_bone_transforms', text='Copy Pose Bone Translation').type = 'TRANSLATION'
            col.operator('sourceops.pose_bone_transforms', text='Copy Pose Bone Rotation').type = 'ROTATION'

    def draw_texture_settings(self, box, config, item_type):
        col = common.split_column(box)
        col.prop(config, 'name')
        
        box.separator()
        box.label(text='VTF Format:', icon='TEXTURE')
        col = common.split_column(box)
        col.prop(config, 'vtf_format')
        col.prop(config, 'vtf_alphaformat')
        
        box.separator()
        box.label(text='Mipmaps:', icon='IMAGE_ZDEPTH')
        col = common.split_column(box)
        col.prop(config, 'vtf_nomipmaps')
        if not config.vtf_nomipmaps:
            col.prop(config, 'vtf_mfilter')
            col.prop(config, 'vtf_msharpen')
            
        box.separator()
        box.label(text='Resize (-resize):', icon='FULLSCREEN_ENTER')
        col = common.split_column(box)
        col.prop(config, 'vtf_resize')
        if config.vtf_resize:
            col.prop(config, 'vtf_rmethod')
            col.prop(config, 'vtf_rfilter')
            col.prop(config, 'vtf_rsharpen')
            col.prop(config, 'vtf_rwidth')
            col.prop(config, 'vtf_rheight')
            col.prop(config, 'vtf_rclampwidth')
            col.prop(config, 'vtf_rclampheight')

        box.separator()
        box.label(text='Normal Maps (-normal):', icon='MATFLUID')
        col = common.split_column(box)
        col.prop(config, 'vtf_normal_map')
        if config.vtf_normal_map:
            col.prop(config, 'vtf_nkernel')
            col.prop(config, 'vtf_nheight')
            col.prop(config, 'vtf_nalpha')
            col.prop(config, 'vtf_nscale')
            col.prop(config, 'vtf_nwrap')

        box.separator()
        box.label(text='Extras:', icon='MODIFIER')
        col = common.split_column(box)
        col.prop(config, 'vtf_gamma')
        if config.vtf_gamma:
            col.prop(config, 'vtf_gcorrection')
        col.prop(config, 'vtf_bumpscale')
        col.prop(config, 'vtf_nothumbnail')
        col.prop(config, 'vtf_noreflectivity')

        box.separator()
        flags_box = box.box()
        flags_box.label(text="Flags (-flag)", icon='BOOKMARKS')
        flags_row = flags_box.row()
        f_col1 = flags_row.column()
        f_col2 = flags_row.column()
        
        flags =["POINTSAMPLE", "TRILINEAR", "CLAMPS", "CLAMPT", "ANISOTROPIC", "HINT_DXT5", "NORMAL", "NOMIP", "NOLOD", "MINMIP", "PROCEDURAL", "RENDERTARGET", "DEPTHRENDERTARGET", "NODEBUGOVERRIDE", "SINGLECOPY", "NODEPTHBUFFER", "CLAMPU", "VERTEXTEXTURE", "SSBUMP", "BORDER"]
        
        for i, flag in enumerate(flags):
            if i < 10: f_col1.prop(config, f"vtf_flag_{flag}")
            else: f_col2.prop(config, f"vtf_flag_{flag}")
            
        box.separator()
        box.label(text='VMT Material Setup:', icon='SHADING_RENDERED')
        col = common.split_column(box)
        col.prop(config, 'vmt_shader')
        col.prop(config, 'vmt_translucent')
        col.prop(config, 'vmt_alphatest')
        col.prop(config, 'vmt_nocull')
        col.prop(config, 'vmt_envmap')
        
        box.separator()
        box.label(text='Custom VMT Editor:', icon='TEXT')
        row = box.row()
        row.scale_y = 1.2
        op = row.operator('sourceops.preview_vmt', text='Preview / Edit VMT', icon='TEXT')
        op.item_type = item_type

    def draw_list_buttons(self, layout, item):
        op = layout.operator('sourceops.list_operator', text='', icon='ADD')
        op.mode, op.item = 'ADD', item
        op = layout.operator('sourceops.list_operator', text='', icon='REMOVE')
        op.mode, op.item = 'REMOVE', item

        layout.separator()
        op = layout.operator('sourceops.list_operator', text='', icon='DUPLICATE')
        op.mode, op.item = 'COPY', item
        layout.separator()

        op = layout.operator('sourceops.list_operator', text='', icon='TRIA_UP')
        op.mode, op.item = 'MOVE_UP', item
        op = layout.operator('sourceops.list_operator', text='', icon='TRIA_DOWN')
        op.mode, op.item = 'MOVE_DOWN', item