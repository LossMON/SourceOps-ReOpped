bl_info = {
    'name': 'SourceOps ReOpped',
    'author': 'bonjorno7, Almaas, Cabbage McGravel, CryptAlchemy, Gorange, Krystian, RED_EYE, SethTooQuick, Yonder, Blueberry_pie, Glad_BR',
    'description': 'REMAKED BY: LESSMAN (A more convenient alternative to Blender Source Tools)',
    'blender': (2, 83, 0),
    'version': (0, 8, 1),
    'location': '3D View > Sidebar',
    'category': 'Import-Export',
}

import bpy
import os
from . import addon

def auto_restore():
    """Runs automatically 0.5 seconds after Blender opens to restore your Games list!"""
    try:
        from .utils.backup import filepath, restore
        path = filepath()
        if os.path.exists(path):
            restore(path)
            print(f"[SourceOps] Auto-restored settings and Game Paths from backup.")
    except Exception as e:
        print(f"[SourceOps ERROR] Auto-restore failed: {e}")
    return None

def register():
    addon.register()
    # Schedule the auto-restore to happen as soon as Blender is ready
    bpy.app.timers.register(auto_restore, first_interval=0.5)

def unregister():
    addon.unregister()