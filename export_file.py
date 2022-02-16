from __future__ import annotations
import math
import os
import shutil
import sys
from typing import Optional, Union, Any

from math_objects import Vector3, Quaternion, Euler
from armature import Armature, Bone, ArmatureFrame, ArmatureAnimation
# from minecraft import AecArmorStandPair
from utility import tuple_to_m_list


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

    def __init__(self, original_armature: Armature, visible_bones: list[
        tuple[Optional[str], Optional[Union[Vector3, str]], Vector3, Vector3, Any]]):
        """bruh"""
        # visible_bones is in format:
        # parent_bone_name, child_bone_name, size, offset

        self.original_armature = original_armature.copy()
        self.animated_armature = None

        self.keep = set()
        self.positional = set()

        vector_child_count = 0

        # loop through all the defined visible_bones, fill in parent information where missing, and if child is
        # vector, create a new bone.

        for i in range(len(visible_bones)):
            visible_bone = visible_bones[i]
            if visible_bone[0] is None:
                visible_bones[i] = tuple((self.original_armature.bones[visible_bone[1]].parent.name, *visible_bone[1:]))

            if type(visible_bone[1]) is str:
                end_bone = self.original_armature.bones[visible_bone[1]]
                end_bone.additional_info = visible_bone[4]
                bone_name = visible_bone[1]
            else:
                bone_name = visible_bone[0] + '_vector_child_' + str(vector_child_count)
                end_bone = Bone(bone_name)
                end_bone.additional_info = visible_bone[4]
                self.original_armature.add_bone(end_bone, visible_bone[0])

                visible_bones[i] = (visible_bone[0], bone_name, *visible_bone[2:])

                vector_child_count += 1

            self.keep.add(visible_bone[0])
            self.keep.add(bone_name)

            # TODO remove this later
            def add_keep(bone: Bone):
                if bone is None:
                    return
                self.keep.add(bone.name)
                add_keep(bone.parent)

            add_keep(end_bone)


        def dfs_add_positional(bone: Bone):
            if bone.name not in self.keep:
                self.positional.add(bone.name)

                for child in bone.children:
                    dfs_add_positional(child)

        # add names to positional set as needed
        dfs_add_positional(self.original_armature.root)

        # set size and offset of visible bones as needed
        for visible_bone in visible_bones:
            bone = self.original_armature.bones[visible_bone[1]]
            bone.model_size = visible_bone[2]
            bone.original_size.scale_to(visible_bone[2].magnitude())

            bone.pivot = visible_bone[3]
            bone.model_size_to_original = Quaternion().between_vectors(bone.model_size, bone.original_size)

    def original_armature_pruned(self):
        """Return a pruned version of the armature without any animation."""
        new_armature = self.original_armature.copy()
        new_armature.prune_bones_filtered(self.keep, self.positional, True)

        return new_armature

    def per_frame(self, frame: ArmatureFrame) -> Armature:
        self.animated_armature = self.original_armature.copy()
        self.animated_armature.import_frame(frame)
        # copy rotation if parent is not in keep
        rotational = set()
        for bone_name in set(self.animated_armature.bones.keys()):
            try:
                if self.animated_armature.bones[bone_name].name not in self.keep:
                    rotational.add(bone_name)
            except AttributeError:
                pass

        self.animated_armature.prune_bones_filtered(self.keep, self.positional, rotational)


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


class BedrockModelExporter:
    ap: Optional[ArmaturePreparer]
    def __init__(self):
        self.ap = None

    def create_geo_model(self, armature: Armature, visible_bones: list[
        tuple[Optional[str], Optional[Union[Vector3, str]], Vector3, Vector3, Any]]):
        self.ap = ArmaturePreparer(armature, visible_bones)

        original_pose = self.ap.original_armature_pruned()

        # first loop change original size to model size (this is so the elements look right in blockbench)
        for bone_name in original_pose.bones:
            original_pose.bones[bone_name].original_size = original_pose.bones[bone_name].model_size.copy()

        # then put every element at the correct global position
        for bone_name in original_pose.bones:
            original_pose.bones[bone_name].delocalize(True, False)

        # third round, probably wouldn't have to if we dfsed
        for bone_name in original_pose.bones:
            current_bone = original_pose.bones[bone_name]

            print('{')
            name = current_bone.name
            print('"name": "' + name + '",')
            if current_bone.parent is not None:
                parent = current_bone.parent.name
                print('"parent": "' + parent + '",')

                parent_rot_reverse = current_bone.parent.model_size_to_original.conjugate()
            else:
                parent_rot_reverse = Quaternion()
            pivot = current_bone.pivot_offset + current_bone.pivot
            print('"pivot": ' + tuple_to_m_list(pivot.to_tuple()) + ',')

            rotation = Euler('zyx').set_from_quaternion(
                current_bone.model_size_to_original.parented(parent_rot_reverse))
            rotation.y *= -1
            rotation.z *= -1
            print('"rotation": ' + tuple_to_m_list(rotation.to_tuple()) + ',')

            print('"cubes": [')

            cube_info = current_bone.additional_info
            if type(cube_info) is not DisplayVoxel:
                cube_offset = Vector3(0.05, 0.05, 0.05)
                cube_size = current_bone.model_size
            else:
                cube_offset = cube_info.offset
                cube_size = cube_info.size

            origin = pivot + cube_offset
            size = cube_size
            print('{"origin": ' + tuple_to_m_list(origin.to_tuple()) + ', "size": ' + tuple_to_m_list(
                (size).to_tuple()) + ', "uv": [0, 0]}')
            print(']},')

    def create_animation(self, aa: ArmatureAnimation) -> dict[str: list[tuple[float, Quaternion]]]:
        output_animation = {}
        fps = 20

        for i, frame in enumerate(aa.frames):
            armature_animated = self.ap.per_frame(frame)
            def dfs(bone: Bone):
                if not bone.name[0:9] == 'mcf_root_':
                    frame_time = i / fps
                    try:
                        rotation = frame.bone_channels[bone.parent.name].rotation
                    except KeyError:
                        rotation = Quaternion()
                    if i == 0:
                        output_animation[bone.name] = []
                    output_animation[bone.name].append((frame_time, rotation))
                for child in bone.children:
                    dfs(child)


            dfs(armature_animated.root)

        return output_animation

    def write_animation(self, processed_animation: dict[str: list[tuple[float, Quaternion]]]):

        complete_path = os.path.join('C://Users//Hanmin//Desktop', 'test' + ".json")
        open(complete_path, 'w').close()
        g = open(complete_path, "a")
        # Write the header
        g.write('{\n"format_version": "1.8.0",\n"animations": {\n"animation.model.new": {\n"animation_length": 1,'
                '\n"bones": {\n')

        l_1 = len(processed_animation) - 1
        for i, bone_name in enumerate(processed_animation):
            g.write('"' + bone_name+ '": {\n')
            g.write('"rotation": {\n')
            l_2 = len(processed_animation[bone_name]) - 1

            for j, fixed_frame in enumerate(processed_animation[bone_name]):

                rotator = fixed_frame[1].copy()
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

    a = load_bvh('data/nikkori/nene.bvh', 1.0)
    armature = a[0]

    b = BedrockModelExporter()

    visible_bones = [
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

    b.create_geo_model(a[0], visible_bones)

    b.write_animation(b.create_animation(a[1]))
