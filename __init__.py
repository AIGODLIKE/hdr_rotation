from . import key, ops


def register():
    ops.register()
    key.register()


def unregister():
    ops.unregister()
    key.unregister()
