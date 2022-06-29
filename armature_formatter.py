from typing import Union

from armature_objects import ArmatureModel, ArmatureFrame, MinecraftModel, DisplayVoxel, VisibleBone, Joint, PositionalBone, Bone
from math_objects import Vector3, Quaternion


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


class MinecraftModelFormatter:
    @staticmethod
    def get_model_global(minecraft_model: MinecraftModel) -> dict[str, tuple[Vector3, Quaternion]]:
        global_transformation = {minecraft_model.root.name: (Vector3(), Quaternion())}

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
