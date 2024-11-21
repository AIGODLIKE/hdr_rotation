import ast
import re

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

    def draw(self, context):
        from .key import draw_keymap
        column = self.layout.column()
        for text in ["In 3D viewport (both renderd or material preview mode)",
                     "Shift + Right-Drag on empty space",
                     "you can rotate the enviroment texture to preview shaders and lighting more practical and faster",
                     "When dragging on objects, moves 3D cursor"
                     ]:
            column.label(text=text)
        column.separator()
        column.label(text="Keymap:")
        draw_keymap(column)


def get_language_list() -> list:
    """
    Traceback (most recent call last):
  File "<blender_console>", line 1, in <module>
TypeError: bpy_struct: item.attr = val: enum "a" not found in ('DEFAULT', 'en_US', 'es', 'ja_JP', 'sk_SK', 'vi_VN', 'zh_HANS', 'ar_EG', 'de_DE', 'fr_FR', 'it_IT', 'ko_KR', 'pt_BR', 'pt_PT', 'ru_RU', 'uk_UA', 'zh_TW', 'ab', 'ca_AD', 'cs_CZ', 'eo', 'eu_EU', 'fa_IR', 'ha', 'he_IL', 'hi_IN', 'hr_HR', 'hu_HU', 'id_ID', 'ky_KG', 'nl_NL', 'pl_PL', 'sr_RS', 'sr_RS@latin', 'sv_SE', 'th_TH', 'tr_TR')
    """
    try:
        bpy.context.preferences.view.language = ""
    except TypeError as e:
        matches = re.findall(r'\(([^()]*)\)', e.args[-1])
        return ast.literal_eval(f"({matches[-1]})")


def register():
    ops.register()
    key.register()
    bpy.utils.register_class(RotationPreferences)
    language = "ZH_CN" if "ZH_CN" in get_language_list() else "zh_HANS"
    bpy.app.translations.register("hdr_rotation", {language: {
        ("*", "HDR Rotation"): "HDR旋转",
        ("*", "In 3D viewport (both renderd or material preview mode)"): "在3D视图(渲染或材质预览模式)",
        ("*", "Shift + Right-Drag on empty space"): "Shift+右键拖动 空白处",
        ("*", "you can rotate the enviroment texture to preview shaders and lighting more practical and faster",
         ): "您可以旋转环境纹理，以便更实用、更快速地预览着色器和照明效果",
        ("*",
         "When dragging on objects, moves 3D cursor",): "在对象上拖动时,会移动3D游标",
        ("*", "Keymap:"): "快捷键:",
    }})


def unregister():
    ops.unregister()
    key.unregister()
    bpy.utils.unregister_class(RotationPreferences)
    bpy.app.translations.unregister("hdr_rotation")
