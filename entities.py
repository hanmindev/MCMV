from typing import Optional

import utility
from math_objects import Quaternion, Vector3, Euler


class Bone:
    """Bone objects as described at the start of the .bvh file.

    Instance Attributes:
      - bone_name: Name of the bone
      - channel_count: The number of channels describing the Bone (e.g. position, rotation)
      - channel_names: The names of the channels (e.g. Xrotation, Xposition)
      - offset: The offset from the bone's parent.
      - parent: Name of the parent of this bone.
      - children: Set containing names of this bone's children.
    """

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
    """Bone objects per frame as described at the end of the .bvh file.

    Instance Attributes:
      - bone_name: The name of the bone that FrameBone is based on.
      - position: The position of the bone from the channels as described by the .bvh file.
      - rotation: The rotation of the bone from the channels as described by the .bvh file.
    """

    def __init__(self, bone_name: str, position: Vector3, rotation: Quaternion) -> None:
        self.bone_name = bone_name
        self.position = position
        self.rotation = rotation

    bone_name: str  # the bone that FrameBone is based on.
    position: Vector3
    rotation: Quaternion


class GlobalBone:
    """Bones with global position and rotation.

    Instance Attributes:
      - name: Name of the bone.
      - position: Position of the bone.
      - rotation: Rotation of the bone.
    """

    def __init__(self, name: str, position: Vector3, rotation: Quaternion):
        self.name = name
        self.position = position
        self.rotation = rotation

    name: str
    position: Vector3
    rotation: Quaternion


class Frame:
    """A single frame containing all FrameBones for a specific armature.

    Instance Attributes:
      - frame_bones: A dictionary mapping the bone name to a FrameBone object.
    """

    def __init__(self) -> None:
        self.frame_bones = {}

    frame_bones: dict[str: FrameBone]


class AecArmorStandPair:
    """A class describing an AEC-ArmorStand pair.

    Instance Attributes:
      - name: Name of the bone (should be a key in main.BONE_MAPPER)
      - aec_uuid: UUID of the AEC (e.g. 2f9d6e9a-aaca-4964-9059-ec43f2016499)
      - stand_uuid: UUID of the Armor Stand (e.g. 19c4830d-8714-4e62-b041-0cde12b6de96)
      - size: The size of the bone as a Vector3 object
      - offset: The offset of the bone as a Vector3 object
      - t_pose: The initial direction of the bone as a Vector3 object (The vector that the bone would
            be pointing towards as default (e.g. if your .bvh model initially is doing a T-Pose,
            the right arm would have the vector (-1.0, 0.0, 0.0).)
      - item: A string representation of the Minecraft item to be displayed. (e.g. diamond_hoe{CustomModelData:100}
    """
    # Private Instance Attributes:
    #  - _update: Whether the Air NBT should be 0 or 1. Updating this value causes the AEC to change position.

    name: str
    aec_uuid: str
    stand_uuid: str
    size: Vector3
    offset: Vector3
    t_pose: Vector3
    item: str
    _update: bool

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

        self._update = True

    def return_reset_commands(self) -> list[str]:
        """Return a list of commands to reset the AEC-Stand pair."""
        commands = ['kill ' + self.aec_uuid,
                    'kill ' + self.stand_uuid,
                    'summon area_effect_cloud ~ ~ ~ {Duration:2147483647,' + utility.uuid_str_to_uuid_nbt(
                        self.aec_uuid) + ',Passengers:[{id:"minecraft:armor_stand",DisabledSlots:4144959,Invisible:1,'
                                         '' + utility.uuid_str_to_uuid_nbt(self.stand_uuid) + '}]}',
                    'item replace entity ' + self.stand_uuid + ' armor.head with ' + self.item]
        return commands

    def return_transformation_command(self, position: Vector3, rotation: Quaternion, root_uuid: str) -> str:
        """Return commands as a single string that translate and rotate the AEC-ArmorStand pair
        to the specified position and rotation.

          - position: The position that the AEC-ArmorStand pair will be at relative to root_uuid
          - rotation: The rotation of the armor_stand
          - root_uuid: The UUID of the entity that the AEC-ArmorStand pair is positioned relative to.
        """
        q = Quaternion().between_vectors(self.size, self.t_pose)
        q.parent(rotation)

        commands = 'execute at ' + root_uuid + ' run tp ' + self.aec_uuid + ' ~' + ' ~'.join(
            ('{:f}'.format(i) for i in position.to_tuple())) + '\n'
        commands += 'data merge entity ' + self.aec_uuid + ' {Air: ' + str(int(self._update)) + '}\n'

        rot = list(Euler('zyx').set_from_quaternion(q).to_tuple())

        rot[1] *= -1
        rot[2] *= -1

        commands += 'data merge entity ' + self.stand_uuid + ' {Pose:{Head:' + utility.tuple_to_m_list(tuple(rot),
                                                                                                       'f') + '}}'

        self._update = self._update is False

        return commands
