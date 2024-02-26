from . import key, ops

bl_info = {
    "name": "Hdr Rotation",
    "author": "AIGODLIKE Community：小萌新",
    "version": (1, 0, 0),
    "blender": (4, 1, 0),
    "location": "Hdr Rotation",
    "description": "",
    "warning": "",
    "category": "AIGODLIKE"
}


def register():
    ops.register()
    key.register()


def unregister():
    ops.unregister()
    key.unregister()
