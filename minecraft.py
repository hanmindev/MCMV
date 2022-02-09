from armature import Bone

class AecArmorStandPair:
    """A class describing an AEC-ArmorStand pair.

    Instance Attributes:
      - name: Name of the bone (as defined in the .bvh file). Should be the name of the ending joint in a bone.
      - start_bone: The starting bone. Should be the parent of end_bone.
      - end_bone: The ending bone. Should be a child of start_bone.
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
    #  - _seed_prefix: The seed value to create the UUID for the armor stand and the area effect cloud.

    name: str
    start_bone: Bone
    end_bone: Bone
    aec_uuid: str
    stand_uuid: str
    size: Vector3
    offset: Vector3
    t_pose: Vector3
    item: str

    _update: bool
    _seed_prefix: str

    def __init__(self, seed_prefix: tuple[str, str], root_uuid: str,
                 item: str, start_bone: Bone, size: Vector3, offset: Vector3, end_bone: Bone, show_names: bool,
                 allow_rotation: bool) -> None:
        self.name = end_bone.bone_name
        self.start_bone = start_bone
        self._seed_prefix = utility.get_function_directory(*seed_prefix).replace(' ', '_')
        self.root_uuid = root_uuid

        self.aec_uuid, self.stand_uuid = utility.get_joint_uuids(*seed_prefix, self.name)

        # vector of the bone
        self.size = size
        # vector of the offset of the bone
        self.offset = offset
        self.end_bone = end_bone
        self.t_pose = end_bone.offset

        if self.size.magnitude() != 0 and self.t_pose.magnitude() != 0:
            q_size_to_t_pose = Quaternion().between_vectors(self.size, self.t_pose)
            self.q_size_to_t_pose = q_size_to_t_pose
        else:
            self.q_size_to_t_pose = Quaternion(0.0, 0.0, 0.0, 1.0)

        # name of the item to hold
        self.item = item
        self.show_names = show_names

        self.allow_rotation = allow_rotation

        tag = self._seed_prefix.split('/')
        self.common_tags = {'armature_stands', 'path_' + tag[0].replace(':', '_'),
                            'path_' + self._seed_prefix.replace(':', '_').replace('/', '_')}

        self._update = True

    def __repr__(self) -> str:
        """Return a string representation of the AecArmorStandPair object for debugging purposes."""
        return 'AEC-AS Object: ' + self.name

    def return_reset_commands(self) -> list[str]:
        """Return a list of commands to reset the AEC-Stand pair."""

        tags = self.common_tags.copy()
        tags.add('bn_' + self.name.replace(' ', '_'))

        commands = ['kill ' + self.aec_uuid,
                    'kill ' + self.stand_uuid,
                    'summon area_effect_cloud ~ ~ ~ {Tags:[' + ','.join(
                        '\"' + i + '\"' for i in tags) + '],Duration:2147483647,' + utility.uuid_str_to_uuid_nbt(
                        self.aec_uuid) + ',Passengers:[{id:"minecraft:armor_stand",Tags:[' + ','.join(
                        '\'' + i + '\'' for i in tags) + '],DisabledSlots:4144959,Invisible:1,'
                                                         '' + utility.uuid_str_to_uuid_nbt(
                        self.stand_uuid) + ',CustomNameVisible: ' + str(
                        1 * self.show_names) + 'b, '
                                               'CustomName: \'{"text": "'
                                               '' + self.name + '"}\' }]}',
                    'item replace entity ' + self.stand_uuid + ' armor.head with ' + self.item]

        if self.root_uuid is not None:
            commands.append(
                'execute at ' + self.stand_uuid + ' rotated as ' + self.root_uuid + ' run tp ' + self.stand_uuid + ' ~ ~ ~ ~ ~')
        return commands

    def return_transformation_command(self, position: Vector3, rotation: Quaternion) -> list[str]:
        """Return commands as a single string that translate and rotate the AEC-ArmorStand pair
        to the specified position and rotation.

          - position: The position that the AEC-ArmorStand pair will be at relative to root_uuid
          - rotation: The rotation of the armor_stand
          - root_uuid: The UUID of the entity that the AEC-ArmorStand pair is positioned relative to.
        """
        q = self.q_size_to_t_pose.copy()

        q.parent(rotation)

        if self.root_uuid is None:
            commands = [
                'tp ' + self.aec_uuid + ' {} {} {}'.format(
                    *('{:f}'.format(i) for i in position.to_tuple()))
            ]
        else:
            commands = [
                'execute at ' + self.root_uuid + ' run tp ' + self.aec_uuid + ' ^{} ^{} ^{}'.format(
                    *('{:f}'.format(i) for i in position.to_tuple())) + ' ~ ~'
            ]
            if self.allow_rotation:
                commands.append(
                    'execute at ' + self.stand_uuid + ' rotated as ' + self.
                    root_uuid + ' run tp ' + self.stand_uuid + ' ~ ~ ~ ~ ~'
                )

        commands.append('data merge entity ' + self.aec_uuid + ' {Air: ' + str(int(self._update)) + '}')

        rot = list(Euler('zyx').set_from_quaternion(q).to_tuple())

        # I'm really confused why Minecraft armor stand poses are Euler zyx but y and z are negative. Or I did the math
        # wrong but it works so /shrug
        rot[1] *= -1
        rot[2] *= -1

        commands.append(
            'data merge entity ' + self.stand_uuid + ' {Pose:{Head:' + utility.tuple_to_m_list(tuple(rot), 'f') + '}}')

        self._update = self._update is False

        return commands