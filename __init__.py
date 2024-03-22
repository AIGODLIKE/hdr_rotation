import bpy

from . import key, ops


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
