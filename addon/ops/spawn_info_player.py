import bpy
import os

class SOURCEOPS_OT_SpawnInfoPlayer(bpy.types.Operator):
    bl_idname = 'sourceops.spawn_info_player'
    bl_options = {'REGISTER', 'UNDO'}
    bl_label = 'Spawn Info Player'
    bl_description = 'Spawns an info_playerstart reference model into the scene for scale'

    def execute(self, context):
        # Find the root addon directory based on this script's location
        ops_dir = os.path.dirname(os.path.abspath(__file__))
        addon_dir = os.path.dirname(ops_dir)
        
        # Path to the GLB file
        glb_path = os.path.join(addon_dir, 'glb', 'info_playerstart.glb')
        
        if not os.path.exists(glb_path):
            self.report({'ERROR'}, f"Could not find {glb_path}. Make sure the glb folder and file exist!")
            return {'CANCELLED'}
            
        try:
            # Import the GLB file
            bpy.ops.import_scene.gltf(filepath=glb_path)
            self.report({'INFO'}, "Spawned info_player_start reference")
        except Exception as e:
            self.report({'ERROR'}, f"Failed to spawn info_player_start: {e}")
            return {'CANCELLED'}
            
        return {'FINISHED'}