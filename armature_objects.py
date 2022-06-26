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

    def __init__(self, name: str, parent: Joint = None):
        self.name = name
        self.parent = parent
        self.parent.children[self.name] = self

        self.children = {}

        self.initial_offset = Vector3()

        self.animation_rotation = Quaternion()
        self.animation_offset = Vector3()


class ArmatureModel:
    """Contains the model of the armature."""
    name: str
    root_name: str
    joints: dict[str, Joint]

    def __init__(self, name: str):
        self.name = name

    def add_joint(self, joint: Joint, parent_name: Optional[str]):
        self.joints[joint.name] = joint
        if parent_name is not None:
            parent = self.joints[parent_name]
            parent.children[joint.name] = joint

            joint.parent = parent


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
