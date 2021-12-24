from typing import Optional

import utility
from math_objects import Quaternion, Vector3, Euler


class Bone:
    def __init__(self, bone_name):
        self.bone_name = bone_name
        self.channel_count = 0
        self.channel_names = []
        self.offset = (0.0, 0.0, 0.0)
        self.parent = None
        self.children = set()

    bone_name: str
    channel_count: int
    channel_names = list[str]
    offset: tuple[float, float, float]
    parent: Optional[str]
    children: set[str]


class FrameBone:
    def __init__(self, parent: str, channels: tuple[float]) -> None:
        self.parent = parent
        self.channels = channels
        self.bone_name = parent

    bone_name: str  # the bone that FrameBone is based on.
    channels: tuple[float]
    bone_name: str


class GlobalBone:
    def __init__(self, name: str, position: Vector3, rotation: Quaternion, bone_vector: Vector3):
        self.name = name
        self.position = position
        self.rotation = rotation
        self.bone_vector = bone_vector


class Frame:
    def __init__(self) -> None:
        self.frame_bones = {}

    frame_bones: dict[str: FrameBone]


class AecArmorStandPair:
    def __init__(self, aec_uuid: str, stand_uuid: str) -> None:
        self.aec_uuid = aec_uuid
        self.stand_uuid = stand_uuid
        self.update = True

    def return_command(self, position: Vector3, rotation: Quaternion, scale: float, root: str):

        commands = 'execute at ' + root + ' run tp ' + self.aec_uuid + ' ~' + ' ~'.join(
            ('{:f}'.format(i * scale) for i in position.to_tuple())) + '\n'
        commands += 'data merge entity ' + self.aec_uuid + ' {Air: ' + str(int(self.update)) + '}\n'

        rot = list(Euler('zyx').set_from_quaternion(rotation).to_tuple())

        rot[1] *= -1
        rot[2] *= -1

        commands += 'data merge entity ' + self.stand_uuid + ' {Pose:{Head:' + utility.tuple_to_m_list(tuple(rot), 'f') + '}}'

        self.update = self.update is False

        return commands
