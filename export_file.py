from __future__ import annotations
import math
import os
import shutil
import sys
from typing import Optional, Union, Any

import utility
from math_objects import Vector3, Quaternion, Euler
from armature_objects import Armature, Bone, ArmatureFrame, ArmatureAnimation, DisplayVoxel, VisibleBones
# from minecraft import AecArmorStandPair
from utility import tuple_to_m_list


class ArmaturePreparer:
    """Prepares an armature for export.

    Gets a raw armature and then figures out how the information from the visible bones should be used to scale,
    """

    def __init__(self, original_armature: Armature, visible_bone_object: VisibleBones, translation_fix_bones: set[str]):
        """bruh"""

        self.original_armature = original_armature.copy()
        self.animated_armature = None

        self.keep = translation_fix_bones.copy()
        self.positional = translation_fix_bones.copy()
        self.rotational = set()

        k, p = visible_bone_object.format()
        self.keep.update(k)
        # self.positional.update(p)

    def original_armature_pruned(self) -> Armature:
        """Return a pruned version of the armature without any animation."""
        new_armature = self.original_armature.copy()
        new_armature.prune_bones_filtered(self.keep, self.positional, True)

        return new_armature

    def per_frame(self, frame: ArmatureFrame) -> Armature:
        self.animated_armature = self.original_armature.copy()
        self.animated_armature.import_frame(frame)
        # copy rotation if parent is not in keep

        self.animated_armature.prune_bones_filtered(self.keep, False, True)

        return self.animated_armature


# class MinecraftExporter:
#     def __init__(self, function_directory: str) -> None:
#         """Initialize a new MainConverter class.
#             WARNING: This will remove all items in the directory
#           - function_directory: A string of the function directory (absolute).
#         """
#
#         self.function_directory = function_directory
#         self.scale = 1.0
#         self.current_armature = None
#
#         self._aec_stand_pairs = {}
#         self._global_offset_fix = Vector3(0.0, 0.0, 0.0)
#         self._model_rotation = Quaternion(0.0, 0.0, 0.0, 1.0)
#
#         # Ensure that the directory points into a Minecraft datapack folder.
#         if 'functions' in function_directory and 'datapacks' in function_directory \
#                 and 'functions' not in function_directory[-10:len(function_directory)]:
#             try:
#                 shutil.rmtree(function_directory)
#             except FileNotFoundError:
#                 pass
#         else:
#             print('Directory name does not include \'functions\' or \'datapacks\' '
#                   'or does not contain a folder following \'functions\' folder!'
#                   ' Are you sure this is the right directory?')
#             sys.exit()

class BedrockJsonHeader:
    def __init__(self):
        pass


class BedrockModelHeader(BedrockJsonHeader):
    def __init__(self, format_version: str, identifier: str, texture_size: tuple[int, int],
                 visible_bounds_size: tuple[int, int] = (1, 2),
                 visible_bounds_offset: Vector3 = Vector3(0.0, 0.0, 0.0)):
        super().__init__()

        self.format_version = format_version
        self.identifier = identifier
        self.texture_size = texture_size
        self.visible_bounds_size = visible_bounds_size
        self.visible_bounds_offset = visible_bounds_offset

    def start(self):
        return ('{'
                '\n"format_version": "' + self.format_version + '",'
                                                                '\n"minecraft:geometry": ['
                                                                '\n{'
                                                                '\n"description": {'
                                                                '\n"identifier": "' + self.identifier + '",'
                                                                                                        '\n"texture_width": ' + str(
            self.texture_size[0]) + ','
                                    '\n"texture_height": ' + str(self.texture_size[1]) + ','
                                                                                         '\n"visible_bounds_width": ' + str(
            self.visible_bounds_size[0]) + ','
                                           '\n"visible_bounds_height": ' + str(self.visible_bounds_size[0]) + ','
                                                                                                              '\n"visible_bounds_offset": ' + utility.tuple_to_m_list(
            self.visible_bounds_offset.to_tuple()) + ''
                                                     '\n},'
                                                     '\n"bones": [')

    def end(self):
        return '\n			]\n		}\n	]\n}'


class BedrockModelExporter:
    ap: Optional[ArmaturePreparer]
    model: Optional[Armature]
    fps: Optional[Union[float, int]]
    animation: Optional[dict[str: list[tuple[float, Vector3, Quaternion]]]]
    animation_length: Optional[Union[float, int]]
    visible_bones: Optional[set[str]]
    translation_fix_bones: Optional[set]
    pre_rotate: Optional[set[str]]

    def __init__(self):
        self.ap = None
        self.model = None
        self.fps = None
        self.animation = None
        self.animation_length = None
        self.visible_bones = None
        self.translation_fix_bones = None
        self.pre_rotate = None

    def create_geo_model(self, armature: Armature, visible_bones: VisibleBones,
                         translation_fix_bones: Optional[set[str]]):
        self.translation_fix_bones = translation_fix_bones

        self.ap = ArmaturePreparer(armature, visible_bones, self.translation_fix_bones)

        self.model = self.ap.original_armature_pruned()

        self.pre_rotate = visible_bones.pre_rotate

        # first loop change original size to model size (this is so the elements look right in blockbench)
        for bone_name in self.model.bones:
            self.model.bones[bone_name].original_size = self.model.bones[bone_name].model_size.copy()

        # then put every element at the correct global position
        for bone_name in self.model.bones:
            self.model.bones[bone_name].delocalize(True, False)

    def write_geo_model(self, path: str, file_name: str, model_header: BedrockModelHeader):
        # third round, probably wouldn't have to if we dfsed
        complete_path = os.path.join(path, file_name + ".geo.json")
        open(complete_path, 'w').close()
        g = open(complete_path, "a", encoding="utf-8")
        # Write the header
        g.write(model_header.start())

        first = True

        for bone_name in self.model.bones:
            current_bone = self.model.bones[bone_name]
            if first:
                first = False
            else:
                g.write(',')

            g.write('{')
            name = current_bone.name
            g.write('"name": "' + name + '",')
            if current_bone.parent is not None:
                parent = current_bone.parent.name
                g.write('"parent": "' + parent + '",')

                parent_rot_reverse = current_bone.parent.model_size_to_original.conjugate()
            else:
                parent_rot_reverse = Quaternion()
            pivot = current_bone.pivot_offset + current_bone.pivot
            g.write('"pivot": ' + tuple_to_m_list(pivot.to_tuple()) + ',')

            # pre_rotate
            if bone_name in self.pre_rotate:
                rotation = Euler('zyx').set_from_quaternion(
                    current_bone.model_size_to_original.parented(parent_rot_reverse))
                rotation.y *= -1
                rotation.z *= -1
            else:
                rotation = Euler('zyx')
            g.write('"rotation": ' + tuple_to_m_list(rotation.to_tuple()))

            cube_info = current_bone.bone_display

            if cube_info is not None:
                g.write(',\n"cubes": [')

                if type(cube_info) is not DisplayVoxel:
                    cube_offset = Vector3(0.05, 0.05, 0.05)
                    cube_size = current_bone.model_size
                else:
                    cube_offset = cube_info.offset
                    cube_size = cube_info.size

                origin = pivot + cube_offset
                size = cube_size
                g.write('{"origin": ' + tuple_to_m_list(origin.to_tuple()) + ', "size": ' + tuple_to_m_list(
                    size.to_tuple()) + ', "uv": [0, 0]}')
                g.write(']')

            g.write('}')

        g.write(model_header.end())

    def create_animation(self, aa: ArmatureAnimation):
        self.animation = {}
        self.fps = aa.fps
        self.animation_length = len(aa.frames) // self.fps

        for i, frame in enumerate(aa.frames):
            armature_animated = self.ap.per_frame(frame)
            frame_time = i / self.fps

            def dfs(bone: Bone):
                if not bone.name[0:9] == 'mcf_root_':
                    if bone.name not in self.pre_rotate:
                        if bone.parent is not None:
                            parent_rot_reverse = bone.parent.model_size_to_original.conjugate()
                        else:
                            parent_rot_reverse = Quaternion()
                        pre_rotation = bone.model_size_to_original.parented(parent_rot_reverse)
                    else:
                        pre_rotation = Quaternion()

                    try:
                        rotation = frame.bone_channels[bone.parent.name].rotation.parented(pre_rotation)
                    except KeyError:
                        rotation = Quaternion()

                    if bone.name in self.translation_fix_bones:
                        position = bone.animation_size_delta
                    else:
                        position = Vector3(0.0, 0.0, 0.0)

                    if i == 0:
                        self.animation[bone.name] = []
                    self.animation[bone.name].append((frame_time, position, rotation))
                for child in bone.children:
                    dfs(child)

            dfs(armature_animated.root)

    def write_animation(self, path: str, file_name: str, animation_name: str):

        complete_path = os.path.join(path, file_name + ".json")
        open(complete_path, 'w').close()
        g = open(complete_path, "a", encoding="utf-8")
        # Write the header
        g.write('{'
                '\n"format_version": "1.8.0",'
                '\n"animations": '
                '{\n"' + animation_name + '": {\n"animation_length": ' + str(
            math.ceil(self.animation_length)) + ',\n"bones": {\n')

        l_1 = len(self.animation) - 1
        for i, bone_name in enumerate(self.animation):
            g.write('"' + bone_name + '": {\n')

            g.write('"position": {\n')
            l_2 = len(self.animation[bone_name]) - 1

            for j, fixed_frame in enumerate(self.animation[bone_name]):

                position = fixed_frame[1].copy()
                position.k *= -1

                if j == l_2:
                    end = '\n'
                else:
                    end = ',\n'
                g.write(
                    '"' + '{:.2f}'.format(fixed_frame[0]) + '": ' + tuple_to_m_list((16 * position).to_tuple()) + end)
            g.write('},')

            g.write('"rotation": {\n')
            l_2 = len(self.animation[bone_name]) - 1

            prev_x = None
            prev_y = None
            prev_z = None

            bias_x = 0.0
            bias_y = 0.0
            bias_z = 0.0

            for j, fixed_frame in enumerate(self.animation[bone_name]):

                rotator = fixed_frame[2].copy()
                rotation = Euler('zyx').set_from_quaternion(rotator)
                rotation.y *= -1
                rotation.z *= -1
                rotator = Quaternion().set_from_euler(rotation)

                inner_vector = rotator.extract_vector()
                inner_vector.rotate_by_quaternion(self.ap.original_armature.bones[bone_name].model_size_to_original)
                rotator.replace_vector(inner_vector)

                bl_original = self.model.bones[bone_name].bone_lock
                bl = bl_original.copy()

                bl_i = 0
                if len(bl_original) != 0:
                    if 'x' not in bl:
                        bl.append('x')
                    if 'y' not in bl:
                        bl.append('y')
                    if 'z' not in bl:
                        bl.append('z')

                    e_order = ''.join(reversed(bl))
                    euler_copy = Euler(e_order).set_from_quaternion(rotator)

                    while bl_i < len(bl_original):
                        if bl_original[bl_i] == 'x':
                            euler_copy.x = 0.0
                        elif bl_original[bl_i] == 'y':
                            euler_copy.y = 0.0
                        elif bl_original[bl_i] == 'z':
                            euler_copy.z = 0.0
                        else:
                            euler_copy = Euler('xyz')
                        rotator = Quaternion().set_from_euler(euler_copy)
                        bl_i += 1

                rotation = Euler('zyx').set_from_quaternion(rotator)
                rotation.x += bias_x
                rotation.y += bias_y
                rotation.z += bias_z

                if prev_x is not None and abs(prev_x - rotation.x) > 180:
                    if prev_x < bias_x < rotation.x:
                        rotation.x -= 360.0
                        bias_x -= 360.0
                    elif prev_x > bias_x > rotation.x:
                        rotation.x += 360.0
                        bias_x += 360.0
                prev_x = rotation.x

                if prev_x is not None and abs(prev_x - rotation.x) > 180:
                    if prev_x < bias_x < rotation.x:
                        rotation.x -= 360.0
                        bias_x -= 360.0
                    elif prev_x > bias_x > rotation.x:
                        rotation.x += 360.0
                        bias_x += 360.0
                prev_x = rotation.x

                if prev_y is not None and abs(prev_y - rotation.y) > 180:
                    if prev_y < bias_y < rotation.y:
                        rotation.y -= 360.0
                        bias_y -= 360.0
                    elif prev_y > bias_y > rotation.y:
                        rotation.y += 360.0
                        bias_y += 360.0
                prev_y = rotation.y

                if prev_z is not None and abs(prev_z - rotation.z) > 180:
                    if prev_z < bias_z < rotation.z:
                        rotation.z -= 360.0
                        bias_z -= 360.0
                    elif prev_z > bias_z > rotation.z:
                        rotation.z += 360.0
                        bias_z += 360.0
                prev_z = rotation.z


                if j == l_2:
                    end = '\n'
                else:
                    end = ',\n'
                g.write('"' + '{:.2f}'.format(fixed_frame[0]) + '": ' + tuple_to_m_list(rotation.to_tuple()) + end)

            if i == l_1:
                end = '\n'
            else:
                end = ',\n'
            g.write('}\n}' + end)
        g.write('}\n}\n}\n}')
        g.close()
