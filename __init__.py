import bpy

from . import key, ops

bl_info = {
    "name": "Hdr Rotation",
    "description": "Rotation HDR by Shift+Right Drag in 3D View",
    "author": "AIGODLIKE Community(小萌新)",
    "version": (1, 0, 4),
    "blender": (4, 2, 0),
    "location": "3D View",
    "support": "COMMUNITY",
    "category": "幻之境",
}


class RotationPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__


def register():
    ops.register()
    key.register()
    bpy.utils.register_class(RotationPreferences)


def unregister():
    ops.unregister()
    key.unregister()
    bpy.utils.unregister_class(RotationPreferences)
