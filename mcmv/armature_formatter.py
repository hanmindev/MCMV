from typing import Union

from mcmv.armature_objects import ArmatureModel, ArmatureFrame, MinecraftModel, DisplayVoxel, VisibleBone, Joint, PositionalBone, Bone
from mcmv.math_objects import Vector3, Quaternion


class MinecraftModelCreator:
    """Object used to create a Minecraft Model"""

    def __init__(self):
        self.minecraft_model = MinecraftModel()

    def set_bones(self, visible_bone_list: list[Union[tuple[str, str, Vector3, Vector3, DisplayVoxel], tuple[str, str]]]):
        """Set bones for the Minecraft Model"""
        new_root_name = None
        for visible_bone_tuple in visible_bone_list:
            if len(visible_bone_tuple) == 5:
                parent_name, name, size, offset, display = visible_bone_tuple
                new_bone = VisibleBone(name, size.scaled_pixels_to_meter(), offset.scaled_pixels_to_meter(), display)
            else:
                parent_name, name = visible_bone_tuple
                new_bone = PositionalBone(name)
            self.minecraft_model.bones[visible_bone_tuple[1]] = new_bone

        for visible_bone_tuple in visible_bone_list:
            bone = self.minecraft_model.bones[visible_bone_tuple[1]]

            if visible_bone_tuple[0] not in self.minecraft_model.bones:
                if new_root_name is not None:
                    raise 'Multiple roots detected!'
                new_root_name = visible_bone_tuple[0]
                self.minecraft_model.root = bone
            else:
                bone.parent = self.minecraft_model.bones[visible_bone_tuple[0]]
                bone.parent.children[bone.name] = bone

        fake_root = self.minecraft_model.root
        new_root = PositionalBone(new_root_name)
        new_root.children[fake_root.name] = fake_root
        fake_root.parent = new_root

        self.minecraft_model.bones[new_root.name] = new_root

        self.minecraft_model.root = new_root

    def create_bones(self, model: ArmatureModel, scale: Union[int, float] = 1, base: str = None):

        def find_fixed_direction(vec: Vector3) -> tuple[str, str]:
            largest = 'z'
            m = vec.z
            if abs(vec.y) > abs(vec.z):
                largest = 'y'
                m = vec.y
                if abs(vec.x) > abs(vec.y):
                    largest = 'x'
                    m = vec.x
            else:
                if abs(vec.x) > abs(vec.z):
                    largest = 'x'
                    m = vec.x
            if m < 0:
                sign = '-'
            else:
                sign = '+'

            return sign, largest

        def dfs(joint: Joint, reached_base: bool) -> Bone:
            if reached_base:
                d = find_fixed_direction(joint.initial_offset)
                length = joint.initial_offset.magnitude()
                lw_ratio = 8
                width = length / lw_ratio

                if d[1] == 'x':
                    bone_direction_vector = Vector3(length, 0.0, 0.0)
                    bone_size_vector = Vector3(length, width, width)
                    bone_size_offset_vector = Vector3(0.0, -width / 2, -width / 2)
                elif d[1] == 'y':
                    bone_direction_vector = Vector3(0.0, length, 0.0)
                    bone_size_vector = Vector3(width, length, width)
                    bone_size_offset_vector = Vector3(-width / 2, 0.0, -width / 2)
                else:
                    bone_direction_vector = Vector3(0.0, 0.0, length)
                    bone_size_vector = Vector3(width, width, length)
                    bone_size_offset_vector = Vector3(-width / 2, -width / 2, 0.0)

                if d[0] == '-':
                    bone_direction_vector *= -1
                    bone_size_offset_vector += bone_direction_vector

                new_bone = VisibleBone(joint.name, bone_direction_vector * scale, Vector3(),
                                       DisplayVoxel(bone_size_offset_vector * 16 * scale, bone_size_vector * 16 * scale, 'mcmv_end_rod ' + ''.join(d)))
            else:
                new_bone = PositionalBone(joint.name)
                if joint.name == base:
                    reached_base = True

            self.minecraft_model.bones[new_bone.name] = new_bone

            for child_name in joint.children:
                child = joint.children[child_name]
                child_bone = dfs(child, reached_base)
                new_bone.children[child_bone.name] = child_bone
                child_bone.parent = new_bone

            return new_bone

        self.minecraft_model.root = dfs(model.root, base is None)
        self.minecraft_model.bones[self.minecraft_model.root.name] = self.minecraft_model.root


class MinecraftModelFormatter:
    @staticmethod
    def get_model_global(minecraft_model: MinecraftModel,
                         offset: Vector3 = Vector3().copy(), rotate: Quaternion = Quaternion().copy()) -> dict[str, tuple[Vector3, Quaternion]]:
        global_transformation = {minecraft_model.root.name: (offset, rotate)}

        def dfs(bone: Bone):
            parent_global_offset, parent_global_rotation = global_transformation[bone.name]

            for child_name in bone.children:
                child = bone.children[child_name]

                child_global_offset = parent_global_offset + bone.size + child.offset
                child_global_rotation = Quaternion()

                global_transformation[child_name] = (child_global_offset, child_global_rotation)

                dfs(child)

        dfs(minecraft_model.root)

        return global_transformation


class ArmatureFormatter:
    @staticmethod
    def set_frame(model: ArmatureModel, frame: ArmatureFrame = None):
        if frame is None:
            return
        for joint_name in frame.joint_channels:
            joint = model.joints[joint_name]
            joint.animation_offset = frame.joint_channels[joint_name][0]
            joint.animation_rotation = frame.joint_channels[joint_name][1]

    @staticmethod
    def get_model_global(model: ArmatureModel) -> dict[str, tuple[Vector3, Quaternion]]:
        global_transformation = {model.root.name: (model.root.animation_offset, Quaternion())}

        # ending point, rotation
        def dfs(joint: Joint):
            parent_translation, parent_rotation = global_transformation[joint.name]

            for child_name in joint.children:
                child = joint.children[child_name]

                child_translation = parent_translation + child.animation_offset.rotated_by_quaternion(parent_rotation)  # TODO rotate this by grandparent rotation
                child_rotation = child.animation_rotation.parented(parent_rotation)

                global_transformation[child_name] = (child_translation, child_rotation)

                dfs(child)

        dfs(model.root)

        return global_transformation
