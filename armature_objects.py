from __future__ import annotations
import math
import json
import os

from typing import Optional, Any, Union

from math_objects import Quaternion, Vector3

# from minecraft import AecArmorStandPair

FORMAT_VERSION = 1.0


class VisibleBones:
    visible_bones: dict[str, Bone]
    armature: Armature
    pose_to_input: bool
    bone_list: list[tuple[str, str, Vector3, Vector3, Optional[list[str]], DisplayVoxel]]
    pre_rotate: set[str]

    def __init__(self, armature: Armature, pose_to_input: bool = False):
        self.visible_bones = {}
        self.armature = armature
        self.pose_to_input = pose_to_input
        self.pre_rotate = set()
        self.bone_list = []

    def add_bones(self, bone_list: list[
        tuple[Optional[str], Optional[Union[Vector3, str]], Vector3, Vector3, Optional[list[str]], DisplayVoxel]]):
        # Fill in missing bone information
        vector_child_count = 0
        for i in range(len(bone_list)):
            if bone_list[i][0] is None or type(bone_list[i][1]) is str:
                # normal bone
                bone_name = bone_list[i][1]

                end_bone = self.armature.bones[bone_name]
                end_bone.bone_lock = bone_list[i][4]
                end_bone.bone_display = bone_list[i][5]

                self.visible_bones[bone_name] = end_bone
            else:
                # give child to childless parent
                bone_name = bone_list[i][0] + '_vector_child_' + str(vector_child_count)

                end_bone = Bone(bone_name)
                end_bone.bone_lock = bone_list[i][4]
                end_bone.bone_display = bone_list[i][5]
                self.armature.add_bone(end_bone, bone_list[i][0])

                self.visible_bones[bone_name] = end_bone

                vector_child_count += 1

            if end_bone.bone_lock is None:
                end_bone.bone_lock = []

            end_bone.model_size = bone_list[i][2]
            end_bone.original_size.scale_to(bone_list[i][2].magnitude())
            end_bone.pivot = bone_list[i][3]
            end_bone.model_size_to_original = Quaternion().between_vectors(end_bone.model_size, end_bone.original_size)

            self.bone_list.append((end_bone.parent.name, end_bone.name, end_bone.model_size, end_bone.pivot,
                                   end_bone.bone_lock, end_bone.bone_display))

            if self.pose_to_input:
                self.pre_rotate.add(end_bone.name)

    def create_bones(self, bone_set: set, scale: Union[float, int] = 1.0):
        for new_bone_name in bone_set:
            end_bone = self.armature.bones[new_bone_name]
            if end_bone is self.armature.root:
                continue

            model_magnitude = scale * 16 * end_bone.original_size.magnitude()

            if model_magnitude != 0:
                if end_bone.original_size.normalized().dot_prod(Vector3(0.0, 1.0, 0.0)) > 0:
                    end_bone.bone_display = DisplayVoxel(Vector3(-0.5, -0.5, -0.5), Vector3(1.0, model_magnitude, 1.0))
                    end_bone.model_size = Vector3(0.0, model_magnitude, 0.0)
                else:
                    end_bone.bone_display = DisplayVoxel(Vector3(-0.5, 0.5 - model_magnitude, -0.5),
                                                         Vector3(1.0, model_magnitude, 1.0))
                    end_bone.model_size = Vector3(0.0, -model_magnitude, 0.0)

            end_bone.model_size_to_original = Quaternion().between_vectors(end_bone.model_size, end_bone.original_size)

            self.bone_list.append((end_bone.parent.name, end_bone.name, end_bone.model_size, end_bone.pivot,
                                   end_bone.bone_lock, end_bone.bone_display))

            self.visible_bones[new_bone_name] = end_bone

            if self.pose_to_input:
                self.pre_rotate.add(end_bone.name)

    def fill_bones(self):
        new_bone_set = set(self.armature.bones.keys()).difference(set(self.visible_bones.keys()))
        self.create_bones(new_bone_set)

    def format(self) -> tuple[set, set]:
        keep = set()
        positional = set()
        for visible_bone_name in self.visible_bones:
            if visible_bone_name == self.armature.root.name:
                continue
            keep.add(visible_bone_name)
            keep.add(self.visible_bones[visible_bone_name].parent.name)

        def dfs_add_positional(bone: Bone):
            for child in bone.children:
                dfs_add_positional(child)

                if child.name in positional and bone.name not in keep:
                    positional.add(bone.name)

        dfs_add_positional(self.armature.root)

        return keep, positional

    def export_json(self, path: str, file_name: str):
        complete_path = os.path.join(path, file_name + ".json")
        open(complete_path, 'w').close()
        f = open(complete_path, "a", encoding="utf-8")

        json_dict = {'format_version': FORMAT_VERSION, 'visible_bones': []}
        for bone_info in self.bone_list:
            current_bone_dict = {
                'parent_name': bone_info[0],
                'name': bone_info[1],
                'model_size': bone_info[2].to_tuple(),
                'pivot': bone_info[3].to_tuple(),
                'bone_lock': bone_info[4]
            }
            if bone_info[5] is not None:
                bone_offset = bone_info[5].offset.to_tuple()
                bone_size = bone_info[5].size.to_tuple()
                if bone_offset is not None or bone_size is not None:
                    current_bone_dict['bone_display'] = {}

                if bone_offset is not None:
                    current_bone_dict['bone_display']['offset'] = bone_offset
                if bone_size is not None:
                    current_bone_dict['bone_display']['size'] = bone_size

            json_dict['visible_bones'].append(current_bone_dict)

        json.dump(json_dict, f, indent=4)

    def import_json(self, path: str, file_name: str):
        self.bone_list = []
        complete_path = os.path.join(path, file_name + ".json")
        f = open(complete_path, "r", encoding="utf-8")
        json_dict = json.load(f)
        if json_dict['format_version'] != FORMAT_VERSION:
            assert 'Format Version for bones is incorrect! Got ' + str(
                json_dict['format_version']) + ', expected ' + str(FORMAT_VERSION)

        for j_inf in json_dict['visible_bones']:
            dv_o = j_inf['bone_display']['offset']
            dv_s = j_inf['bone_display']['size']

            dv = None
            if dv_o is not None:
                dv_o = Vector3(*dv_o)
            if dv_s is not None:
                dv_s = Vector3(*dv_s)

            if dv_o is not None or dv_s is not None:
                dv = DisplayVoxel(dv_o, dv_s)

            self.bone_list.append(
                (
                    j_inf['parent_name'],
                    j_inf['name'],
                    Vector3(*j_inf['model_size']),
                    Vector3(*j_inf['pivot']),
                    j_inf['bone_lock'],
                    dv
                )
            )


class DisplayVoxel:
    def __init__(self, offset: Vector3, size: Vector3):
        self.offset = offset
        self.size = size

    def copy(self):
        return DisplayVoxel(self.offset.copy(), self.size.copy())


class Bone:
    name: str
    parent: Optional[Bone]
    children: list[Bone]

    channels: list[str]

    pivot_offset: Vector3
    pivot: Vector3

    model_size = Vector3
    model_size_to_original: Quaternion
    original_size = Vector3

    animation_size_delta: Vector3
    animation_rotation: Quaternion

    bone_display: Optional[DisplayVoxel]
    bone_lock: list[str]

    fix_bone_size: bool

    def __init__(self, name):
        self.name = name
        self.parent = None
        self.children = []

        self.channels = []

        # default pose stuff
        self.pivot_offset = Vector3(0.0, 0.0, 0.0)
        self.pivot = Vector3(0.0, 0.0, 0.0)

        self.model_size = Vector3(0.0, 0.0, 0.0)
        self.model_size_to_original = Quaternion(0.0, 0.0, 0.0, 1.0)
        self.original_size = Vector3(0.0, 0.0, 0.0)

        # keyframe stuff
        self.animation_size_delta = Vector3(0.0, 0.0, 0.0)
        self.animation_rotation = Quaternion(0.0, 0.0, 0.0, 1.0)

        self.bone_display = None
        self.bone_lock = []

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

        new_bone.bone_lock = self.bone_lock.copy()

        if self.bone_display is not None:
            new_bone.bone_display = self.bone_display.copy()
        else:
            new_bone.bone_display = self.bone_display

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
    offset: Vector3
    rotation: Quaternion

    def __init__(self, offset: Vector3, rotation: Quaternion):
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
