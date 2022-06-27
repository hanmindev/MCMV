from armature_objects import ArmatureModel, ArmatureAnimation, ArmatureFrame, VisibleBones, DisplayVoxel, VisibleBone, Joint
from math_objects import Vector3, Quaternion


class VisibleBonesCreator:
    def __init__(self):
        self.visible_bone = VisibleBones()

    def add_bones(self, visible_bone_list: list[tuple[str, str, Vector3, Vector3, DisplayVoxel]]):
        for visible_bone_tuple in visible_bone_list:
            self.add_bone(visible_bone_tuple)

    def add_bone(self, visible_bone_tuple: tuple[str, str, Vector3, Vector3, DisplayVoxel]):
        parent_joint_name, child_joint_name, initial_direction, offset, display = visible_bone_tuple
        self.visible_bone.visible_bones[child_joint_name] = VisibleBone(*visible_bone_tuple)


class ArmatureFormatter:
    model: ArmatureModel

    def __init__(self, model: ArmatureModel):
        self.model = model.copy()

    def set_frame(self, frame: ArmatureFrame):
        for joint_name in frame.joint_channels:
            joint = self.model.joints[joint_name]
            joint.animation_offset = frame.joint_channels[joint_name][0]
            joint.animation_rotation = frame.joint_channels[joint_name][1]

    def transform_to_minecraft(self, visible_bones: VisibleBones):
        for joint_name in self.model.joints:
            if joint_name not in visible_bones.visible_bones and joint_name not in visible_bones.positional:
                self.model.joints[joint_name].initial_offset = Vector3()
            elif joint_name in visible_bones.visible_bones:
                joint = self.model.joints[joint_name]

                bone = visible_bones.visible_bones[joint_name]

                initial_direction = bone.initial_direction

                new_to_old = Quaternion().between_vectors(initial_direction, joint.initial_offset)

                joint.initial_offset = initial_direction

                joint.animation_rotation = joint.animation_rotation.parented(new_to_old)
                joint.animation_offset = Vector3()

                joint.minecraft_offset = bone.offset

    def remove_joint(self, joint_name: str):
        current_joint = self.model.joints[joint_name]

        for child_name in current_joint.children:
            child = current_joint.children[child_name]
            child.initial_offset += current_joint.initial_offset
            child.animation_offset += current_joint.animation_offset
            child.animation_rotation = child.animation_rotation.parented(current_joint.animation_rotation)

            child.parent = current_joint.parent

        self.model.joints.pop(joint_name)
        del current_joint

    def prune_joints(self, keep: set):
        def dfs(joint: Joint):
            keep_children = joint.children
            if joint.parent is not None:
                joint.minecraft_offset = joint.minecraft_offset.rotated_by_quaternion(joint.parent.animation_rotation)

            if joint.name not in keep:
                self.remove_joint(joint.name)

            for child_name in keep_children:
                child = keep_children[child_name]

                dfs(child)

        dfs(self.model.joints[self.model.root_name])
