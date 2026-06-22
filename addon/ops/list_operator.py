import bpy
import re
from .. utils import common


class SOURCEOPS_OT_AddSelectedCollections(bpy.types.Operator):
    bl_idname = 'sourceops.add_selected_collections'
    bl_options = {'REGISTER', 'UNDO'}
    bl_label = 'Add Collections'
    bl_description = 'Automatically create new static models from selected collections (NO SKINS)'

    @classmethod
    def poll(cls, context):
        return context.scene.sourceops is not None

    def execute(self, context):
        sourceops = common.get_globals(context)
        collections_to_add = set()

        if hasattr(context, "selected_ids"):
            for sel in context.selected_ids:
                if isinstance(sel, bpy.types.Collection):
                    collections_to_add.add(sel)
        
        for obj in context.selected_objects:
            for col in obj.users_collection:
                collections_to_add.add(col)

        if not collections_to_add:
            self.report({'WARNING'}, 'Select a collection in the Outliner or Viewport first!')
            return {'CANCELLED'}

        count = 0
        for col in collections_to_add:
            exists = any(m.reference == col for m in sourceops.model_items)
            if not exists:
                item = sourceops.model_items.add()
                item.name = col.name
                item.reference = col
                item.static = True
                item.surface = sourceops.default_surface
                
                col_name_check = f"{col.name} COL"
                col_col = bpy.data.collections.get(col_name_check)
                if col_col:
                    item.collision = col_col
                
                count += 1

        if count > 0:
            sourceops.model_index = len(sourceops.model_items) - 1
            self.report({'INFO'}, f'Added {count} new models.')
        else:
            self.report({'INFO'}, 'Selected collections are already in the models list.')

        return {'FINISHED'}


class SOURCEOPS_OT_AddSelectedCollectionsSkins(bpy.types.Operator):
    bl_idname = 'sourceops.add_selected_collections_skins'
    bl_options = {'REGISTER', 'UNDO'}
    bl_label = 'Add Collections + Skins'
    bl_description = 'Automatically create new static models AND add each material in order as a Skin entry'

    @classmethod
    def poll(cls, context):
        return context.scene.sourceops is not None

    def execute(self, context):
        sourceops = common.get_globals(context)
        collections_to_add = set()

        if hasattr(context, "selected_ids"):
            for sel in context.selected_ids:
                if isinstance(sel, bpy.types.Collection):
                    collections_to_add.add(sel)
        
        for obj in context.selected_objects:
            for col in obj.users_collection:
                collections_to_add.add(col)

        if not collections_to_add:
            self.report({'WARNING'}, 'Select a collection in the Outliner or Viewport first!')
            return {'CANCELLED'}

        count = 0
        for col in collections_to_add:
            exists = any(m.reference == col for m in sourceops.model_items)
            if not exists:
                item = sourceops.model_items.add()
                item.name = col.name
                item.reference = col
                item.static = True
                item.surface = sourceops.default_surface
                
                col_name_check = f"{col.name} COL"
                col_col = bpy.data.collections.get(col_name_check)
                if col_col:
                    item.collision = col_col
                
                objs_in_col =[obj for obj in col.all_objects if obj.type == 'MESH']
                selected_objs_in_col =[obj for obj in objs_in_col if obj in context.selected_objects]
                target_objs = selected_objs_in_col if selected_objs_in_col else objs_in_col
                
                ordered_mats =[]
                seen_mats = set()
                
                for obj in target_objs:
                    for mat in obj.data.materials:
                        if mat:
                            mat_clean = re.sub(r'\.\d{3}$', '', mat.name).replace(" ", "_")
                            if mat_clean not in seen_mats:
                                ordered_mats.append(mat_clean)
                                seen_mats.add(mat_clean)
                
                for mat_name in ordered_mats:
                    skin = item.skin_items.add()
                    skin.name = mat_name
                
                count += 1

        if count > 0:
            sourceops.model_index = len(sourceops.model_items) - 1
            self.report({'INFO'}, f'Added {count} new models.')
        else:
            self.report({'INFO'}, 'Selected collections are already in the models list.')

        return {'FINISHED'}


class SOURCEOPS_OT_ApplySurfaceProp(bpy.types.Operator):
    bl_idname = 'sourceops.apply_surface_prop'
    bl_options = {'REGISTER', 'UNDO'}
    bl_label = 'Apply Surface to Checked'
    bl_description = 'Apply the selected surface property to ALL checked models in the list'

    @classmethod
    def poll(cls, context):
        return context.scene.sourceops is not None

    def execute(self, context):
        sourceops = common.get_globals(context)
        count = 0
        for m in sourceops.model_items:
            if getattr(m, 'export_checked', True):
                m.surface = sourceops.default_surface
                count += 1
        
        self.report({'INFO'}, f'Applied {sourceops.default_surface} to {count} models.')
        return {'FINISHED'}


class SOURCEOPS_OT_ListOperator(bpy.types.Operator):
    bl_idname = 'sourceops.list_operator'
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}
    bl_label = 'List Operator'

    @classmethod
    def description(cls, context, properties):
        action = properties.mode.split('_')
        item = properties.item.replace('_', ' ')
        text = f'{action[0]} {item[:-1]}'
        if len(action) > 1: text = f'{text} {action[1]}'
        return text.capitalize()

    mode: bpy.props.EnumProperty(
        name='Mode',
        items=[
            ('ADD', 'Add', ''), ('REMOVE', 'Remove', ''),
            ('COPY', 'Copy', ''), ('MOVE_UP', 'Move Up', ''),
            ('MOVE_DOWN', 'Move Down', ''),
        ],
    )
    item: bpy.props.EnumProperty(
        name='Type',
        items=[
            ('GAMES', 'Games', ''), ('MODELS', 'Models', ''),
            ('MODEL_FOLDERS', 'Model Folders', ''),
            ('MATERIAL_FOLDERS', 'Material Folders', ''),
            ('MATERIALS', 'Materials', ''), ('SKINS', 'Skins', ''),
            ('TEXTUREGROUPS', 'Texture Groups', ''),
            ('SEQUENCES', 'Sequences', ''), ('EVENTS', 'Events', ''),
            ('ATTACHMENTS', 'Attachments', ''), ('PARTICLES', 'Particles', ''),
            ('MAPS', 'Maps', ''),
        ],
    )

    def add(self, parent, items, index):
        items.add()
        return len(items) - 1

    def remove(self, parent, items, index):
        items.remove(index)
        return min(max(0, index - 1), max(0, len(items) - 1))

    def copy(self, parent, items, index):
        items.add()
        old, new = items[index], items[-1]
        for key, value in old.items(): new[key] = value
        return len(items) - 1

    def move(self, parent, items, index, direction):
        neighbor = max(0, index + direction)
        items.move(neighbor, index)
        return max(0, min(neighbor, max(0, len(items) - 1)))

    def move_up(self, parent, items, index): return self.move(parent, items, index, -1)
    def move_down(self, parent, items, index): return self.move(parent, items, index, 1)

    def invoke(self, context, event):
        prefs = common.get_prefs(context)
        sourceops = common.get_globals(context)
        model = common.get_model(sourceops)
        sequence = common.get_sequence(model)

        mode_dict = {
            'ADD': self.add, 'REMOVE': self.remove, 'COPY': self.copy,
            'MOVE_UP': self.move_up, 'MOVE_DOWN': self.move_down,
        }
        item_dict = {
            'GAMES': (prefs, 'game_items', 'game_index'),
            'MODELS': (sourceops, 'model_items', 'model_index'),
            'MODEL_FOLDERS': (model, 'model_folder_items', 'model_folder_index'),
            'MATERIAL_FOLDERS': (model, 'material_folder_items', 'material_folder_index'),
            'MATERIALS': (model, 'material_items', 'material_index'),
            'SKINS': (model, 'skin_items', 'skin_index'),
            'TEXTUREGROUPS': (model, 'texturegroup_items', 'texturegroup_index'),
            'SEQUENCES': (model, 'sequence_items', 'sequence_index'),
            'EVENTS': (sequence, 'event_items', 'event_index'),
            'ATTACHMENTS': (model, 'attachment_items', 'attachment_index'),
            'PARTICLES': (model, 'particle_items', 'particle_index'),
            'MAPS': (sourceops, 'map_items', 'map_index'),
        }

        function = mode_dict[self.mode]
        parent, items_name, index_name = item_dict[self.item]

        if self.mode != 'ADD' and (not parent or not getattr(parent, items_name)): return {'CANCELLED'}

        items = getattr(parent, items_name)
        index = getattr(parent, index_name)
        index = function(parent, items, index)
        setattr(parent, index_name, index)
        
        # --- AUTO BACKUP TRIGGER FOR GAMES ---
        if self.item == 'GAMES':
            try:
                from .. import utils
                utils.backup.backup(utils.backup.filepath())
            except: pass
            
        return {'FINISHED'}