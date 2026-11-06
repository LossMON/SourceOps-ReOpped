import bpy
import os
from . import utils
from . import props
from . import icons
from . import ops
from . import ui
from .vhacd_collision import vhacd

try:
    from .texture_combiner import atlas_texture_converter
    has_combiner = True
except Exception as e:
    print(f"[SourceOps WARNING] Could not load texture combiner: {e}")
    has_combiner = False

try:
    from . import io_scene_x3d
    has_x3d = True
except Exception as e:
    print(f"[SourceOps WARNING] Could not find 'io_scene_x3d': {e}")
    has_x3d = False

def auto_restore():
    try:
        filepath = utils.backup.filepath()
        if os.path.exists(filepath):
            utils.backup.restore(filepath)
            print("[SourceOps] Auto-restored preferences and paths from backup.")
    except Exception as e:
        print(f"[SourceOps ERROR] Auto-restore failed: {e}")
    return None

def register():
    props.register()
    icons.register()
    ops.register()
    ui.register()
    vhacd.register()
    if has_combiner:
        atlas_texture_converter.register()
    
    if has_x3d:
        io_scene_x3d.register()
    
    bpy.app.timers.register(auto_restore, first_interval=0.5)

def unregister():
    if has_combiner:
        atlas_texture_converter.unregister()
    if has_x3d:
        io_scene_x3d.unregister()
        
    vhacd.unregister()
    ui.unregister()
    ops.unregister()
    props.unregister()
    icons.unregister()