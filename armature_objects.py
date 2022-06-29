from __future__ import annotations

from typing import Union, Optional

from math_objects import Vector3, Quaternion


class Joint:
    """Object representing a bvh Joint"""
    name: str
    parent: Optional[Joint]
    children: dict[str, Joint]

    initial_offset: Vector3

    animation_rotation: Quaternion
    animation_offset: Vector3

    def __init__(self, name: str):
        self.name = name

        self.parent = None
        self.children = {}

        # this is like the size
        self.initial_offset = Vector3()

        self.animation_rotation = Quaternion()
        self.animation_offset = Vector3()

    def __repr__(self) -> str:
        """Return a string representation of the object for debugging purposes."""
        return 'Joint({})'.format(self.name)

    def copy(self) -> Joint:
        """Return a copy of this joint (not a deepcopy)"""
        new_joint = Joint(self.name)
        new_joint.parent = self.parent
        new_joint.children = self.children

        new_joint.initial_offset = self.initial_offset

        new_joint.animation_rotation = self.animation_rotation
        new_joint.animation_offset = self.animation_offset

        return new_joint


class ArmatureModel:
    """Contains the model of the armature representing the original bvh model."""
    name: str
    root: Optional[Joint]
    joints: dict[str, Joint]

    def __init__(self, name: str):
        self.name = name
        self.root = None
        self.joints = {}

    def copy(self) -> ArmatureModel:
        """Return a (deep)copy of this Armature Model"""
        new_model = ArmatureModel(self.name)

        def dfs(joint: Joint):
            new_joint = joint.copy()
            new_joint.parent = None
            new_joint.children = {}
            new_model.joints[new_joint.name] = new_joint
            try:
                new_joint.parent = new_model.joints[joint.parent.name]
                new_model.joints[joint.parent.name].children[new_joint.name] = new_joint
            except AttributeError:
                pass

            for child_name in joint.children:
                dfs(joint.children[child_name])

        dfs(self.root)
        new_model.root = new_model.joints[self.root.name]
        return new_model

    def add_joint(self, joint: Joint, parent_name: str = None):
        """Add a joint to this armature model."""
        self.joints[joint.name] = joint
        if parent_name is not None:
            parent = self.joints[parent_name]
            parent.children[joint.name] = joint

            joint.parent = parent
        else:
            self.root = joint


class ArmatureFrame:
    """Contains a single frame of an animation with the offset and rotation of each joint."""
    joint_channels: dict[str, tuple[Vector3, Quaternion]]

    def __init__(self):
        self.joint_channels = {}


class ArmatureAnimation:
    """Contains the animation for the armature."""
    frames: list[ArmatureFrame]
    fps: int

    def __init__(self, fps: Union[float, int]):
        self.frames = []
        self.fps = fps

    def __len__(self):
        return len(self.frames)


class DisplayVoxel:
    """Contains information regarding the visible part of the bone"""
    def __init__(self, offset: Vector3, size: Vector3, item: str = None):
        self.offset = offset
        self.size = size
        self.item = item

    def copy(self):
        """Return a (deep)copy of this object."""
        return DisplayVoxel(self.offset.copy(), self.size.copy(), self.item)


class Bone:
    """Object representing a Minecraft Bone"""
    name: str
    parent: Optional[Bone]
    children: dict[str, Bone]

    size: Vector3
    offset: Vector3

    local_animation_rotation: Quaternion

    def __init__(self, name: str):
        self.name = name
        self.parent = None
        self.children = {}

        self.size = Vector3()
        self.offset = Vector3()

        self.local_animation_rotation = Quaternion()

    def __repr__(self):
        return 'Bone({})'.format(self.name)


class VisibleBone(Bone):
    """Object representing a Visible Minecraft Bone"""
    display: Optional[DisplayVoxel]

    def __init__(self, name: str, size: Vector3, offset: Vector3, display: DisplayVoxel):
        super().__init__(name)
        self.size = size
        self.offset = offset
        self.display = display

    def __repr__(self):
        return 'VisibleBone({})'.format(self.name)


class PositionalBone(Bone):
    """Object representing a Positional Minecraft Bone"""
    local_animation_position: Vector3

    def __init__(self, name: str):
        super().__init__(name)
        self.local_animation_position = Vector3()

    def __repr__(self):
        return 'PositionalBone({})'.format(self.name)


class MinecraftModel:
    """Object representing a Minecraft Model"""
    bones: dict[str, Bone]
    root: Optional[Bone]

    def __init__(self):
        self.bones = {}
        self.root = None
