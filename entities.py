from typing import Optional

import utility
from math_objects import Quaternion, Vector3, Euler


class Bone:
    """Bone objects as described at the start of the .bvh file."""

    def __init__(self, bone_name: str) -> None:
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
    """Bone objects per frame as described at the end of the .bvh file."""

    def __init__(self, parent: str, channels: tuple[float]) -> None:
        self.parent = parent
        self.channels = channels
        self.bone_name = parent

    bone_name: str  # the bone that FrameBone is based on.
    channels: tuple[float]
    bone_name: str


class GlobalBone:
    """Bones with global position and rotation."""

    def __init__(self, name: str, position: Vector3, rotation: Quaternion):
        self.name = name
        self.position = position
        self.rotation = rotation


class Frame:
    """A single frame containing all FrameBones."""

    def __init__(self) -> None:
        self.frame_bones = {}

    frame_bones: dict[str: FrameBone]


class AecArmorStandPair:
    """A class describing an AEC-ArmorStand pair."""

    def __init__(self, name: str, aec_uuid: str, stand_uuid: str, size: Vector3, offset: Vector3, t_pose: Vector3,
                 item: str) -> None:
        self.name = name
        self.aec_uuid = aec_uuid
        self.stand_uuid = stand_uuid
        # vector of the bone
        self.size = size
        # vector of the offset of the bone
        self.offset = offset
        self.t_pose = t_pose
        # name of the item to hold
        self.item = item

        self.update = True

    def return_reset_commands(self) -> list[str]:
        commands = ['kill ' + self.aec_uuid,
                    'kill ' + self.stand_uuid,
                    'summon area_effect_cloud ~ ~ ~ {Duration:2147483647,' + utility.uuid_str_to_uuid_nbt(
                        self.aec_uuid) + ',Passengers:[{id:"minecraft:armor_stand",DisabledSlots:4144959,Invisible:1,' + utility.uuid_str_to_uuid_nbt(
                        self.stand_uuid) + '}]}',
                    'item replace entity ' + self.stand_uuid + ' armor.head with ' + self.item]
        return commands

    def return_transformation_command(self, position: Vector3, rotation: Quaternion, root_uuid: str):
        """Return commands that translate and rotate the AEC-ArmorStand pair to the specified position and rotation."""
        q = Quaternion().between_vectors(self.size, self.t_pose)
        q.parent(rotation)

        commands = 'execute at ' + root_uuid + ' run tp ' + self.aec_uuid + ' ~' + ' ~'.join(
            ('{:f}'.format(i) for i in position.to_tuple())) + '\n'
        commands += 'data merge entity ' + self.aec_uuid + ' {Air: ' + str(int(self.update)) + '}\n'

        rot = list(Euler('zyx').set_from_quaternion(q).to_tuple())

        rot[1] *= -1
        rot[2] *= -1

        commands += 'data merge entity ' + self.stand_uuid + ' {Pose:{Head:' + utility.tuple_to_m_list(tuple(rot),
                                                                                                       'f') + '}}'

        self.update = self.update is False

        return commands
