from __future__ import annotations

from typing import Union, Optional

from math_objects import Vector3, Quaternion


class Joint:
    name: str
    parent: Optional[Joint]
    children: dict[str, Joint]

    initial_offset: Vector3

    animation_rotation: Quaternion
    animation_offset: Vector3

    minecraft_offset: Vector3

    def __init__(self, name: str):
        self.name = name

        self.children = {}

        # this is like the size
        self.initial_offset = Vector3()

        self.animation_rotation = Quaternion()
        self.animation_offset = Vector3()

        self.minecraft_offset = Vector3()

    def copy(self) -> Joint:
        new_joint = Joint(self.name)
        new_joint.parent = self.parent
        new_joint.children = self.children

        new_joint.initial_offset = self.initial_offset

        new_joint.animation_rotation = self.animation_rotation
        new_joint.animation_offset = self.animation_offset

        return new_joint


class ArmatureModel:
    """Contains the model of the armature."""
    name: str
    root_name: str
    joints: dict[str, Joint]

    def __init__(self, name: str):
        self.name = name
        self.joints = {}

    def copy(self) -> ArmatureModel:
        new_model = ArmatureModel(self.name)

        def dfs(joint: Joint):
            new_joint = joint.copy()
            try:
                joint.parent = new_model.joints[joint.parent.name]
                new_model.joints[joint.parent.name].children[new_joint.name] = new_joint
            except AttributeError:
                pass

        dfs(self.joints[self.root_name])
        new_model.root_name = new_model.root_name
        return new_model

    def add_joint(self, joint: Joint, parent_name: Optional[str]):
        self.joints[joint.name] = joint
        if parent_name is not None:
            parent = self.joints[parent_name]
            parent.children[joint.name] = joint

            joint.parent = parent
        else:
            self.root_name = joint.name


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
    pass


class VisibleBone:
    parent_joint_name: str
    child_joint_name: str

    initial_direction: Vector3
    offset: Vector3

    display: DisplayVoxel

    def __init__(self, parent_joint_name: str, child_joint_name: str, initial_direction: Vector3, offset: Vector3, display: DisplayVoxel):
        self.parent_joint_name = parent_joint_name
        self.child_joint_name = child_joint_name

        self.initial_direction = initial_direction
        self.offset = offset

        self.display = display


class VisibleBones:
    visible_bones: dict[str, VisibleBone]

    def __init__(self):
        self.visible_bones = {}
        # TODO: remove this
        self.positional = {'Hip', 'PositionOffset'}
