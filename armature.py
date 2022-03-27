from __future__ import annotations
import math

from typing import Optional, Any, Union

from math_objects import Quaternion, Vector3


# from minecraft import AecArmorStandPair


class Bone:
    name: str
    parent: Optional[Bone]
    children: list[Bone]

    pivot_offset: Vector3
    pivot: Vector3

    model_size = Vector3
    model_size_to_original: Quaternion
    original_size = Vector3

    animation_size_delta: Vector3
    animation_rotation: Quaternion

    additional_info: Any

    fix_bone_size: bool

    def __init__(self, name):
        self.name = name
        self.parent = None
        self.children = []

        # default pose stuff
        self.pivot_offset = Vector3(0.0, 0.0, 0.0)
        self.pivot = Vector3(0.0, 0.0, 0.0)

        self.model_size = Vector3(0.0, 0.0, 0.0)
        self.model_size_to_original = Quaternion(0.0, 0.0, 0.0, 1.0)
        self.original_size = Vector3(0.0, 0.0, 0.0)

        # keyframe stuff
        self.animation_size_delta = Vector3(0.0, 0.0, 0.0)
        self.animation_rotation = Quaternion(0.0, 0.0, 0.0, 1.0)

        self.additional_info = None

        self.fix_bone_size = False

        self._delocalized = False

    def __repr__(self) -> str:
        """Return a string representation of the object for debugging purposes."""
        return 'Bone: ' + self.name

    def copy(self):
        new_bone = Bone(self.name)

        # default pose stuff
        new_bone.pivot_offset = self.pivot_offset.copy()
        new_bone.pivot = self.pivot.copy()

        new_bone.model_size = self.model_size.copy()
        new_bone.model_size_to_original = self.model_size_to_original.copy()
        new_bone.original_size = self.original_size.copy()

        # keyframe stuff
        new_bone.animation_size_delta = self.animation_size_delta.copy()
        new_bone.animation_rotation = self.animation_rotation.copy()

        if self.additional_info is not None:
            new_bone.additional_info = self.additional_info.copy()
        else:
            new_bone.additional_info = self.additional_info

        new_bone.fix_bone_size = self.fix_bone_size

        return new_bone

    def find_ending(self) -> Vector3:
        """Return the vector of the ending point of this vector"""
        return self.pivot_offset + self.pivot + self.animation_size_delta + self.original_size.rotated_by_quaternion(
            self.animation_rotation)

    def import_frame(self, animation_data: ArmatureFrameBone):
        if not self.fix_bone_size:
            self.animation_size_delta = animation_data.offset - self.original_size
        self.animation_rotation = animation_data.rotation.copy()

    def delocalize(self, preserve_offset: bool = False, preserve_rotation: bool = False):
        """Delocalize the bone's pivot position and rotation such that the parent is not needed."""
        self._delocalized = True
        if self.parent is not None:
            if preserve_rotation:
                # preserve rotation

                # keep animation_rotation the same since that's just slapped on rotation
                self.pivot_offset.rotate_by_quaternion(self.parent.animation_rotation)
                self.pivot.rotate_by_quaternion(self.parent.animation_rotation)

                self.animation_rotation.parent(self.parent.animation_rotation)

            if preserve_offset:
                # preserve position
                # self.pivot_offset + self.pivot + self.animation_size_delta + self.original_size.rotated_by_quaternion(
                #     self.animation_rotation)

                self.pivot_offset += self.parent.pivot_offset + self.parent.pivot + self.parent.original_size

                parent_anim_copy = self.parent.animation_size_delta.copy()
                try:
                    parent_anim_copy.rotate_by_quaternion(self.parent.parent.animation_rotation)
                except:
                    pass

                self.animation_size_delta += parent_anim_copy

                # self.pivot_offset += self.parent.find_ending()

    def remove_bone(self, preserve_offset: bool = False, preserve_rotation: bool = False):
        """Remove a bone. Any children of this bone will be given to this bone's parent.
        If this bone does not have a parent, the children will be destroyed."""

        curr = self

        if curr.parent is None:
            self.__init__(self.name)
        else:
            curr.parent.children.remove(curr)

            for child in curr.children:
                child.delocalize(preserve_offset, preserve_rotation)
                child.parent = curr.parent

            curr.parent.children += curr.children


class ArmatureAnimation:
    frames: list[ArmatureFrame]
    fps: int

    def __init__(self, fps: Union[float, int]):
        self.frames = []
        self.fps = fps

    def __len__(self):
        return len(self.frames)


class ArmatureFrame:
    bone_channels: dict[str, ArmatureFrameBone]

    def __init__(self):
        self.bone_channels = {}


class ArmatureFrameBone:
    def __init__(self, offset, rotation):
        self.offset = offset
        self.rotation = rotation


class Armature:
    name: str
    bones: dict[str: Bone]
    root: Bone

    def __init__(self, name: str):
        self.name = name
        self.root = Bone('mcf_root_' + self.name)
        self.bones = {self.root.name: self.root}

    def __repr__(self) -> str:
        """Return a string representation of the object for debugging purposes."""
        return 'Armature: ' + self.name

    def __len__(self):
        return len(self.bones)

    def copy(self):
        new_armature = Armature(self.name)
        new_armature.bones = {}

        def dfs(bone: Bone):
            new_bone = bone.copy()
            try:
                new_bone.parent = new_armature.bones[bone.parent.name]
                new_armature.bones[bone.parent.name].children.append(new_bone)
            except AttributeError:
                pass

            new_armature.bones[bone.name] = new_bone

            for child in bone.children:
                dfs(child)

        dfs(self.root)
        new_armature.root = new_armature.bones[self.root.name]
        return new_armature

    def add_bone(self, new_bone: Bone, parent_name: str):
        # The root bone must be added first.

        self.bones[new_bone.name] = new_bone

        if self.root is None:
            self.root = new_bone
        else:
            for bone_name in self.bones:
                if bone_name == parent_name:
                    bone = self.bones[bone_name]
                    new_bone.parent = bone
                    bone.children.append(new_bone)
                    break

    def remove_bone(self, removal_bone: Bone, preserve_offset: bool = False, preserve_rotation: bool = False):
        if removal_bone.parent is None:
            self.root = Bone('mcf_root_' + self.name)
            self.bones = None
        else:
            removal_bone.remove_bone(preserve_offset, preserve_rotation)
            del self.bones[removal_bone.name]

    def prune_bones(self, keep: set, preserve_offset: bool = False, preserve_rotation: bool = False):
        """Remove all bones that are not in keep.
        """

        # TODO: Check whether order matters. Do we need to dfs?

        def dfs(bone: Bone):
            save_children = bone.children.copy()

            if bone.name not in keep:
                self.remove_bone(bone, preserve_offset, preserve_rotation)

            del self.bones[bone.name]

            for child in save_children:
                dfs(child)

        keep.add(self.root.name)
        dfs(self.root)

    def prune_bones_filtered(self, keep: set, positional: Union[set, bool], rotational: Union[set, bool]):
        """Remove all bones that are not in keep. Whether the bones will retain their position and
        rotation depends on whether they are in sets positional and rotational.

        Positional and rotational can also be a boolean value if one of the parameters should be set for all
        bones.
        """
        if type(positional) is bool:
            pos = positional
        else:
            pos = None

        if type(rotational) is bool:
            rot = rotational
        else:
            rot = None

        def dfs(bone: Bone):
            save_children = bone.children.copy()
            p = pos
            r = rot

            if p is None:
                p = bone.name in positional
            if r is None:
                r = bone.name in rotational
            if bone is not self.root:
                bone.delocalize(p, r)

            for child in save_children:
                dfs(child)
            if bone.name not in keep and bone is not self.root:
                self.remove_bone(bone, False, False)

        dfs(self.root)

    def import_frame(self, frame: ArmatureFrame):
        for bone_name in frame.bone_channels:
            self.bones[bone_name].import_frame(frame.bone_channels[bone_name])
