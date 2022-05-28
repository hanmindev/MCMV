from __future__ import annotations

from typing import Optional, Union

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

class ArmatureAnimation:
    """Contains the animation for the armature."""
    frames: list[ArmatureFrame]
    fps: int

    def __init__(self, fps: Union[float, int]):
        self.frames = []
        self.fps = fps

    def __len__(self):
        return len(self.frames)


class ArmatureFrame:
    joint_channels: dict[str, tuple[Vector3, Quaternion]]

    def __init__(self):
        self.joint_channels = {}


class Armature:
    name: str
    joints: dict[str: Joint]
    root: Joint

    def __init__(self, name: str):
        self.name = name
        self.root = Joint('mcf_root_' + self.name)
        self.joints = {self.root.name: self.root}

    def __repr__(self) -> str:
        """Return a string representation of the object for debugging purposes."""
        return 'Armature: ' + self.name

    def __len__(self):
        return len(self.joints)

    def copy(self):
        new_armature = Armature(self.name)
        new_armature.joints = {}

        def _joint_copy_helper(joint: Joint, copied_parent_joint: Optional[Joint]):
            new_joint = Joint(joint.name, copied_parent_joint)
            new_armature.joints[joint.name] = new_joint

            new_joint.initial_offset = joint.initial_offset.copy()
            new_joint.animation_offset = joint.animation_offset.copy()
            new_joint.animation_rotation = joint.animation_rotation

            for child_name in joint.children:
                _joint_copy_helper(joint.children[child_name], new_joint)

        _joint_copy_helper(self.root, None)

        return new_armature

    def import_frame(self, frame: ArmatureFrame):
        for joint_name in frame.joint_channels:
            joint = self.joints[joint_name]

            frame_info = frame.joint_channels[joint_name]

            joint.animation_offset = frame_info[0]
            joint.animation_rotation = frame_info[1]

    def add_joint(self, new_joint: Joint, parent_name: str):
        # The root joint must be added first.

        self.joints[new_joint.name] = new_joint

        if self.root is None:
            self.root = new_joint
        else:
            parent_joint = self.joints[parent_name]
            new_joint.parent = parent_joint
            parent_joint.children[new_joint.name] = new_joint
