from __future__ import annotations
import math
import os
import shutil
import sys
from typing import Optional, Union, Any

import utility
from math_objects import Vector3, Quaternion, Euler
from armature import Armature, Bone, ArmatureFrame, ArmatureAnimation
# from minecraft import AecArmorStandPair
from utility import tuple_to_m_list

class VisibleBones:
    def __init__(self, armature: Armature):
        self.visible_bones = {}
        self.armature = armature

    def add_bones(self, bone_list: list[tuple[Optional[str], Optional[Union[Vector3, str]], Vector3, Vector3, Any]]):
        self.visible_bones

    def create_bones(self, bone_set: set):
        raise NotImplementedError

    def fill_bones(self):
        self.armature.bones
        pass




class DisplayVoxel:
    def __init__(self, offset: Vector3, size: Vector3):
        self.offset = offset
        self.size = size

    def copy(self):
        return DisplayVoxel(self.offset.copy(), self.size.copy())

class ArmaturePreparer:
    """Prepares an armature for export.

    Gets a raw armature and then figures out how the information from the visible bones should be used to scale,
    """

    def __init__(self, original_armature: Armature, visible_bone_object: VisibleBones, translation_fix_bones: set[str]):
        """bruh"""
        # visible_bones is in format:
        # parent_bone_name, child_bone_name, size, offset

        self.original_armature = original_armature.copy()
        self.animated_armature = None

        self.keep = translation_fix_bones.copy()
        self.positional = translation_fix_bones.copy()
        self.rotational = set()

        vector_child_count = 0

        # loop through all the defined visible_bones, fill in parent information where missing, and if child is
        # vector, create a new bone.

        # TODO: remove this, this is horrible
        visible_bones = visible_bone_object.visible_bones

        # Fill in missing bone information
        for i in range(len(visible_bones)):
            # give parent to parentless children
            if visible_bones[i][0] is None:
                visible_bones[i] = tuple((self.original_armature.bones[visible_bones[i][1]].parent.name, *visible_bones[i][1:]))

            if type(visible_bones[i][1]) is str:
                end_bone = self.original_armature.bones[visible_bones[i][1]]
                end_bone.additional_info = visible_bones[i][4]
                bone_name = visible_bones[i][1]
            else:
                # give child to childless parent
                bone_name = visible_bones[i][0] + '_vector_child_' + str(vector_child_count)
                end_bone = Bone(bone_name)
                end_bone.additional_info = visible_bones[i][4]
                self.original_armature.add_bone(end_bone, visible_bones[i][0])

                visible_bones[i] = (visible_bones[i][0], bone_name, *visible_bones[i][2:])

                vector_child_count += 1

        # figure out which bones to keep

        for visible_bone in visible_bones:
            bone_name = visible_bone[1]
            end_bone = self.original_armature.bones[bone_name]

            self.keep.add(bone_name)
            self.keep.add(visible_bone[0])

        def dfs_add_positional(bone: Bone):
            for child in bone.children:
                dfs_add_positional(child)

                if child.name in self.positional and bone.name not in self.keep:
                    self.positional.add(bone.name)

        dfs_add_positional(self.original_armature.root)

        # set size and offset of visible bones as needed
        for visible_bone in visible_bones:
            bone = self.original_armature.bones[visible_bone[1]]
            bone.model_size = visible_bone[2]
            bone.original_size.scale_to(visible_bone[2].magnitude())

            bone.pivot = visible_bone[3]
            bone.model_size_to_original = Quaternion().between_vectors(bone.model_size, bone.original_size)

    def original_armature_pruned(self) -> Armature:
        """Return a pruned version of the armature without any animation."""
        new_armature = self.original_armature.copy()
        new_armature.prune_bones_filtered(self.keep, self.positional, True)

        return new_armature

    def per_frame(self, frame: ArmatureFrame) -> Armature:
        self.animated_armature = self.original_armature.copy()
        self.animated_armature.import_frame(frame)
        # copy rotation if parent is not in keep

        self.animated_armature.prune_bones_filtered(self.keep, self.positional, True)

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
                 visible_bounds_size: tuple[int, int], visible_bounds_offset: Vector3):
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

    def __init__(self):
        self.ap = None
        self.model = None
        self.fps = None
        self.animation = None
        self.animation_length = None
        self.visible_bones = None

    def write_geo_model(self, path: str, file_name: str, model_header: BedrockModelHeader):
        # third round, probably wouldn't have to if we dfsed
        complete_path = os.path.join(path, file_name + ".geo.json")
        open(complete_path, 'w').close()
        g = open(complete_path, "a")
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

            rotation = Euler('zyx').set_from_quaternion(
                current_bone.model_size_to_original.parented(parent_rot_reverse))
            rotation.y *= -1
            rotation.z *= -1
            g.write('"rotation": ' + tuple_to_m_list(rotation.to_tuple()))

            cube_info = current_bone.additional_info

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

    def create_geo_model(self, armature: Armature, visible_bones: VisibleBones,
                         translation_fix_bones: Optional[set[str]]):

        self.ap = ArmaturePreparer(armature, visible_bones, translation_fix_bones)

        self.model = self.ap.original_armature_pruned()

        # first loop change original size to model size (this is so the elements look right in blockbench)
        for bone_name in self.model.bones:
            self.model.bones[bone_name].original_size = self.model.bones[bone_name].model_size.copy()

        # then put every element at the correct global position
        for bone_name in self.model.bones:
            self.model.bones[bone_name].delocalize(True, False)

    def create_animation(self, aa: ArmatureAnimation):
        self.animation = {}
        self.fps = aa.fps
        self.animation_length = len(aa.frames) // self.fps

        for i, frame in enumerate(aa.frames):
            armature_animated = self.ap.per_frame(frame)
            frame_time = i / self.fps

            def dfs(bone: Bone):
                if bone.name == 'Left_Ankle':
                    pass

                if not bone.name[0:9] == 'mcf_root_':
                    try:
                        rotation = frame.bone_channels[bone.parent.name].rotation
                    except KeyError:
                        rotation = Quaternion()

                    position = bone.animation_size_delta

                    if i == 0:
                        self.animation[bone.name] = []
                    self.animation[bone.name].append((frame_time, position, rotation))
                for child in bone.children:
                    dfs(child)

            dfs(armature_animated.root)

    def write_animation(self, path: str, file_name: str, animation_name: str):

        complete_path = os.path.join(path, file_name + ".json")
        open(complete_path, 'w').close()
        g = open(complete_path, "a")
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

            for j, fixed_frame in enumerate(self.animation[bone_name]):

                rotator = fixed_frame[2].copy()
                rotation = Euler('zyx').set_from_quaternion(rotator)
                rotation.y *= -1
                rotation.z *= -1
                rotator = Quaternion().set_from_euler(rotation)

                inner_vector = rotator.extract_vector()
                inner_vector.rotate_by_quaternion(self.ap.original_armature.bones[bone_name].model_size_to_original)
                rotator.replace_vector(inner_vector)

                rotation = Euler('zyx').set_from_quaternion(rotator)

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


# if __name__ == '__main__':
#     from import_file import load_bvh
#
#     a = load_bvh('data/straight_line.bvh', 1.0)
#     armature = a[0]
#
#     b = BedrockModelExporter()
#
#     visible_bones = [('a',
#                       'b',
#                       Vector3(0.0, 1.0, 0.0),
#                       Vector3(0.0, 0.0, 0.0),
#                       None
#                       ),
#                      ('b',
#                       'c',
#                       Vector3(0.0, 2.0, 0.0),
#                       Vector3(0.0, 1.0, 0.0),
#                       None
#                       ),
#                      ('c',
#                       'd',
#                       Vector3(0.0, 3.0, 0.0),
#                       Vector3(0.0, 0.0, 0.0),
#                       None
#                       ),
#                      ('d',
#                       'e',
#                       Vector3(0.0, 4.0, 0.0),
#                       Vector3(0.0, 1.0, 0.0),
#                       None
#                       ),
#                      ('e',
#                       Vector3(0.0, 4.0, 0.0),
#                       Vector3(0.0, 4.0, 0.0),
#                       Vector3(0.0, 1.0, 0.0),
#                       None
#                       )
#                      ]
#
#     b.create_geo_model(a[0], visible_bones)
#
#     b.create_animation(a[1])


if __name__ == '__main__':
    from import_file import load_bvh

    a = load_bvh('data/nikkori/nene.bvh', 2.0, max_frames=10)
    armature, animation = a

    b = BedrockModelExporter()

    visible_bone_list = [
        ('Neck',
         'Head',
         Vector3(0.0, 8.0, 0.0),
         Vector3(0.0, 0.0, 0.0),
         DisplayVoxel(Vector3(-4.0, 0.0, -4.0), Vector3(8.0, 8.0, 8.0))
         ),
        ('Waist',
         'Spine',
         Vector3(0.0, 12.0, 0.0),
         Vector3(0.0, -1.0, 0.0),
         DisplayVoxel(Vector3(-4.0, 0.0, -2.0), Vector3(8.0, 12.0, 4.0))
         ),
        ('Right_Arm',
         'Right_Elbow',
         Vector3(0.0, -5.0, 0.0),
         Vector3(-4.0, -1.0, 0.0),
         DisplayVoxel(Vector3(-4.0, -5.0, -2.0), Vector3(4.0, 6.0, 4.0))
         ),
        ('Right_Elbow',
         'Right_Wrist',
         Vector3(0.0, -4.0, 0.0),
         Vector3(0.0, 0.0, 0.0),
         DisplayVoxel(Vector3(-4.0, -6.0, -2.0), Vector3(4.0, 6.0, 4.0))
         ),
        ('Left_Arm',
         'Left_Elbow',
         Vector3(0.0, -5.0, 0.0),
         Vector3(4.0, -1.0, 0.0),
         DisplayVoxel(Vector3(0.0, -5.0, -2.0), Vector3(4.0, 6.0, 4.0))
         ),
        ('Left_Elbow',
         'Left_Wrist',
         Vector3(0.0, -4.0, 0.0),
         Vector3(0.0, 0.0, 0.0),
         DisplayVoxel(Vector3(0.0, -6.0, -2.0), Vector3(4.0, 6.0, 4.0))
         ),
        ('Right_Thigh',
         'Right_Knee',
         Vector3(0.0, -6.5, 0.0),
         Vector3(-4.0, 0.0, 0.0),
         DisplayVoxel(Vector3(0.0, -6.5, -2.0), Vector3(4.0, 6.0, 4.0))
         ),
        ('Right_Knee',
         'Right_Ankle',
         Vector3(0.0, -6.0, 0.0),
         Vector3(0.0, 0.0, -2.0),
         DisplayVoxel(Vector3(0.0, -6.0, 0.0), Vector3(4.0, 6.0, 4.0))
         ),
        ('Left_Thigh',
         'Left_Knee',
         Vector3(0.0, -6.5, 0.0),
         Vector3(0.0, 0.0, 0.0),
         DisplayVoxel(Vector3(0.0, -6.5, -2.0), Vector3(4.0, 6.0, 4.0))
         ),
        ('Left_Knee',
         'Left_Ankle',
         Vector3(0.0, -6.0, 0.0),
         Vector3(0.0, 0.0, -2.0),
         DisplayVoxel(Vector3(0.0, -6.0, 0.0), Vector3(4.0, 6.0, 4.0))
         )
    ]
    visible_bones = VisibleBones(armature)
    visible_bones.add_bones(visible_bone_list)


    b.create_geo_model(armature, visible_bones, {'Hip'})
    b.write_geo_model('C://Users//Hanmin//Desktop', 'model2',
                      BedrockModelHeader('1.12.0', 'geometry.unknown', (16, 16), (11, 3), Vector3(0.0, 0.0, 0.0)))

    b.create_animation(animation)
    b.write_animation('C://Users//Hanmin//Desktop', 'test2', 'animation.model.new')
