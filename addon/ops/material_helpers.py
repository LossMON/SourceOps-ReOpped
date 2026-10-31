import bpy

def detect_model_normal_maps(model):
    normal_maps = []
    seen = set()

    for mat in bpy.data.materials:
        if not mat or not mat.use_nodes or not mat.node_tree:
            continue
        nodes = mat.node_tree.nodes

        for node in nodes:
            if node.type in ('NORMAL_MAP', 'BUMP'):
                for inp in ('Color', 'Height', 'Normal'):
                    socket = node.inputs.get(inp)
                    if socket and socket.is_linked:
                        from_node = socket.links[0].from_node
                        if from_node.type == 'TEX_IMAGE' and from_node.image:
                            img_name = from_node.image.name
                            if img_name not in seen:
                                seen.add(img_name)
                                normal_maps.append(img_name)

        for node in nodes:
            if node.type == 'TEX_IMAGE' and node.image:
                name_lower = node.image.name.lower()
                is_normal_name = any(k in name_lower for k in ('normal', 'norm', 'bump', '_n.', '_n_', '_nm'))
                if is_normal_name and node.image.name not in seen:
                    seen.add(node.image.name)
                    normal_maps.append(node.image.name)

    return normal_maps

class SOURCEOPS_OT_RemoveLinkedMaterial(bpy.types.Operator):
    bl_idname = 'sourceops.remove_linked_material'
    bl_label = 'Remove Linked Material'
    bl_options = {'INTERNAL', 'UNDO'}
    material_name: bpy.props.StringProperty()

    def execute(self, context):
        sourceops = getattr(context.scene, 'sourceops', None)
        model = sourceops.model_items[sourceops.model_index] if (sourceops and len(sourceops.model_items) > sourceops.model_index) else None
        if model and len(model.skin_items) > model.skin_index:
            skin = model.skin_items[model.skin_index]
            current = [m for m in skin.linked_materials.split() if m]
            if self.material_name in current:
                current.remove(self.material_name)
                skin.linked_materials = " ".join(current)
        return {'FINISHED'}

class SOURCEOPS_OT_AutoDetectNormalMap(bpy.types.Operator):
    bl_idname = 'sourceops.auto_detect_normal_map'
    bl_label = 'Auto Detect Normal Map'
    bl_description = 'Automatically detect the normal map applied to this material in Blender'
    bl_options = {'INTERNAL', 'UNDO'}

    def execute(self, context):
        sourceops = getattr(context.scene, 'sourceops', None)
        model = sourceops.model_items[sourceops.model_index] if (sourceops and len(sourceops.model_items) > sourceops.model_index) else None
        if not model or len(model.material_items) <= model.material_index:
            return {'CANCELLED'}

        mat_item = model.material_items[model.material_index]
        target_mat = bpy.data.materials.get(mat_item.name)

        found_name = ""
        if target_mat and target_mat.use_nodes and target_mat.node_tree:
            for node in target_mat.node_tree.nodes:
                if node.type in ('NORMAL_MAP', 'BUMP'):
                    for inp in ('Color', 'Height', 'Normal'):
                        sock = node.inputs.get(inp)
                        if sock and sock.is_linked:
                            from_n = sock.links[0].from_node
                            if from_n.type == 'TEX_IMAGE' and from_n.image:
                                found_name = from_n.image.name
                                break
                if found_name:
                    break

        if not found_name:
            all_detected = detect_model_normal_maps(model)
            if all_detected:
                found_name = all_detected[0]

        if found_name:
            mat_item.normal_map = found_name
            self.report({'INFO'}, f"Auto-detected Normal Map: {found_name}")
        else:
            self.report({'WARNING'}, "No Normal Map texture node detected for this material.")

        return {'FINISHED'}

class SOURCEOPS_OT_ClearNormalMap(bpy.types.Operator):
    bl_idname = 'sourceops.clear_normal_map'
    bl_label = 'Clear Normal Map'
    bl_description = 'Deselect this normal map'
    bl_options = {'INTERNAL', 'UNDO'}

    def execute(self, context):
        sourceops = getattr(context.scene, 'sourceops', None)
        model = sourceops.model_items[sourceops.model_index] if (sourceops and len(sourceops.model_items) > sourceops.model_index) else None
        if model and len(model.material_items) > model.material_index:
            model.material_items[model.material_index].normal_map = ""
        return {'FINISHED'}

class SOURCEOPS_OT_NormalMapPopup(bpy.types.Operator):
    bl_idname = 'sourceops.normal_map_popup'
    bl_label = 'Normal Map Notice'
    bl_options = {'INTERNAL'}

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=380)

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        col.label(text="A normal map is already selected for this material!", icon='INFO')
        col.label(text="Clear the Assigned Normal in the NormalMap box first", icon='BLANK1')
        col.label(text="if you want to generate a new one from scratch.", icon='BLANK1')