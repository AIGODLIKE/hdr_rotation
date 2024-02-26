from . import key, ops

bl_info = {
    "name": "Hdr Rotation",
    "author": "AIGODLIKE Community：小萌新",
    "version": (1, 2, 3),
    "blender": (4, 0, 0),
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
