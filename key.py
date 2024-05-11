import bpy

from .ops import HdrRotationOperator

kc = bpy.context.window_manager.keyconfigs.addon  # 获取按键配置addon的
km = kc.keymaps.new(name='3D View', space_type='VIEW_3D', region_type='WINDOW')

kmi = None


def register():
    global kmi
    kmi = km.keymap_items.new(
        idname=HdrRotationOperator.bl_idname,
        type="RIGHTMOUSE",
        value="PRESS",
        ctrl=False,
        shift=True,
        alt=False,
    )


def unregister():
    km.keymap_items.remove(kmi)
