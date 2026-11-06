import bpy
import os
import re
import traceback

LOG_PREFIX = '[TEXTURE COMBINER] '
TEMP_MATERIAL_PREFIX = '__SourceOps_Bake__'

def log(*items):
    print(LOG_PREFIX + ' '.join(str(v) for v in items), flush=True)

def popup(message, *, error=False):
    log(('ERROR: ' if error else 'SUCCESS: ') + message)
    try:
        lines = [message[i:i+95] for i in range(0, len(message), 95)]
        def draw(self, context):
            for line in lines[:7]:
                self.layout.label(text=line)
        bpy.context.window_manager.popup_menu(
            draw, title='Texture Combiner — ' + ('Error' if error else 'Done'),
            icon='ERROR' if error else 'CHECKMARK')
    except Exception:
        pass

def get_main_color_input(mat):
    if not mat or not mat.node_tree:
        return None
    nodes = mat.node_tree.nodes
    output = next((n for n in nodes if n.type == 'OUTPUT_MATERIAL' and n.is_active_output), None)
    if output is None:
        output = next((n for n in nodes if n.type == 'OUTPUT_MATERIAL'), None)
    shader = None
    if output and output.inputs.get('Surface') and output.inputs['Surface'].is_linked:
        shader = output.inputs['Surface'].links[0].from_node
    if shader:
        if shader.type == 'BSDF_PRINCIPLED':
            return shader.inputs.get('Base Color')
        if shader.type in {'BSDF_DIFFUSE', 'EMISSION'}:
            return shader.inputs.get('Color')
    for node_type, socket_name in (
        ('BSDF_PRINCIPLED', 'Base Color'),
        ('BSDF_DIFFUSE', 'Color'),
        ('EMISSION', 'Color'),
    ):
        candidates = [n for n in nodes if n.type == node_type]
        if len(candidates) == 1:
            return candidates[0].inputs.get(socket_name)
    return None

def source_uv_name(obj):
    uvs = obj.data.uv_layers
    if not uvs:
        uv = obj.data.uv_layers.new(name='UVMap')
        return uv.name
    chosen = next((u for u in uvs if u.active_render), None) or uvs.active
    return chosen.name

def force_source_uvs(nodes, links, uv_name):
    for node in list(nodes):
        if node.type == 'UVMAP' and not node.uv_map:
            node.uv_map = uv_name
        if node.type == 'TEX_COORD':
            uv_socket = node.outputs.get('UV')
            if uv_socket and uv_socket.is_linked:
                explicit = nodes.new('ShaderNodeUVMap')
                explicit.uv_map = uv_name
                for link in list(uv_socket.links):
                    links.new(explicit.outputs['UV'], link.to_socket)
        if node.type == 'TEX_IMAGE':
            vector = node.inputs.get('Vector')
            if vector and not vector.is_linked:
                explicit = nodes.new('ShaderNodeUVMap')
                explicit.uv_map = uv_name
                links.new(explicit.outputs['UV'], vector)

def make_bake_material(original, original_uv, target_image):
    was_node_material = original.use_nodes
    mat = original.copy()
    mat.name = TEMP_MATERIAL_PREFIX + original.name
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    force_source_uvs(nodes, links, original_uv)

    base = get_main_color_input(mat)
    emitter = nodes.new('ShaderNodeEmission')
    emitter.name = 'Atlas_Emitter'
    emitter.inputs['Strength'].default_value = 1.0

    if not was_node_material or base is None:
        emitter.inputs['Color'].default_value = tuple(getattr(original, 'diffuse_color', (0.8, 0.8, 0.8, 1.0)))
    elif base.is_linked:
        links.new(base.links[0].from_socket, emitter.inputs['Color'])
    else:
        emitter.inputs['Color'].default_value = tuple(base.default_value)

    output = next((n for n in nodes if n.type == 'OUTPUT_MATERIAL' and n.is_active_output), None)
    if not output:
        output = nodes.new('ShaderNodeOutputMaterial')
    links.new(emitter.outputs['Emission'], output.inputs['Surface'])

    target = nodes.new('ShaderNodeTexImage')
    target.name = 'Atlas_Bake_Target'
    target.image = target_image
    for node in nodes:
        node.select = False
    target.select = True
    nodes.active = target
    return mat

def new_atlas_material(image, uv_name, name):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    tree = mat.node_tree
    tree.nodes.clear()
    out = tree.nodes.new('ShaderNodeOutputMaterial')
    out.location = (500, 100)
    shader = tree.nodes.new('ShaderNodeBsdfPrincipled')
    shader.location = (230, 100)
    if 'Metallic' in shader.inputs:
        shader.inputs['Metallic'].default_value = 0
    if 'Roughness' in shader.inputs:
        shader.inputs['Roughness'].default_value = 0.5
    img = tree.nodes.new('ShaderNodeTexImage')
    img.location = (-50, 100)
    img.image = image
    img.interpolation = 'Linear'
    uv = tree.nodes.new('ShaderNodeUVMap')
    uv.location = (-270, 100)
    uv.uv_map = uv_name
    tree.links.new(uv.outputs['UV'], img.inputs['Vector'])
    tree.links.new(img.outputs['Color'], shader.inputs['Base Color'])
    tree.links.new(shader.outputs['BSDF'], out.inputs['Surface'])
    return mat

def unused_png_path(name, atlas_size):
    stem = re.sub(r'[^a-zA-Z0-9_.-]+', '_', name).strip('._') or 'Atlas'
    folder = os.path.dirname(bpy.data.filepath) if bpy.data.filepath else bpy.app.tempdir
    size_str = f"{atlas_size//1024}K" if atlas_size >= 1024 else str(atlas_size)
    candidate = os.path.join(folder, f"{stem}_ATLAS_{size_str}.png")
    i = 1
    while os.path.exists(candidate):
        candidate = os.path.join(folder, f"{stem}_ATLAS_{size_str}_{i:02d}.png")
        i += 1
    return candidate

def create_atlas(target_col, selected_mats=None, atlas_size=2048, bake_margin=12, uv_margin=0.012):
    if target_col is None:
        raise RuntimeError('Please select a collection.')

    mesh_objs = [o for o in target_col.all_objects if o.type == 'MESH']
    if not mesh_objs:
        raise RuntimeError(f'No mesh objects found in collection "{target_col.name}".')

    if bpy.context.object and bpy.context.object.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')

    all_materials = []
    seen = set()
    for obj in mesh_objs:
        for slot in obj.material_slots:
            if slot.material and slot.material not in seen:
                seen.add(slot.material)
                all_materials.append(slot.material)

    if not all_materials:
        raise RuntimeError('No materials found on any mesh in this collection.')

    if selected_mats is None:
        selected_mats = all_materials

    selected_mat_set = set(selected_mats)
    if not selected_mat_set:
        raise RuntimeError('No materials were selected to combine. Check at least one material.')

    participating_objs = []
    for obj in mesh_objs:
        obj_mats = {slot.material for slot in obj.material_slots if slot.material}
        if obj_mats.intersection(selected_mat_set):
            participating_objs.append(obj)

    if not participating_objs:
        raise RuntimeError('None of the mesh objects use the selected materials.')

    log(f'Collection: {target_col.name} | Meshes: {len(participating_objs)} | Resolution: {atlas_size}x{atlas_size}')

    scene = bpy.context.scene
    old_selected = list(bpy.context.selected_objects)
    old_active = bpy.context.view_layer.objects.active
    old_engine = scene.render.engine
    old_device = scene.cycles.device
    old_samples = scene.cycles.samples
    old_selected_to_active = scene.render.bake.use_selected_to_active

    temp_mats = []
    atlas_uv_name = 'Atlas_UV'
    size_str = f"{atlas_size//1024}K" if atlas_size >= 1024 else str(atlas_size)
    filepath = unused_png_path(target_col.name, atlas_size)

    try:
        orig_uv_names = {}
        for obj in participating_objs:
            orig_uv = source_uv_name(obj)
            orig_uv_names[obj] = orig_uv

            if atlas_uv_name in obj.data.uv_layers:
                obj.data.uv_layers.remove(obj.data.uv_layers[atlas_uv_name])
            new_uv = obj.data.uv_layers.new(name=atlas_uv_name)
            obj.data.uv_layers.active = new_uv

        # Multi-object unwrap across separate meshes without joining
        for o in bpy.context.selected_objects:
            o.select_set(False)
        for o in participating_objs:
            o.select_set(True)
        bpy.context.view_layer.objects.active = participating_objs[0]

        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.object.mode_set(mode='OBJECT')

        for obj in participating_objs:
            for poly in obj.data.polygons:
                slot = obj.material_slots[poly.material_index] if poly.material_index < len(obj.material_slots) else None
                if slot and slot.material in selected_mat_set:
                    poly.select = True
                else:
                    poly.select = False

        bpy.ops.object.mode_set(mode='EDIT')
        log(f'Unwrapping UVs across {len(participating_objs)} separate meshes...')
        bpy.ops.uv.smart_project(
            angle_limit=1.15192,
            island_margin=uv_margin,
            margin_method='FRACTION',
            correct_aspect=True,
            scale_to_bounds=True,
        )
        bpy.ops.object.mode_set(mode='OBJECT')

        # Shift unselected faces out of 0..1 bake window
        for obj in participating_objs:
            orig_uv = orig_uv_names[obj]
            orig_uv_data = obj.data.uv_layers[orig_uv].data
            atlas_uv_data = obj.data.uv_layers[atlas_uv_name].data
            for poly in obj.data.polygons:
                slot = obj.material_slots[poly.material_index] if poly.material_index < len(obj.material_slots) else None
                if not (slot and slot.material in selected_mat_set):
                    for l_idx in poly.loop_indices:
                        atlas_uv_data[l_idx].uv = (orig_uv_data[l_idx].uv[0] + 100.0, orig_uv_data[l_idx].uv[1])

        new_img = bpy.data.images.new(
            name=f"{target_col.name}_ATLAS_{size_str}",
            width=atlas_size, height=atlas_size,
            alpha=False, float_buffer=False)
        new_img.generated_color = (0.0, 0.0, 0.0, 1.0)
        new_img.colorspace_settings.name = 'sRGB'

        cache = {}
        original_slots_map = {}
        for obj in participating_objs:
            orig_uv = orig_uv_names[obj]
            original_slots_map[obj] = [slot.material for slot in obj.material_slots]
            for slot in obj.material_slots:
                original = slot.material
                slot.link = 'DATA'
                if original is None:
                    original = bpy.data.materials.new(name='__EmptySlot')
                    original.diffuse_color = (0.8, 0.8, 0.8, 1)
                    temp_mats.append(original)
                if original not in cache:
                    cache[original] = make_bake_material(original, orig_uv, new_img)
                    temp_mats.append(cache[original])
                slot.material = cache[original]

        scene.render.engine = 'CYCLES'
        scene.cycles.device = 'CPU'
        scene.cycles.samples = 1
        scene.render.bake.use_selected_to_active = False

        for idx, obj in enumerate(participating_objs):
            orig_uv = orig_uv_names[obj]
            obj.data.uv_layers[orig_uv].active_render = True
            obj.data.uv_layers.active = obj.data.uv_layers[atlas_uv_name]

            for o in bpy.context.selected_objects:
                o.select_set(False)
            obj.select_set(True)
            bpy.context.view_layer.objects.active = obj

            use_clear = (idx == 0)
            log(f'Baking mesh {idx+1}/{len(participating_objs)} ("{obj.name}")...')
            result = bpy.ops.object.bake(
                type='EMIT', target='IMAGE_TEXTURES', uv_layer=atlas_uv_name,
                margin=bake_margin, margin_type='EXTEND',
                use_clear=use_clear, use_selected_to_active=False,
                save_mode='INTERNAL')
            if 'FINISHED' not in result:
                raise RuntimeError(f'Bake failed on mesh "{obj.name}": {result}')

        new_img.filepath_raw = filepath
        new_img.file_format = 'PNG'
        new_img.save()

        new_mat = new_atlas_material(new_img, atlas_uv_name, f"{target_col.name}_Atlas_Mat")

        for obj in participating_objs:
            orig_uv = orig_uv_names[obj]
            orig_uv_data = obj.data.uv_layers[orig_uv].data
            atlas_uv_data = obj.data.uv_layers[atlas_uv_name].data
            orig_mats = original_slots_map[obj]

            for poly in obj.data.polygons:
                slot_m = orig_mats[poly.material_index] if poly.material_index < len(orig_mats) else None
                if not (slot_m and slot_m in selected_mat_set):
                    for l_idx in poly.loop_indices:
                        atlas_uv_data[l_idx].uv = orig_uv_data[l_idx].uv

            obj_all_selected = all((m in selected_mat_set) for m in orig_mats if m)

            if obj_all_selected:
                obj.data.materials.clear()
                obj.data.materials.append(new_mat)
                for poly in obj.data.polygons:
                    poly.material_index = 0
            else:
                unselected_unique = []
                seen_unsel = set()
                for m in orig_mats:
                    if m and m not in selected_mat_set and m not in seen_unsel:
                        seen_unsel.add(m)
                        unselected_unique.append(m)

                mat_to_idx = {m: 0 for m in selected_mat_set}
                for idx_u, m in enumerate(unselected_unique, start=1):
                    mat_to_idx[m] = idx_u

                for poly in obj.data.polygons:
                    orig_m = orig_mats[poly.material_index] if poly.material_index < len(orig_mats) else None
                    poly.material_index = mat_to_idx.get(orig_m, 0)

                obj.data.materials.clear()
                obj.data.materials.append(new_mat)
                for m in unselected_unique:
                    obj.data.materials.append(m)

            obj.data.uv_layers[atlas_uv_name].active_render = True
            obj.data.uv_layers.active = obj.data.uv_layers[atlas_uv_name]

        popup(f"Combined textures on {len(participating_objs)} separate meshes! PNG: {filepath}")
        return participating_objs, filepath

    finally:
        if bpy.context.object and bpy.context.object.mode != 'OBJECT':
            try:
                bpy.ops.object.mode_set(mode='OBJECT')
            except Exception:
                pass
        scene.render.engine = old_engine
        scene.cycles.device = old_device
        scene.cycles.samples = old_samples
        scene.render.bake.use_selected_to_active = old_selected_to_active

        for mat in temp_mats:
            if mat and mat.users == 0:
                bpy.data.materials.remove(mat)

class SOURCEOPS_OT_CombineTextures(bpy.types.Operator):
    bl_idname = 'sourceops.combine_textures'
    bl_label = 'Combine Textures'
    bl_description = 'Bake selected materials across collection into a shared texture atlas on each separate mesh'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        sourceops = getattr(context.scene, 'sourceops', None)
        return bool(sourceops and sourceops.combiner_target_collection)

    def execute(self, context):
        sourceops = context.scene.sourceops
        target_col = sourceops.combiner_target_collection
        atlas_size = int(getattr(sourceops, 'combiner_atlas_size', '2048'))
        bake_margin = getattr(sourceops, 'combiner_bake_margin', 12)
        uv_margin = getattr(sourceops, 'combiner_uv_margin', 0.012)

        mesh_objs = [o for o in target_col.all_objects if o.type == 'MESH']
        all_materials = []
        seen = set()
        for o in mesh_objs:
            for slot in o.material_slots:
                if slot.material and slot.material not in seen:
                    seen.add(slot.material)
                    all_materials.append(slot.material)

        selected_mats = [m for m in all_materials if getattr(m, 'sourceops_combine', True)]

        try:
            objs, filepath = create_atlas(
                target_col=target_col,
                selected_mats=selected_mats,
                atlas_size=atlas_size,
                bake_margin=bake_margin,
                uv_margin=uv_margin
            )
            self.report({'INFO'}, f"Combined textures across {len(objs)} meshes at {atlas_size}x{atlas_size}")
            return {'FINISHED'}
        except Exception as e:
            traceback.print_exc()
            popup(f"{e}", error=True)
            self.report({'ERROR'}, f"Atlas bake failed: {e}")
            return {'CANCELLED'}

class SOURCEOPS_OT_CombinerSelectAllMats(bpy.types.Operator):
    bl_idname = 'sourceops.combiner_select_all_mats'
    bl_label = 'Select All'
    bl_description = 'Select all materials across the collection'
    bl_options = {'INTERNAL', 'UNDO'}

    def execute(self, context):
        col = context.scene.sourceops.combiner_target_collection
        if col:
            for o in col.all_objects:
                if o.type == 'MESH':
                    for slot in o.material_slots:
                        if slot.material:
                            slot.material.sourceops_combine = True
        return {'FINISHED'}

class SOURCEOPS_OT_CombinerDeselectAllMats(bpy.types.Operator):
    bl_idname = 'sourceops.combiner_deselect_all_mats'
    bl_label = 'Deselect All'
    bl_description = 'Deselect all materials across the collection'
    bl_options = {'INTERNAL', 'UNDO'}

    def execute(self, context):
        col = context.scene.sourceops.combiner_target_collection
        if col:
            for o in col.all_objects:
                if o.type == 'MESH':
                    for slot in o.material_slots:
                        if slot.material:
                            slot.material.sourceops_combine = False
        return {'FINISHED'}

class SOURCEOPS_OT_CombinerPickActive(bpy.types.Operator):
    bl_idname = 'sourceops.combiner_pick_active'
    bl_label = 'Pick Active Collection'
    bl_description = 'Pick the collection of the active object or active collection in outliner'
    bl_options = {'INTERNAL', 'UNDO'}

    def execute(self, context):
        sourceops = context.scene.sourceops
        col = context.view_layer.active_layer_collection.collection
        if col and col != context.scene.collection and any(o.type == 'MESH' for o in col.all_objects):
            sourceops.combiner_target_collection = col
            self.report({'INFO'}, f"Selected collection: '{col.name}'")
            return {'FINISHED'}

        obj = context.active_object
        if obj and obj.users_collection:
            sourceops.combiner_target_collection = obj.users_collection[0]
            self.report({'INFO'}, f"Selected collection: '{sourceops.combiner_target_collection.name}'")
            return {'FINISHED'}

        self.report({'WARNING'}, 'No valid collection found from active object!')
        return {'FINISHED'}

classes = (
    SOURCEOPS_OT_CombineTextures,
    SOURCEOPS_OT_CombinerSelectAllMats,
    SOURCEOPS_OT_CombinerDeselectAllMats,
    SOURCEOPS_OT_CombinerPickActive,
)

def register():
    bpy.types.Material.sourceops_combine = bpy.props.BoolProperty(
        name="Combine to Atlas",
        description="Include this material when combining textures into the atlas",
        default=True
    )
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    if hasattr(bpy.types.Material, 'sourceops_combine'):
        del bpy.types.Material.sourceops_combine