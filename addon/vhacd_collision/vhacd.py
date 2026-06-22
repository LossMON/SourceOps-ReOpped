# ----------------
# V-HACD Blender add-on
# Copyright (c) 2014, Alain Ducharme
# ----------------

import bpy
import bmesh
import re
import os
import subprocess
from bpy.props import BoolProperty, EnumProperty, FloatProperty, IntProperty, PointerProperty, StringProperty
from mathutils import Matrix, Vector

from subprocess import Popen
from os import path as os_path
from tempfile import gettempdir

# Import common utilities so we can safely read the user's Wine path
from ..utils import common


def obj_export(mesh, fullpath):
    '''Export triangulated mesh to Wavefront OBJ Format (Required for V-HACD V2.2+)'''
    with open(fullpath, 'w', encoding='utf-8') as f:
        for vert in mesh.vertices:
            f.write(f"v {vert.co.x:g} {vert.co.y:g} {vert.co.z:g}\n")
        for face in mesh.polygons:
            # Wavefront OBJ uses 1-based indexing for faces
            indices = " ".join(str(v + 1) for v in face.vertices)
            f.write(f"f {indices}\n")


class VHACD_OT_RenameHulls(bpy.types.Operator):
    bl_idname = 'object.vhacd_rename_hulls'
    bl_label = 'Rename Hulls'
    bl_description = 'Rename selected objects with name of active object using a template'
    bl_options = {'REGISTER', 'UNDO'}

    name_template: StringProperty(
        name='Name Template',
        description='Name template used for generated hulls.\n? = original mesh name\n# = hull id',
        default='?_hull_#'
    )

    set_display: BoolProperty(
        name='Set Display',
        description='Set the display properties of selected objects to wireframe',
        default=True
    )

    def execute(self, context):
        name_template = self.name_template if self.name_template else '?_hull_#'

        active_object = context.active_object
        selected_objects =[ob for ob in context.selected_objects if ob != active_object and ob.type == 'MESH']

        for index, ob in enumerate(selected_objects):
            name = name_template.replace('?', active_object.name, 1)
            name = name.replace('#', str(index + 1), 1)
            if name == name_template:
                name += str(index + 1)
            ob.name = name
            ob.data.name = name

            if self.set_display:
                ob.display_type = 'WIRE'

        return {'FINISHED'}


class VHACD_OT_SelectHulls(bpy.types.Operator):
    bl_idname = 'object.vhacd_select_hulls'
    bl_label = 'Select Hulls'
    bl_description = 'Select any convex hulls in the scene for the current object based on object name'
    bl_options = {'REGISTER', 'UNDO'}

    only_hulls: BoolProperty(
        name="Only Hulls",
        default=False,
        description="Select only hulls and deselect everything else"
    )

    def execute(self, context):
        selected_objects =[ob for ob in bpy.context.selected_objects if ob.type == 'MESH']

        if len(selected_objects) < 1:
            self.report({'ERROR'}, 'First select an object to find its matching hulls')
            return {'CANCELLED'}

        all_objects =[ob for ob in context.scene.objects if ob.type == 'MESH']

        name_template = "?_hull_[0-9]+"

        hulls =[]

        for ob in selected_objects:
            regex = re.compile(name_template.replace('?', ob.name, 1))

            for ob_search in all_objects[-1::-1]:
                if regex.match(ob_search.name):
                    hulls.append(ob_search)
                    all_objects.remove(ob_search)

        if self.only_hulls:
            bpy.ops.object.select_all(action='DESELECT')

        for ob in hulls:
            ob.select_set(True)

        return {'FINISHED'}


class VHACD_OT_VHACD(bpy.types.Operator):
    bl_idname = 'object.vhacd'
    bl_label = 'SourceOps ReOpped Collision Menu (V-HACD) (Convex Hull)'
    bl_description = 'Create accurate convex hulls using Hierarchical Approximate Convex Decomposition'
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.active_object.type == 'MESH'

    remove_doubles: BoolProperty(
        name='Remove Doubles',
        description='Collapse overlapping vertices in generated mesh',
        default=True
    )

    apply_transforms: EnumProperty(
        name='Apply',
        description='Apply Transformations to generated mesh',
        items=(
            ('LRS', 'Location + Rotation + Scale', 'Apply location, rotation and scale'),
            ('RS', 'Rotation + Scale', 'Apply rotation and scale'),
            ('S', 'Scale', 'Apply scale only'),
            ('NONE', 'None', 'Do not apply transformations'),
        ),
        default='NONE'
    )

    resolution: IntProperty(
        name='Voxel Resolution',
        description='Maximum number of voxels generated during the voxelization stage',
        default=100000,
        min=10000,
        max=64000000
    )

    depth: IntProperty(
        name='Clipping Depth',
        description='Maximum number of clipping stages',
        default=20,
        min=1,
        max=32
    )

    concavity: FloatProperty(
        name='Maximum Concavity',
        description='Maximum concavity',
        default=0.0025,
        min=0.0,
        max=1.0,
        precision=4
    )

    planeDownsampling: IntProperty(
        name='Plane Downsampling',
        description='Granularity of the search for the best clipping plane',
        default=4,
        min=1,
        max=16
    )

    convexhullDownsampling: IntProperty(
        name='Convex Hull Downsampling',
        description='Precision of the convex-hull generation process',
        default=4,
        min=1,
        max=16
    )

    alpha: FloatProperty(
        name='Alpha',
        description='Bias toward clipping along symmetry planes',
        default=0.05,
        min=0.0,
        max=1.0,
        precision=4
    )

    beta: FloatProperty(
        name='Beta',
        description='Bias toward clipping along revolution axes',
        default=0.05,
        min=0.0,
        max=1.0,
        precision=4
    )

    gamma: FloatProperty(
        name='Gamma',
        description='Maximum allowed concavity during the merge stage',
        default=0.00125,
        min=0.0,
        max=1.0,
        precision=5
    )

    pca: BoolProperty(
        name='PCA',
        description='Enable/disable normalizing the mesh before applying convex decomposition',
        default=False
    )

    mode: EnumProperty(
        name='ACD Mode',
        description='Approximate convex decomposition mode',
        items=(('VOXEL', 'Voxel', 'Voxel ACD Mode'),
               ('TETRAHEDRON', 'Tetrahedron', 'Tetrahedron ACD Mode')),
        default='VOXEL'
    )

    maxNumVerticesPerCH: IntProperty(
        name='Maximum Vertices Per CH',
        description='Maximum number of vertices per convex-hull',
        default=32,
        min=4,
        max=1024
    )

    minVolumePerCH: FloatProperty(
        name='Minimum Volume Per CH',
        description='Minimum volume to add vertices to convex-hulls',
        default=0.0001,
        min=0.0,
        max=0.01,
        precision=5
    )

    collection_mode: EnumProperty(
        name='Target Collection',
        description='Choose exactly one location where the generated hulls will be placed',
        items=(
            ('COLLISION_MODELS', 'Put in "Collision Models" Collection', 'Move all models to a single collection named Collision Models'),
            ('SAME_AS_PARENT', 'SAME AS COLLECTION NAME', 'Move models to a new collection immediately beneath the source object\'s collection'),
            ('NONE', 'NO COLLECTION', 'Leave models in the current active collection (default behavior)'),
        ),
        default='COLLISION_MODELS'
    )

    def execute(self, context):
        
        # FIND THE NATIVE V-HACD EXECUTABLE
        current_dir = os_path.dirname(os_path.abspath(__file__))
        vhacd_lower = os_path.join(current_dir, 'testVHACD.exe')
        vhacd_upper = os_path.join(current_dir, 'testvhacd.exe')
        vhacd_path = vhacd_lower if os_path.exists(vhacd_lower) else vhacd_upper
        
        if not os_path.exists(vhacd_path):
            self.report({'ERROR'}, f'Cannot find testVHACD.exe at {current_dir}')
            return {'CANCELLED'}

        # USE THE OS TEMP DIRECTORY FOR FILES
        data_path = gettempdir()

        selected = bpy.context.selected_objects

        if not selected:
            self.report({'ERROR'}, 'Object(s) must be selected first')
            return {'CANCELLED'}
        for ob in selected:
            ob.select_set(False)

        new_objects =[]

        for ob in selected:
            if ob.type != 'MESH':
                continue

            filename = ''.join(c for c in ob.name if c.isalnum() or c in (' ', '.', '_')).rstrip()

            # USING RELATIVE FILE NAMES ONLY TO PREVENT LINUX/WINDOWS PATH CONFLICTS
            obj_name = f"{filename}.obj"
            out_name = f"{filename}.wrl"
            log_name = f"{filename}_log.txt"

            obj_full_path = os_path.join(data_path, obj_name)
            out_full_path = os_path.join(data_path, out_name)

            mesh = ob.data.copy()

            translation, quaternion, scale = ob.matrix_world.decompose()
            scale_matrix = Matrix(((scale.x, 0, 0, 0), (0, scale.y, 0, 0), (0, 0, scale.z, 0), (0, 0, 0, 1)))
            if self.apply_transforms in['S', 'RS', 'LRS']:
                pre_matrix = scale_matrix
                post_matrix = Matrix()
            else:
                pre_matrix = Matrix()
                post_matrix = scale_matrix
            if self.apply_transforms in['RS', 'LRS']:
                pre_matrix = quaternion.to_matrix().to_4x4() @ pre_matrix
            else:
                post_matrix = quaternion.to_matrix().to_4x4() @ post_matrix
            if self.apply_transforms == 'LRS':
                pre_matrix = Matrix.Translation(translation) @ pre_matrix
            else:
                post_matrix = Matrix.Translation(translation) @ post_matrix

            mesh.transform(pre_matrix)

            bm = bmesh.new()
            bm.from_mesh(mesh)
            if self.remove_doubles:
                bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0001)
            bmesh.ops.triangulate(bm, faces=bm.faces)
            bm.to_mesh(mesh)
            bm.free()

            print('\n[SourceOps] Exporting mesh for V-HACD: {}...'.format(obj_full_path))
            obj_export(mesh, obj_full_path)
            bpy.data.meshes.remove(mesh)
            
            # --- WINE DETECTION & SAFE EXECUTION PIPELINE ---
            cmd = []
            
            if os.name == 'posix':
                prefs = common.get_prefs(context)
                wine_raw = getattr(prefs, 'wine', '')
                
                # Safely default to 'wine' if field is empty, just a period, or the Blender double slash
                if not wine_raw or wine_raw.strip() in ('.', '//', ''):
                    wine_exe = 'wine'
                else:
                    wine_exe = str(bpy.path.abspath(wine_raw))
                cmd.append(wine_exe)
                
            cmd.append(vhacd_path)
            
            # WE PASS ONLY THE BARE RELATIVE FILENAMES AND EXECUTE FROM CWD
            cmd.extend([
                '--input', obj_name,
                '--resolution', str(self.resolution),
                '--depth', str(self.depth),
                '--concavity', f"{self.concavity:g}",
                '--planeDownsampling', str(self.planeDownsampling),
                '--convexhullDownsampling', str(self.convexhullDownsampling),
                '--alpha', f"{self.alpha:g}",
                '--beta', f"{self.beta:g}",
                '--gamma', f"{self.gamma:g}",
                '--pca', '1' if self.pca else '0',
                '--mode', '1' if self.mode == 'TETRAHEDRON' else '0',
                '--maxNumVerticesPerCH', str(self.maxNumVerticesPerCH),
                '--minVolumePerCH', f"{self.minVolumePerCH:g}",
                '--output', out_name,
                '--log', log_name
            ])

            print(f'[SourceOps] Running V-HACD Command: {" ".join(cmd)}')
            print(f'[SourceOps] Working Directory (CWD): {data_path}\n')
            
            try:
                # Execution with CWD ensures Windows executable doesn't trip on Linux absolute paths!
                vhacd_process = Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True, cwd=data_path)
                for line in vhacd_process.stdout:
                    print(line, end='')
                vhacd_process.wait()
                
                if vhacd_process.returncode != 0:
                    print(f"\n[SourceOps ERROR] V-HACD exited with critical code {vhacd_process.returncode}")
            except Exception as e:
                print(f"\n[SourceOps ERROR] Failed to run V-HACD executable: {e}")
                self.report({'ERROR'}, f"Failed to execute V-HACD: {e}")
                continue

            if not os_path.exists(out_full_path):
                print(f"[SourceOps ERROR] V-HACD failed to generate the output file: {out_full_path}")
                continue

            try:
                bpy.ops.import_scene.x3d(filepath=out_full_path, axis_forward='Y', axis_up='Z')
            except:
                try:
                    bpy.ops.import_scene.vrml(filepath=out_full_path)
                except:
                    self.report({'ERROR'}, 'Failed to import V-HACD output. Ensure X3D or VRML importer is enabled.')
                    continue
            
            imported = bpy.context.selected_objects
            new_objects.extend(imported)

            # --- TARGET COLLECTION LOGIC ---
            target_col = None
            if self.collection_mode == 'COLLISION_MODELS':
                col_name = "Collision Models"
                if col_name not in bpy.data.collections:
                    target_col = bpy.data.collections.new(col_name)
                    bpy.context.scene.collection.children.link(target_col)
                else:
                    target_col = bpy.data.collections[col_name]
                    
            elif self.collection_mode == 'SAME_AS_PARENT':
                # If the object is in a specific collection
                if ob.users_collection:
                    source_col = ob.users_collection[0]
                    col_name = f"{source_col.name} COL"
                    
                    # Find the parent of the source collection so we can put it ALONGSIDE it (not inside)
                    parent_of_source = bpy.context.scene.collection
                    for c in bpy.data.collections:
                        if source_col.name in c.children.keys():
                            parent_of_source = c
                            break
                else:
                    # Fallback if the object is just loose in the master Scene Collection
                    source_col = None
                    col_name = "Collision Models"
                    parent_of_source = bpy.context.scene.collection
                
                if col_name not in bpy.data.collections:
                    target_col = bpy.data.collections.new(col_name)
                else:
                    target_col = bpy.data.collections[col_name]
                    
                # Make sure it's correctly linked in the right parent level
                if target_col.name not in parent_of_source.children.keys():
                    parent_of_source.children.link(target_col)

                # --- REORDER MAGIC ---
                # This forces the new collection to show up IMMEDIATELY beneath the source collection
                if source_col:
                    current_children = list(parent_of_source.children)
                    if source_col in current_children and target_col in current_children:
                        current_children.remove(target_col)
                        source_idx = current_children.index(source_col)
                        current_children.insert(source_idx + 1, target_col)
                        
                        # Unlink and relink everything to enforce the new order visually in the Outliner
                        for col in list(parent_of_source.children):
                            parent_of_source.children.unlink(col)
                        for col in current_children:
                            parent_of_source.children.link(col)

            name_template = '?_hull_#'
            for index, hull in enumerate(imported):
                hull.select_set(False)
                hull.matrix_basis = post_matrix
                name = name_template.replace('?', ob.name, 1)
                name = name.replace('#', str(index + 1), 1)
                if name == name_template:
                    name += str(index + 1)
                hull.name = name
                hull.data.name = name
                hull.display_type = 'WIRE'
                
                # MOVE OBJECT TO TARGET COLLECTION (IF NOT 'NONE')
                if target_col:
                    if target_col.name not in[c.name for c in hull.users_collection]:
                        target_col.objects.link(hull)
                    for old_col in hull.users_collection:
                        if old_col != target_col:
                            old_col.objects.unlink(hull)

        if len(new_objects) < 1:
            for ob in selected:
                ob.select_set(True)
            self.report({'WARNING'}, 'No meshes to process! Check the System Console for V-HACD errors.')
            return {'CANCELLED'}

        for ob in new_objects:
            ob.select_set(True)
            
        # --- NEW: AUTOMATICALLY SHADE SMOOTH ALL NEW HULLS ---
        if new_objects:
            bpy.context.view_layer.objects.active = new_objects[0]
            bpy.ops.object.shade_smooth()

        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=400)

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.label(text='Pre-Processing Options:')
        col.prop(self, 'remove_doubles')
        col.prop(self, 'apply_transforms')

        layout.separator()
        col = layout.column()
        col.label(text='V-HACD Parameters:')
        col.prop(self, 'resolution')
        col.prop(self, 'depth')
        col.prop(self, 'concavity')
        col.prop(self, 'planeDownsampling')
        col.prop(self, 'convexhullDownsampling')
        row = col.row()
        row.prop(self, 'alpha')
        row.prop(self, 'beta')
        row.prop(self, 'gamma')
        col.prop(self, 'pca')
        col.prop(self, 'mode')
        col.prop(self, 'maxNumVerticesPerCH')
        col.prop(self, 'minVolumePerCH')

        # NEW COLLECTION OPTIONS DRAWN AS RADIO BUTTONS
        layout.separator()
        col = layout.column()
        col.label(text='Collection Options:')
        col.prop(self, 'collection_mode', expand=True)

        layout.separator()
        col = layout.column()
        col.label(text='WARNING:', icon='ERROR')
        col.label(text='  Processing can take several minutes per object!')
        col.label(text='  ALL selected objects will be processed sequentially!')
        col.label(text='  See Console Window for progress...')


def menu_func_object(self, context):
    self.layout.operator(VHACD_OT_VHACD.bl_idname)


classes = (
    VHACD_OT_RenameHulls,
    VHACD_OT_SelectHulls,
    VHACD_OT_VHACD,
)


def register():
    for c in classes:
        bpy.utils.register_class(c)
    bpy.types.VIEW3D_MT_object.append(menu_func_object)


def unregister():
    bpy.types.VIEW3D_MT_object.remove(menu_func_object)
    for c in reversed(classes):
        bpy.utils.unregister_class(c)


if __name__ == '__main__':
    register()