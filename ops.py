from math import degrees, radians

import bpy
from bpy.props import IntProperty, FloatProperty
from bpy.types import Operator


def get_node(node_tree=None, match_type=None):
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


class HdrProperty:
    first_mouse_x: IntProperty()
    first_value: FloatProperty()
    x_repeat = 0
    y_repeat = 0

    @property
    def shading(self):
        return bpy.context.space_data.shading

    @property
    def is_rotation_hdr(self):
        return self.shading.type in {'MATERIAL', 'RENDERED'}

    @property
    def use_scene_world(self):
        shading = self.shading
        is_material = (shading.type == 'MATERIAL' and shading.use_scene_world)
        is_rendered = (shading.type == 'RENDERED' and shading.use_scene_world_render)
        return is_material or is_rendered

    @property
    def nodes(self):
        return get_node(node_tree=bpy.context.scene.world.node_tree)


class HdrRotationOperator(Operator, HdrProperty):
    bl_idname = 'hdr.rotation'
    bl_label = 'HDR Rotation'
    bl_options = {'UNDO'}

    def __init__(self):
        self.start_rotation = None
        self.start_value = None

    def invoke(self, context, event):
        shading = context.space_data.shading
        self.start_value = event.mouse_region_x

        if context.area and context.area.type == "VIEW_3D":
            if self.use_scene_world:
                if len(self.nodes) == 0:
                    self.report({'WARNING'}, "World Environment Not Map Node")
                    return {'FINISHED', 'PASS_THROUGH'}
                else:
                    self.start_rotation = degrees(self.nodes[0].inputs[2].default_value[2])
            else:
                self.start_rotation = degrees(shading.studiolight_rotate_z)
            if self.is_rotation_hdr:  # 旋转HDR
                context.window_manager.modal_handler_add(self)
                return {'RUNNING_MODAL'}
            else:
                return {'FINISHED', 'PASS_THROUGH'}

    def modal(self, context, event):
        if check_modal_exit(event):
            modal_exit()
            return {'FINISHED'}
        elif event.type == "ESC":
            modal_exit()
            return {'CANCELLED'}

        if self.is_rotation_hdr:  # 旋转HDR
            bpy.context.window.cursor_set("MOVE_X")
            x, y = self.mouse_region(context, event)

            factor = 0.25
            value = (x - self.start_value) * factor
            value = self.start_rotation + value

            if value >= 180:
                if value // 360 >= 1:  # 超过一圈
                    rotation_value = -180 + value % 360  #
                else:
                    rotation_value = -180 + value % 180  #
            elif value <= -180:
                if value // -360 >= 1:  # 超过一圈
                    rotation_value = 180 + (value % -360)
                else:
                    rotation_value = 180 + (value % -180)
            else:
                rotation_value = value

            if self.use_scene_world:  # 用世界HDR
                inputs_list = []
                vector_list = []
                for node in context.scene.world.node_tree.nodes:
                    if node.type == 'GROUP':
                        for inputs in node.inputs:
                            en = inputs.name in ['Rotation'] and inputs.bl_label in ['Vector']
                            cn = inputs.name in ['HDR旋转', 'Z旋转']
                            if en or cn:
                                vector_list.append(inputs)

                for node in self.nodes:
                    node.inputs[2].default_value[2] = radians(rotation_value)

                for node in inputs_list:
                    node.default_value = radians(rotation_value)
                for node in vector_list:
                    node.default_value[2] = radians(rotation_value)

                context.area.header_text_set('HDR Angle:%f.2     Node Count: %s' % (
                    int(rotation_value), (len(inputs_list) + len(inputs_list) + len(vector_list))))
            else:  # 用预览的功能来做
                context.area.spaces[0].shading.studiolight_rotate_z = radians(rotation_value)
                context.area.header_text_set(f'{value} Preview HDR Angle:{rotation_value}')
        return {'RUNNING_MODAL'}

    def mouse_region(self, context, event, safe_area=100, mouse_data='MOUSE_DATA_REPEAT'):
        safe_mouse = 10
        mouse_xy = []

        def mouse_(area, mouse, r):
            if mouse > (area - safe_area):
                mouse_xy.append(safe_area + safe_mouse)
                r += 1
                return r
            elif mouse < safe_area:
                mouse_xy.append(area - (safe_area + safe_mouse))
                r -= 1
                return r
            else:
                mouse_xy.append(mouse)
                return r

        self.x_repeat = mouse_(context.region.width, event.mouse_region_x, self.x_repeat)
        self.y_repeat = mouse_(context.region.height, event.mouse_region_y, self.y_repeat)

        context.window.cursor_warp(context.region.x + mouse_xy[0], context.region.y + mouse_xy[1])
        context.window.cursor_warp(context.region.x + mouse_xy[0], context.region.y + mouse_xy[1])
        context.window.cursor_warp(context.region.x + mouse_xy[0], context.region.y + mouse_xy[1])
        context.window.cursor_warp(context.region.x + mouse_xy[0], context.region.y + mouse_xy[1])

        if mouse_data == 'MOUSE_DATA_REPEAT':
            return [mouse_xy[0] + (context.region.width - (safe_mouse + safe_area) * 2) * self.x_repeat,
                    mouse_xy[1] + (context.region.height - (safe_mouse + safe_area) * 2) * self.y_repeat]
        elif mouse_data == 'MOUSE_DATA':
            return mouse_xy
        else:
            pass


def register():
    bpy.utils.register_class(HdrRotationOperator)


def unregister():
    bpy.utils.unregister_class(HdrRotationOperator)
