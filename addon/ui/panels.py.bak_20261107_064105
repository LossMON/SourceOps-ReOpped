import bpy
from .. utils import common
from .. import icons


def get_material_preview_icon(layout, mat):
    if not mat:
        return 0, 'MATERIAL'
    if mat.use_nodes and mat.node_tree:
        img_node = next((n for n in mat.node_tree.nodes if n.type == 'TEX_IMAGE' and n.image), None)
        if img_node and img_node.image:
            img = img_node.image
            if hasattr(img, 'preview_ensure'):
                img.preview_ensure()
            try:
                val = layout.icon(img)
                if val:
                    return val, ''
            except Exception:
                pass
            if getattr(img, 'preview', None) and img.preview.icon_id:
                return img.preview.icon_id, ''

    if hasattr(mat, 'preview_ensure'):
        mat.preview_ensure()
    try:
        val = layout.icon(mat)
        if val:
            return val, ''
    except Exception:
        pass
    if getattr(mat, 'preview', None) and mat.preview.icon_id:
        return mat.preview.icon_id, ''

    return 0, 'MATERIAL'


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
                col.prop(model, 'name', placeholder='Name of the .MDL model')
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

                box.separator()
                row = box.row()
                row.alignment = 'CENTER'
                row.label(text='(Global Material Settings, Materials that are listed in materials properties will ignore these Global Settings)')
                
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
                
                flags = ["POINTSAMPLE", "TRILINEAR", "CLAMPS", "CLAMPT", "ANISOTROPIC", "HINT_DXT5", "NORMAL", "NOMIP", "NOLOD", "MINMIP", "PROCEDURAL", "RENDERTARGET", "DEPTHRENDERTARGET", "NODEBUGOVERRIDE", "SINGLECOPY", "NODEPTHBUFFER", "CLAMPU", "VERTEXTEXTURE", "SSBUMP", "BORDER"]
                
                for i, flag in enumerate(flags):
                    if i < 10: f_col1.prop(model, f"vtf_flag_{flag}")
                    else: f_col2.prop(model, f"vtf_flag_{flag}")
                    
                box.separator()
                box.label(text='VMT Material Setup (Global):', icon='SHADING_RENDERED')
                col = common.split_column(box)
                col.prop(model, 'vmt_shader')
                col.prop(model, 'vmt_translucent')
                col.prop(model, 'vmt_alphatest')
                col.prop(model, 'vmt_nocull')

                # Global Cubemap Reflection ($envmap)
                box.separator()
                box.label(text='Cubemap Reflection ($envmap):', icon='SHADING_TEXTURE')
                col = common.split_column(box)
                col.prop(model, 'vmt_envmap', text='Enable Cubemap ($envmap)')
                if model.vmt_envmap:
                    col.prop(model, 'vmt_use_envmaptint', text='Enable $envmaptint')
                    if model.vmt_use_envmaptint:
                        col.prop(model, 'vmt_envmaptint')
                    col.prop(model, 'vmt_envmapfresnel')
                    col.prop(model, 'vmt_envmapmask_source')

                # Global Reflectivity ($reflectivity)
                box.separator()
                box.label(text='Reflectivity ($reflectivity):', icon='SHADING_RENDERED')
                col = common.split_column(box)
                col.prop(model, 'vmt_reflectivity', text='Enable $reflectivity')
                if model.vmt_reflectivity:
                    col.prop(model, 'vmt_reflectivity_vec')

                # Global Phong Specular ($phong)
                box.separator()
                box.label(text='Specular Highlight ($phong):', icon='LIGHT_SUN')
                col = common.split_column(box)
                col.prop(model, 'vmt_phong', text='Enable Phong ($phong)')
                if model.vmt_phong:
                    col.prop(model, 'vmt_phongboost')
                    col.prop(model, 'vmt_phongexponent')
                    col.prop(model, 'vmt_phongfresnelranges')
                    col.prop(model, 'vmt_phongtint')
                    col.prop(model, 'vmt_phongalbedotint')
                    col.prop(model, 'vmt_phongmask_source')

                box.separator()
                box.label(text='Global VMT Editor:', icon='TEXT')
                row = box.row(align=True)
                row.scale_y = 1.2
                op = row.operator('sourceops.preview_vmt', text='Preview / Edit VMT (Global)', icon='TEXT')
                op.is_global = True
                op2 = row.operator('sourceops.reset_vmt', text='Reset', icon='FILE_REFRESH')
                op2.is_global = True
                row2 = box.row(align=True)
                row2.prop(model, 'do_not_sort_vmts', text='Do Not Sort VMTs (Enable This If The Vmt Options Are Getting Messed Up)', icon='PINNED')

        elif model and sourceops.panel == 'MODEL_OPTIONS':
            box = layout.box()
            row = box.row()
            row.alignment = 'CENTER'
            row.label(text='Model Options')

            col = common.split_column(box)
            col.prop(model, 'surface')
            col.prop(model, 'glass')
            col.prop(model, 'static')
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
            row.alignment = 'CENTER'
            row.label(text='(No need to type "models/", it is created automatically) Example: guns/pink_gun')

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
            row.alignment = 'CENTER'
            row.label(text='(No need to type "materials/", it is created automatically) Example: guns/pink_gun')

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

            # --- NORMAL MAP BOX ---
            norm_box = layout.box()
            norm_header = norm_box.row()
            norm_header.alignment = 'CENTER'
            norm_header.label(text='NormalMap', icon='TEXTURE')

            if material_item:
                norm_col = common.split_column(norm_box)
                n_row = norm_col.row(align=True)
                search_source = 'images' if len(bpy.data.images) > 0 else 'materials'
                n_row.prop_search(material_item, 'normal_map', bpy.data, search_source, text='Assigned Normal')
                n_row.operator('sourceops.auto_detect_normal_map', text='', icon='EYEDROPPER')
                if material_item.normal_map:
                    n_row.operator('sourceops.clear_normal_map', text='', icon='X')

                norm_box.separator()
                norm_box.label(text='Normal Map Settings (-normal):', icon='MATFLUID')
                gen_col = common.split_column(norm_box)
                gen_col.prop(material_item, 'vtf_nkernel')
                gen_col.prop(material_item, 'vtf_nheight')
                gen_col.prop(material_item, 'vtf_nalpha')
                gen_col.prop(material_item, 'vtf_nscale')
                gen_col.prop(material_item, 'vtf_nwrap')

                if material_item.vtf_normal_map:
                    norm_box.label(text='Mode: Generating new normal map from base texture', icon='INFO')
                elif material_item.normal_map:
                    norm_box.label(text='Mode: Using assigned normal map from model', icon='CHECKMARK')
            else:
                norm_box.label(text='Select a material above to configure Normal Map', icon='INFO')

            # --- SKINS LIST ---
            box = layout.box()
            row = box.row()
            row.alignment = 'CENTER'
            row.label(text='Skins')

            row = box.row()
            row.template_list('SOURCEOPS_UL_SkinList', '', model, 'skin_items', model, 'skin_index', rows=4)
            col = row.column(align=True)
            self.draw_list_buttons(col, 'SKINS')

            if skin:
                split = box.split(factor=0.40)
                col_info = split.column()
                col_info.scale_y = 0.8
                col_info.label(text='Skin 0 = Material in Blender', icon='INFO')
                col_info.label(text='Linked = Materials that swap')
                col_info.separator(factor=0.4)
                col_info.label(text='Example:')
                col_info.label(text='• Skin 0 (Base):')
                col_info.label(text='  table_bluechair')
                col_info.label(text='  + Link: table_bluecup')
                col_info.label(text='• Skin 1 (New):')
                col_info.label(text='  table_redchair')
                col_info.label(text='  + Link: table_redcup')

                col_right = split.column()
                col = common.split_column(col_right)
                col.prop_search(skin, 'name', bpy.data, 'materials', text='Skin Material')
                col.prop_search(skin, 'add_linked_skin', bpy.data, 'materials', text='Linked Skins', icon='ADD')

                box_links = col_right.box()
                box_links.scale_y = 0.85
                linked_mats = [m for m in skin.linked_materials.split() if m]
                if linked_mats:
                    h_row = box_links.row(align=True)
                    h_row.label(text="Linked (" + str(len(linked_mats)) + "):", icon='LINKED')
                    h_row.operator('sourceops.clear_linked_materials', text='Clear', icon='X')
                    for l_mat in linked_mats:
                        p_row = box_links.row(align=True)
                        p_row.label(text=l_mat, icon='MATERIAL')
                        rm_op = p_row.operator('sourceops.remove_linked_material', text='', icon='X')
                        rm_op.material_name = l_mat
                else:
                    box_links.label(text="No linked skins", icon='LINKED')

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

        if sourceops and sourceops.panel == 'TEXTURE_COMBINER':
            box = layout.box()

            row = box.row()
            row.alignment = 'CENTER'
            row.label(text='Texture Combiner', icon='IMAGE')

            # --- COLLECTION SELECTION ---
            box_col = box.box()
            box_col.label(text='Model Collection:', icon='OUTLINER_COLLECTION')
            row = box_col.row(align=True)
            row.prop(sourceops, 'combiner_target_collection', text='')
            row.operator('sourceops.combiner_pick_active', text='', icon='EYEDROPPER')

            target_col = sourceops.combiner_target_collection

            if target_col:
                mesh_objs = [o for o in target_col.all_objects if o.type == 'MESH']

                if mesh_objs:
                    materials_in_col = []
                    seen_mats = set()
                    for o in mesh_objs:
                        for slot in o.material_slots:
                            if slot.material and slot.material not in seen_mats:
                                seen_mats.add(slot.material)
                                materials_in_col.append(slot.material)

                    # --- MATERIALS SELECTION ---
                    box_mats = box.box()
                    if materials_in_col:
                        selected_count = sum(1 for m in materials_in_col if getattr(m, 'sourceops_combine', True))
                        h_row = box_mats.row(align=True)
                        h_row.label(text=f"Materials to Combine ({selected_count}/{len(materials_in_col)}):", icon='MATERIAL')
                        h_row.operator('sourceops.combiner_select_all_mats', text='All', icon='CHECKBOX_HLT')
                        h_row.operator('sourceops.combiner_deselect_all_mats', text='None', icon='CHECKBOX_DEHLT')

                        col_mats = box_mats.column(align=True)
                        col_mats.scale_y = 1.05
                        for mat in materials_in_col:
                            row = col_mats.row(align=True)
                            row.prop(mat, 'sourceops_combine', text='')
                            icon_val, icon_str = get_material_preview_icon(layout, mat)
                            if icon_val:
                                row.label(text=mat.name, icon_value=icon_val)
                            else:
                                row.label(text=mat.name, icon=icon_str)
                    else:
                        box_mats.label(text='No materials found on meshes in this collection!', icon='ERROR')

                    # --- PROPERTIES BOX ---
                    box_settings = box.box()
                    box_settings.label(text='Properties:', icon='SETTINGS')
                    col_set = common.split_column(box_settings)
                    col_set.prop(sourceops, 'combiner_atlas_size', text='Atlas size')

                    # Switch: Quadratic / Power of 2 / Auto shows SMC settings
                    if sourceops.combiner_atlas_size in {'QUAD', 'PO2', 'AUTO'}:
                        col_set.prop(sourceops, 'combiner_crop')
                        col_set.prop(sourceops, 'combiner_pixel_art')
                        col_set.prop(sourceops, 'combiner_diffuse_size')
                        col_set.prop(sourceops, 'combiner_gaps')
                    else:
                        # 2048, 512, 1024, 4096: shows old settings only
                        col_set.prop(sourceops, 'combiner_bake_margin', text='Margin (px)')
                        col_set.prop(sourceops, 'combiner_uv_margin', text='UV Island Margin')

                    # --- APPLY BUTTON ---
                    box.separator()
                    row = box.row()
                    row.scale_y = 1.6
                    row.operator('sourceops.combine_textures', text='Combine Textures', icon='OUTPUT')
                else:
                    box.label(text='This collection contains no mesh objects!', icon='ERROR')
            else:
                box_info = box.box()
                col_info = box_info.column()
                col_info.label(text='1. Select the collection containing your model meshes.', icon='INFO')
                col_info.label(text='2. All materials across the collection are auto-detected.', icon='BLANK1')
                col_info.label(text='3. Choose options and click Combine Textures.', icon='BLANK1')
                col_info.label(text='Combines textures into a single shared atlas.', icon='BLANK1')

    def draw_texture_settings(self, box, config, item_type):
        col = common.split_column(box)
        col.prop_search(config, 'name', bpy.data, 'materials', text='Material Name')
        
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
        
        flags = ["POINTSAMPLE", "TRILINEAR", "CLAMPS", "CLAMPT", "ANISOTROPIC", "HINT_DXT5", "NORMAL", "NOMIP", "NOLOD", "MINMIP", "PROCEDURAL", "RENDERTARGET", "DEPTHRENDERTARGET", "NODEBUGOVERRIDE", "SINGLECOPY", "NODEPTHBUFFER", "CLAMPU", "VERTEXTEXTURE", "SSBUMP", "BORDER"]
        
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

        # --- REFLECTIONS ($envmap) ---
        box.separator()
        box.label(text='Cubemap Reflection ($envmap):', icon='SHADING_TEXTURE')
        col = common.split_column(box)
        col.prop(config, 'vmt_envmap', text='Enable Cubemap ($envmap)')
        if config.vmt_envmap:
            col.prop(config, 'vmt_use_envmaptint', text='Enable $envmaptint')
            if config.vmt_use_envmaptint:
                col.prop(config, 'vmt_envmaptint')
            col.prop(config, 'vmt_envmapfresnel')
            col.prop(config, 'vmt_envmapmask_source')

        # --- REFLECTIVITY ($reflectivity) ---
        box.separator()
        box.label(text='Reflectivity ($reflectivity):', icon='SHADING_RENDERED')
        col = common.split_column(box)
        col.prop(config, 'vmt_reflectivity', text='Enable $reflectivity')
        if config.vmt_reflectivity:
            col.prop(config, 'vmt_reflectivity_vec')

        # --- PHONG SPECULAR ($phong) ---
        box.separator()
        box.label(text='Specular Highlight ($phong):', icon='LIGHT_SUN')
        col = common.split_column(box)
        col.prop(config, 'vmt_phong', text='Enable Phong ($phong)')
        if config.vmt_phong:
            col.prop(config, 'vmt_phongboost')
            col.prop(config, 'vmt_phongexponent')
            col.prop(config, 'vmt_phongfresnelranges')
            col.prop(config, 'vmt_phongtint')
            col.prop(config, 'vmt_phongalbedotint')
            col.prop(config, 'vmt_phongmask_source')
        
        box.separator()
        box.label(text='Custom VMT Editor:', icon='TEXT')
        row = box.row(align=True)
        row.scale_y = 1.2
        op = row.operator('sourceops.preview_vmt', text='Preview / Edit VMT', icon='TEXT')
        op.item_type = item_type
        op.is_global = False
        
        op2 = row.operator('sourceops.reset_vmt', text='Reset', icon='FILE_REFRESH')
        op2.item_type = item_type
        op2.is_global = False
        
        row3 = box.row(align=True)
        row3.prop(config, 'do_not_sort_vmts', text='Do Not Sort VMTs (Enable This If The Vmt Options Are Getting Messed Up)', icon='PINNED')

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