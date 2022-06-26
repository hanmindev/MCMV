from typing import Union, Optional

from armature_objects import Armature, Joint
from math_objects import Vector3


class DisplayVoxel:
    voxel_size: Optional[Vector3]
    voxel_offset: Optional[Vector3]
    item_name: Optional[str]

    def __init__(self, first: Optional[Union[Vector3, str]] = None, second: Optional[Vector3] = None, item_name: Optional[str] = None):
        if isinstance(first, str):
            self.item_name = first
        else:
            self.voxel_size = first
            self.voxel_offset = second
            self.item_name = item_name


class VisibleBones:
    armature: Armature
    rigid_bones: dict[str, tuple[Optional[str], str, Vector3, Vector3, DisplayVoxel]]
    positional_bones: dict[str, tuple[Optional[str], str, Vector3]]
    keep: set[str]
    positional: set[str]

    def __init__(self, armature: Armature):
        self.armature = armature.copy()
        self._clear_bones()

    def _clear_bones(self):
        self.rigid_bones = {}
        self.positional_bones = {}
        self.keep = set(self.armature.root.name)
        self.positional = set()

    def set_bones(self, visible_bone_list: list[Union[tuple[Optional[str], str, Vector3, Vector3, DisplayVoxel], tuple[Optional[str], str, Vector3]]]):
        self._clear_bones()

        self.add_bones(visible_bone_list)

    def add_bones(self, visible_bone_list: list[Union[tuple[Optional[str], str, Vector3, Vector3, DisplayVoxel], tuple[Optional[str], str, Vector3]]]):
        for visible_bone in visible_bone_list:
            if len(visible_bone) == 5:
                self._add_rigid_bone(*visible_bone)
            else:
                self._add_positional_bone(*visible_bone)

    def _add_rigid_bone(self, start_joint_name: Optional[str], end_joint_name: str, size: Vector3, offset: Vector3, display: DisplayVoxel):
        self.rigid_bones[end_joint_name] = (start_joint_name, end_joint_name, size, offset, display)

        self.keep.add(start_joint_name)
        self.keep.add(end_joint_name)

    def _add_positional_bone(self, start_joint_name: Optional[str], end_joint_name: str, offset: Vector3):
        self.positional_bones[end_joint_name] = (start_joint_name, end_joint_name, offset)

        def _add_ancestor_positional(joint: Joint):
            if joint.name == start_joint_name:
                return

            self.positional.add(joint.name)

            _add_ancestor_positional(joint.parent)

        _add_ancestor_positional(self.armature.joints[end_joint_name])
        self.keep.add(start_joint_name)
        self.keep.add(end_joint_name)


class ArmaturePreparer:
    original_armature: Armature
    visible_bone_object: VisibleBones

    def __init__(self, visible_bone_object: VisibleBones):
        self.original_armature = visible_bone_object.armature.copy()
        self.visible_bone_object = visible_bone_object

    def prune_armature(self, armature: Armature):
        keep = self.visible_bone_object.keep
        positional = self.visible_bone_object.positional

        def _prune_joint(joint: Joint):
            save_children = joint.children
            if joint not in keep:
                for child_name in joint.children:
                    child = joint.children[child_name]
                    if child_name in positional:
                        child.initial_offset += joint.initial_offset
                        child.animation_offset = child.animation_offset.rotated_by_quaternion(joint.animation_rotation) + joint.animation_offset
                    child.animation_rotation = child.animation_rotation.parented(joint.animation_rotation)

                    child.parent = joint.parent
                    joint.parent.children[child.name] = child
                joint_name = joint.name
                
                del armature.joints[joint_name]
                del joint.parent.children[joint_name]

            for child_name in save_children:
                _prune_joint(save_children[child_name])

        _prune_joint(armature.root)
