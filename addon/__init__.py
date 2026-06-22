import bpy
import os
from . import utils
from . import props
from . import icons
from . import ops
from . import ui
from .vhacd_collision import vhacd

# Try to load the newly unzipped X3D Importer natively
try:
    from . import io_scene_x3d
    has_x3d = True
except ImportError as e:
    print(f"[SourceOps WARNING] Could not find the 'io_scene_x3d' folder. Did you rename it? ({e})")
    has_x3d = False

def auto_restore():
    try:
        filepath = utils.backup.filepath()
        if os.path.exists(filepath):
            utils.backup.restore(filepath)
            print("[SourceOps] Auto-restored preferences and paths from backup.")
    except Exception as e:
        print(f"[SourceOps ERROR] Auto-restore failed: {e}")
    return None # Prevents timer from repeating

def register():
    props.register()
    icons.register()
    ops.register()
    ui.register()
    vhacd.register() # Registers the native V-HACD integration
    
    # Silently register the X3D importer in the background so V-HACD can use it
    if has_x3d:
        io_scene_x3d.register()
    
    # Runs the auto-restore a half second after Blender boots up
    bpy.app.timers.register(auto_restore, first_interval=0.5)

def unregister():
    if has_x3d:
        io_scene_x3d.unregister()
        
    vhacd.unregister() # Unregisters V-HACD
    ui.unregister()
    ops.unregister()
    props.unregister()
    icons.unregister()