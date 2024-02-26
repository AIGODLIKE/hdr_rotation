from math import degrees, radians

import bpy
from bpy.props import IntProperty, FloatProperty
from bpy.types import Operator


def get_node(node_tree=None, match_type=None):
    """
    输入一个节点树，反回一个列表
    """
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


class HdrRotationOperator(Operator):
    """hdr_rotation"""
    bl_idname = 'hdr.rotation'
    bl_label = 'HDR Rotation'
    bl_options = {'UNDO'}  # 'REGISTER',
    bl_description = """
    SHIFT 右键旋转HDR
    如果在渲染模式或是预览模式，测使用HDR旋转

    如果是在实体模式，则设置3D游标"""

    first_mouse_x: IntProperty()
    first_value: FloatProperty()

    def modal(self, context, event):
        shading = context.space_data.shading
        overlay = context.space_data.overlay

        if event.type == "RIGHTMOUSE" and event.value == "RELEASE":
            context.window.cursor_set("DEFAULT")
            context.area.header_text_set(None)
            return {'FINISHED'}

        elif event.type == "ESC":
            context.window.cursor_set("DEFAULT")
            context.area.header_text_set(None)
            return {'CANCELLED'}

        if shading.type in {'MATERIAL', 'RENDERED'}:  # 旋转HDR
            bpy.context.window.cursor_set("MOVE_X")

            x, y = self.mouse_region(context, event, )

            factor = 0.25
            value = (x - self.startValue) * factor  # self.x
            value = self.startRotation + value

            if value >= 180:
                if value // 360 >= 1:  # 超过一圈
                    print(f'{value} 超过一圈')
                    rotation_value = -180 + value % 360  #
                else:
                    rotation_value = -180 + value % 180  #
            elif value <= -180:
                if value // -360 >= 1:  # 超过一圈
                    print('超过一圈')
                    rotation_value = 180 + (value % -360)
                else:
                    print(f'{value} 超过一圈')
                    rotation_value = 180 + (value % -180)
            else:
                rotation_value = value

            if self.use_scene_world:  # 用世界HDR
                inputs_list = []
                vector_list = []
                for node in context.scene.world.node_tree.nodes:
                    if node.type == 'GROUP':
                        for inputs in node.inputs:
                            if inputs.name in ['Rotation'] and inputs.bl_label in ['Vector']:
                                vector_list.append(inputs)
                            if inputs.name in ['HDR旋转', 'Z旋转']:
                                inputs_list.append(inputs)

                for node in self.nodes:
                    node.inputs[2].default_value[2] = radians(rotation_value)

                for node in inputs_list:
                    node.default_value = radians(rotation_value)
                for node in vector_list:
                    node.default_value[2] = radians(rotation_value)

                context.area.header_text_set('旋转世界HDR 角度:%s     控制节点数: %s' % (
                    int(rotation_value), (len(inputs_list) + len(inputs_list) + len(vector_list))))
            else:  # 用预览的功能来做

                # print(f'{self.startRotation} 用自带的HDR预览')
                context.area.spaces[0].shading.studiolight_rotate_z = radians(rotation_value)

                context.area.header_text_set(
                    f'{value} 旋转预览HDR 角度:{rotation_value} 鼠标区域{event.mouse_region_x, event.mouse_region_y,}  鼠标{event.mouse_x, event.mouse_x}     高宽{context.area.height, context.area.width,}')

            return {'RUNNING_MODAL'}

        else:
            context.area.header_text_set(f'移动游标 {event.mouse_x, event.mouse_y}')
            bpy.ops.transform.translate('INVOKE_REGION_PREVIEW',
                                        cursor_transform=True,
                                        release_confirm=True)

            return {'FINISHED'}

    def invoke(self, context, event):
        shading = context.space_data.shading
        self.startValue = event.mouse_x

        self.use_scene_world = (shading.type == 'MATERIAL' and shading.use_scene_world) or (
                shading.type == 'RENDERED' and shading.use_scene_world_render)

        if context.area and context.area.type == "VIEW_3D":
            if self.use_scene_world:
                self.nodes = get_node(node_tree=context.scene.world.node_tree)
                if len(self.nodes) == 0:
                    self.report({'WARNING'}, "世界环境无映射节点")
                    return {'CANCELLED'}
                else:
                    self.startRotation = degrees(self.nodes[0].inputs[2].default_value[2])
            else:
                self.startRotation = degrees(shading.studiolight_rotate_z)

            # run modal
            context.window_manager.modal_handler_add(self)
            return {'RUNNING_MODAL'}

    def mouse_region(self, context, event, safe_area=100, mouse_data='MOUSE_DATA_REPEAT'):
        """
        X和Y的内容
        如果超过一次则
        context
        event
        :set_cursor_warp
        :safe_area
        :param mouse_data: Enumerator in ['MOUSE_DATA_REPEAT','MOUSE_DATA','MOUSE_XY'].
        {'MOUSE_DATA_REPEAT'}
        :type mouse_data: set EMM
        """

        if getattr(self, 'x_repeat', None) is None and getattr(self, 'y_repeat', None) is None:
            print('new')
            self.x_repeat = 0
            self.y_repeat = 0

        safe_mouse = 50

        mouse_xy = []

        def mouse_(area, mouse, repeat):
            if mouse > (area - safe_area):
                mouse_xy.append(safe_area + safe_mouse)
                repeat += 1
                print(f'++++ 鼠标当前位置{mouse}   安全边界{(area - safe_area)}')
                return repeat
            elif mouse < safe_area:
                mouse_xy.append(area - (safe_area + safe_mouse))
                repeat -= 1
                print(f'---- 鼠标当前位置{mouse}  安全边界{safe_area}')
                return repeat
            else:
                mouse_xy.append(mouse)
                return repeat

        self.x_repeat = mouse_(context.area.width, event.mouse_region_x, self.x_repeat)

        self.y_repeat = mouse_(context.area.height, event.mouse_region_y, self.y_repeat)

        repeat = [self.x_repeat, self.y_repeat]
        print(
            f"repeat{repeat},'  设置鼠标',{mouse_xy}  设置鼠标{context.area.x + mouse_xy[0]} {context.area.y + mouse_xy[1]}")
        context.window.cursor_warp(context.area.x + mouse_xy[0], context.area.y + mouse_xy[1])
        context.window.cursor_warp(context.area.x + mouse_xy[0], context.area.y + mouse_xy[1])

        if mouse_data == 'MOUSE_DATA_REPEAT':
            return [mouse_xy[0] + (context.area.width - safe_mouse * 2) * self.x_repeat,
                    mouse_xy[1] + (context.area.height - safe_mouse * 2) * self.y_repeat]
        elif mouse_data == 'MOUSE_DATA':
            return mouse_xy
        else:
            pass


def register():
    bpy.utils.register_class(HdrRotationOperator)


def unregister():
    bpy.utils.unregister_class(HdrRotationOperator)
