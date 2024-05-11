from math import degrees, radians

import bpy
from bpy.types import Operator


def get_node(node_tree=None, match_type=None) -> [bpy.types.Node, ...]:
    if match_type is None:
        match_type = {'GROUP', 'MAPPING'}

    res = []
    if node_tree is None:
        return res
    else:
        for node in node_tree.nodes:
            if node.type in match_type:
                if node.type == 'GROUP':
                    group = get_node(node.node_tree)
                    if len(group) != 0:
                        res = res + group
                else:
                    res.append(node)
        return res


def modal_exit():
    bpy.context.window.cursor_set("DEFAULT")
    bpy.context.area.header_text_set(None)


def check_modal_exit(event):
    return event.type == "RIGHTMOUSE" and event.value == "RELEASE"


class HdrRotationOperator(Operator):
    bl_idname = 'hdr.rotation'
    bl_label = 'HDR Rotation'
    bl_options = {'UNDO'}

    def __init__(self):
        shading = self.shading = bpy.context.space_data.shading
        is_material = (shading.type == 'MATERIAL' and shading.use_scene_world)
        is_rendered = (shading.type == 'RENDERED' and shading.use_scene_world_render)

        self.start_rotation_angle = None
        self.start_x = None
        self.nodes = get_node(node_tree=bpy.context.scene.world.node_tree)
        self.is_rotation_hdr = self.shading.type in {'MATERIAL', 'RENDERED'}
        self.use_scene_world = is_material or is_rendered

        self.inputs_list = []
        self.vector_list = []
        self.rotation = None  # 调用的旋转方法,用于替换执行方法优化性能

    def init_node(self, context):
        for node in context.scene.world.node_tree.nodes:
            if node.type == 'GROUP':
                for inputs in node.inputs:
                    if inputs.name in ['Rotation'] and inputs.bl_label in ['Vector']:
                        self.vector_list.append(inputs)
                    if inputs.name in ['HDR旋转', 'Z旋转']:
                        self.inputs_list.append(inputs)

    def get_init_node_rotation(self) -> float:
        return self.nodes[0].inputs[2].default_value[2]

    def invoke(self, context, event):
        self.start_x = event.mouse_region_x

        if context.area and context.area.type == "VIEW_3D":
            if self.use_scene_world:
                if len(self.nodes) == 0:
                    self.report({'WARNING'}, "World Environment Not Mapping Node,Please add a Mapping node")
                    return {'FINISHED', 'PASS_THROUGH'}
                self.init_node(context)
                self.rotation = self.rotation_scene_world_shader
                self.start_rotation_angle = degrees(self.get_init_node_rotation())
            else:
                self.start_rotation_angle = degrees(self.shading.studiolight_rotate_z)
                self.rotation = self.rotation_studio_light

            if self.is_rotation_hdr:  # 旋转HDR
                context.window_manager.modal_handler_add(self)
                bpy.context.window.cursor_set("MOVE_X")
                return {'RUNNING_MODAL'}

        return {'FINISHED', 'PASS_THROUGH'}

    def modal(self, context, event):
        if check_modal_exit(event):
            modal_exit()
            return {'FINISHED'}
        elif event.type == "ESC":
            modal_exit()
            return {'CANCELLED'}

        x = event.mouse_region_x

        factor = 0.1
        value = (x - self.start_x) * factor
        value = self.start_rotation_angle + value
        while value > 180:
            value -= 360
        while value < -180:
            value += 360
        self.rotation(radians(value))
        return {'RUNNING_MODAL'}

    def rotation_scene_world_shader(self, hdr_radians) -> None:
        for node in self.nodes:
            node.inputs[2].default_value[2] = hdr_radians

        for node in self.inputs_list:
            node.default_value = hdr_radians
        for node in self.vector_list:
            node.default_value[2] = hdr_radians

    def rotation_studio_light(self, studio_radians) -> None:
        self.shading.studiolight_rotate_z = studio_radians


def register():
    bpy.utils.register_class(HdrRotationOperator)


def unregister():
    bpy.utils.unregister_class(HdrRotationOperator)
