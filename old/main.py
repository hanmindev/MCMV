import math
import os
import shutil
import sys
from typing import Optional, Union

import utility
from math_objects import Euler, Vector3, Quaternion
from entities import AecArmorStandPair, Armature, Bone, Frame, FrameBone, Stage


class MainConverter:
    """The main converter class.

    Instance Attributes:
          - function_directory: A string of the function directory (absolute).
          - scale: A float representing how much to scale the armature in Minecraft after the .bvh file's initial scaling
        during load.
          - current_armature: The Armature object currently being used.
          - stage: The Stage object currently being used. All armatures (and events, possibly in the future) are stored
          in here.
    """
    # Private Instance Attributes:
    # - _aec_stand_pairs: A dictionary mapping the function name to a dictionary mapping the minecraft
    # bone name to an AecArmorStandPair object
    # - _global_offset_fix: The position of the base bone passed through create_armature(). All positions for
    # an armature is subtracted by this value to center its initial position on the marker entity.
    # - _model_rotation: The final rotation quaternion applied to the whole armature.

    function_directory: str
    scale: float
    current_armature: Optional[Armature]
    stage: Stage

    _aec_stand_pairs: dict[str: dict[str: AecArmorStandPair]]
    _global_offset_fix: Optional[Vector3]
    _model_rotation: Quaternion

    def __init__(self, function_directory: str) -> None:
        """Initialize a new MainConverter class.
            WARNING: This will remove all folders in the directory
          - function_directory: A string of the function directory (absolute).
        """

        self.function_directory = function_directory
        self.scale = 1.0
        self.current_armature = None
        self.stage = Stage()

        self._aec_stand_pairs = {}
        self._global_offset_fix = Vector3(0.0, 0.0, 0.0)
        self._model_rotation = Quaternion(0.0, 0.0, 0.0, 1.0)

        # Ensure that the directory points into a Minecraft datapack folder.
        if 'functions' in function_directory and 'datapacks' in function_directory \
                and 'functions' not in function_directory[-10:len(function_directory)]:
            try:
                shutil.rmtree(function_directory)
            except FileNotFoundError:
                pass
        else:
            print('Directory name does not include \'functions\' or \'datapacks\' '
                  'or does not contain a folder following \'functions\' folder!'
                  ' Are you sure this is the right directory?')
            sys.exit()

    def load_file(self, file_path: str, scale: float, order: str = 'xyz',
                  max_frames: int = None, face_north: Quaternion = Quaternion(0.0, 0.0, 0.0, 1.0)) -> None:
        """Loads a .bvh file.
          - file_path: A string of the location of the .bvh file (relative).
          - scale: A float to scale the armature in the .bvh file by.
          - order: The Euler angle order that the .bvh file uses.
          - max_frames: The maximum number of frames that this function should generate. Negative integers will
          generate the maximum number of frames.
          - face_north: The rotation quaternion that should be applied to the model to face north inside Minecraft.
            All models must initially face north when being loaded to ensure everything works correctly. Armatures
            can later be rotated in any direction.
        """
        self._global_offset_fix = None
        self.scale = 1.0

        # Should probably change how this works later. Currently scale cannot be zero because zeroing a vector
        # causes it to lose information about its direction.
        scale = max(0.000000000000000001, scale)

        face_north_euler = Euler('xyz').set_from_quaternion(face_north)

        angle_x = math.radians(face_north_euler.x)
        angle_y = math.radians(face_north_euler.y)
        angle_z = math.radians(face_north_euler.z)

        rot_matrix_x = lambda y, z: (
            y * math.cos(angle_x) - z * math.sin(angle_x), z * math.cos(angle_x) + y * math.sin(angle_x))
        rot_matrix_y = lambda x, z: (
            x * math.cos(angle_y) + z * math.sin(angle_y), z * math.cos(angle_y) - x * math.sin(angle_y))
        rot_matrix_z = lambda x, y: (
            x * math.cos(angle_z) - y * math.sin(angle_z), y * math.cos(angle_z) + x * math.sin(angle_z))

        with open(file_path, encoding='utf-8') as file:
            self.current_armature = Armature()
            parent_stack = []
            # name parent_name offset channel_names
            current_bone_data = [None, None, None, None]
            mode = 0
            total_frames = 0
            frame = 0
            include_frames = set()
            for line in file:
                words = line.split()
                if mode == 0:
                    if words[0] == 'HIERARCHY':
                        continue

                    elif words[0] == 'ROOT' or words[0] == 'JOINT' or words[0] == 'End':
                        if words[0] == 'End':
                            bone_name = 'End Site_' + current_bone_data[0]
                        else:
                            bone_name = ' '.join(words[1:len(words)])

                        if words[0] == 'ROOT':
                            self.current_armature.root_bone_name = bone_name
                            parent_name = None
                        else:
                            if current_bone_data[0] is not None:
                                self.current_armature.add_bone(*current_bone_data)
                            parent_name = parent_stack[-1]

                        current_bone_data = [bone_name, parent_name, None, None]

                    elif words[0] == '{':
                        parent_stack.append(bone_name)
                    elif words[0] == '}':
                        if current_bone_data[0] is not None:
                            self.current_armature.add_bone(*current_bone_data)
                            current_bone_data = [None, None, None, None]
                        parent_stack.pop()

                    elif words[0] == 'OFFSET':
                        offset = Vector3(*map(float, words[1: 4])) * scale
                        offset.rotate_by_quaternion(face_north)
                        current_bone_data[2] = offset

                    elif words[0] == 'CHANNELS':
                        count = int(words[1])
                        channels = tuple(words[2:count + 2])
                        current_bone_data[3] = channels

                    if len(parent_stack) == 0 and len(self.current_armature.bones) > 2:
                        mode = 1
                else:
                    if words[0] == 'MOTION':
                        pass
                    elif words[0] == 'Frames:':
                        total_frames = int(words[1])
                    elif words[0] == 'Frame' and words[1] == 'Time:':
                        fps = 1 / float(words[2])

                        # since Minecraft runs on 20TPS
                        skip_frames = fps / 20
                        total_minecraft_frames = math.ceil(total_frames / skip_frames)
                        include_frames = {int(i * skip_frames) for i in range(total_minecraft_frames)}

                    elif len(words[0]) == 0:
                        pass
                    else:
                        if max_frames is not None and len(
                                self.current_armature.frames) >= max_frames >= 0:
                            break
                        if frame in include_frames:
                            index_start = 0

                            new_frame = Frame()

                            for bone_name in self.current_armature.bones:
                                bone = self.current_armature.bones[bone_name]
                                if bone.channel_names is not None:
                                    channel_count = len(bone.channel_names)
                                else:
                                    channel_count = 0

                                index_end = index_start + channel_count

                                channels = tuple(map(float, words[index_start:index_end]))
                                channel_mapper = {bone.channel_names[i]: channels[i] for i in range(channel_count)}

                                try:
                                    x_pos = channel_mapper['Xposition']
                                    y_pos = channel_mapper['Yposition']
                                    z_pos = channel_mapper['Zposition']
                                    position = Vector3(x_pos, y_pos, z_pos) * scale
                                    position.rotate_by_quaternion(face_north)
                                except KeyError:
                                    position = None

                                try:
                                    x_rot = channel_mapper['Xrotation']
                                    y_rot = channel_mapper['Yrotation']
                                    z_rot = channel_mapper['Zrotation']
                                    rotation = Quaternion().set_from_euler(Euler(order, x_rot, y_rot, z_rot))

                                    rotation.x, rotation.y = rot_matrix_z(rotation.x, rotation.y)
                                    rotation.x, rotation.z = rot_matrix_y(rotation.x, rotation.z)
                                    rotation.y, rotation.z = rot_matrix_x(rotation.y, rotation.z)
                                except KeyError:
                                    rotation = None

                                index_start = index_end

                                new_frame.frame_bones[bone_name] = FrameBone(bone_name, bone, position, rotation)

                            self.current_armature.frames.append(new_frame)
                        frame += 1

    def create_armature(self, function_name: str, uuid: str = None, offset: Vector3 = Vector3(0.0, 0.0, 0.0),
                        rotate=Quaternion(0.0, 0.0, 0.0, 1.0),
                        show_names: bool = False, scale: float = 1.0,
                        stands: list[tuple[Optional[str], Optional[Union[Vector3, str]], str,
                                           Vector3,
                                           Vector3
                        ]] = None, fill_in: bool = False,
                        base: str = None, center: bool = True,
                        allow_rotation=False) -> None:
        """Creates an instance of an armor_stand armature and writes functions that will manipulate the armature of name
         function_name. This function does not write the function to summon the armor stand however.

          - function_name: Name of the Minecraft function (e.g. could be name of the character, armature_001, etc)
            uuid: UUID of the root entity that the armature is positioned at.
            (e.g. 54e5e739-9221-45fc-a06f-b5326d174cf7)
          - offset: A vector representing the offset from the root entity the model should be positioned at.
            If uuid is None, this will be the offset from world origin (0, 0, 0).
          - rotate: A quaternion representing the rotation that the armature should be rotated by.
          - show_names: Whether to show bone names in Minecraft for debugging purposes.
          - scale: How much to scale the generated armature by. This does not affect bones with a redefined size.
            This scale is additional to the initial scale done on the .bvh model in load_file()

          - stands: A list of tuples containing information for an AEC-ArmorStand Pair:
              - Name of the starting bone (Should be the same name used in the .bvh file).
                    If left blank will the ending bone's parent.
              - Name of the ending bone (Should be the same name used in the .bvh file.)
                    If left blank will use the first child of the ending bone.
                            Optionally, rather than a bone name, a vector can be given to create a "dummy" bone.
                            Useful if the initial pose of the armature bone is irregular. This vector represents
                            the direction that this bone should be facing when the model is in a default pose (e.g.
                            t-pose, A-pose)
              - A string representation of the Minecraft item to be displayed. (e.g. diamond_hoe{CustomModelData:100})
              - The size of the bone as a Vector3 object
              - The offset of the bone as a Vector3 object
          - fill_in: Whether to fill in the missing AEC-ArmorStand Pairs. Filled in bones will use end_rod blocks.
          - base: Name of the base of the model. This will be used to center the armature.
          - allow_rotation: Setting this to True causes it to be slightly more performance intensive. Allows for
            rotating of the root entity that the armature is positioned at to rotate the armature as a whole.
            If disabled, rotation of the root entity will cause the armature to appear disconnected, and will require
            the reset function to be run. In the game, you can copy the rotation of the root entity (x rotation
            must be 0) to the armor stands to emulate this.

        """
        # import all the armor stands
        self._aec_stand_pairs[function_name] = {}

        self.scale = scale
        self._model_rotation = rotate
        original_end_bone_names = set()

        aec_stand_pairs = {}
        if stands is None:
            stands = []
        for stand in stands:
            if stand[0] is None and stand[1] is None:
                assert 'At least one of the bone\'s joint names must be defined!'

            if stand[0] is None:
                end_bone = self.current_armature.bones[stand[1]]
                start_bone = self.current_armature.bones[stand[1]].parent
            elif stand[1] is None or type(stand[1]) is Vector3:
                end_bone = self.current_armature.bones[stand[0]].children[0]
                start_bone = self.current_armature.bones[stand[0]]
            else:
                end_bone = self.current_armature.bones[stand[1]]
                start_bone = self.current_armature.bones[stand[0]]

            aec_stand_pairs[end_bone.bone_name] = AecArmorStandPair(
                (self.function_directory, function_name),
                uuid,
                stand[2],  # item
                start_bone,  # start bone
                stand[3],  # size
                stand[4],  # offset
                end_bone,  # t-pose helper
                show_names,
                allow_rotation
            )
            if type(stand[1]) is Vector3:
                aec_stand_pairs[end_bone.bone_name].t_pose = stand[1]
            original_end_bone_names.add(end_bone.bone_name)

        if fill_in:
            for stand_name in set(self.current_armature.bones.keys()).difference(set(aec_stand_pairs.keys())):
                start_bone = self.current_armature.bones[stand_name].parent
                end_bone = self.current_armature.bones[stand_name]

                if start_bone is None:
                    continue

                new_aec_stand_pair = AecArmorStandPair(
                    (self.function_directory, function_name),
                    uuid,
                    'end_rod',
                    start_bone,
                    Vector3(0.0, math.sqrt(2) / 2, math.sqrt(2) / 2) * end_bone.offset.magnitude(),
                    Vector3(0.0, 0.0, 0.0),
                    end_bone,
                    show_names,
                    allow_rotation
                )
                aec_stand_pairs[end_bone.bone_name] = new_aec_stand_pair

        useful_bones = set()

        def add_parents(bone_name: str) -> None:
            if bone_name not in useful_bones:
                useful_bones.add(bone_name)
                parent = self.current_armature.bones[bone_name].parent
                if parent is not None:
                    add_parents(parent.bone_name)

        for stand_bone_name in set(aec_stand_pairs.keys()):
            add_parents(stand_bone_name)

        try:
            os.mkdir(self.function_directory)
        except FileExistsError:
            pass
        try:
            os.mkdir(os.path.join(self.function_directory, function_name))
        except FileExistsError:
            pass
        self._global_offset_fix = None

        frames = self.current_armature.frames

        for ticks, frame in enumerate(frames):
            if ticks == 0:
                if base is not None and center:
                    self._global_offset_fix = self._find_center_offset_global_frame_armature(frame, aec_stand_pairs,
                                                                                             original_end_bone_names,
                                                                                             base)
                else:
                    self._global_offset_fix = Vector3(0.0, 0.0, 0.0)

            # per function

            complete_path = os.path.join(self.function_directory, function_name, str(ticks) + ".mcfunction")
            open(complete_path, 'w').close()
            g = open(complete_path, "a")

            for command in self._globalize_frame_armature(frame, aec_stand_pairs,
                                                          original_end_bone_names, base, offset):
                g.write(command + "\n")

        self._aec_stand_pairs[function_name] = aec_stand_pairs
        self.stage.update(function_name, self.current_armature)

    def _find_center_offset_global_frame_armature(self, frame: Frame, aec_stand_pairs: dict[str, AecArmorStandPair],
                                                  original_end_bone_names: set, base: str = None) -> Vector3:
        """Return a vector pointing from the root to the armature's base. Much of this function looks similar to
        _globalize_frame_armature(), because it does the same thing, but only to find the position of the base.
          - frame: A Frame object representing the first frame of the animation
          - aec_stand_pairs: A dictionary mapping ending bone names to an AEC-Stand pair.
          - original_end_bone_names: A set containing all initially defined AEC-Stand bones. Used to exclude generated
          bones.
          - base: The base bone of the armature.
        """

        def dfs(parent_frame_bone: FrameBone, parent_pos: Vector3, parent_rot: Quaternion,
                grandparent_rot: Quaternion = None,
                last_stand_bone_rot: Quaternion = None, last_stand: AecArmorStandPair = None,
                translate: bool = False) -> Vector3:
            """Traverse through the Armature from the root until the base is found, rotating bones appropriately
            such that the base bone's location can be accurately found.
              - parent_frame_bone: The current FrameBone object the search is checking.
              - parent_pos: A Vector representing the position of the parent bone
              - parent_rot: A Quaternion representing the rotation of the parent bone
              - grandparent_rot: A Quaternion representing the rotation of the grandparent bone
              - last_stand_bone_rot: A Quaternion representing the rotation of the last visible bone.
              - last_stand: The closest ancestor AecArmorStandPair object.
              - translate: Whether the model will move from its base (e.g. walk around).
            """
            # recursion
            parent_bone = parent_frame_bone.bone
            child_bones = parent_bone.children

            for child_bone in child_bones:
                is_defined_bone = child_bone.bone_name in aec_stand_pairs
                is_generated_bone = child_bone.bone_name not in original_end_bone_names
                child_frame_bone = frame.frame_bones[child_bone.bone_name]

                bone_end_pos = parent_pos.copy()
                if is_defined_bone:
                    bone_start_pos = parent_pos.copy()
                    if is_generated_bone:
                        try:
                            bone_end_pos = bone_start_pos + child_frame_bone.position.rotated_by_quaternion(
                                parent_rot) * self.scale
                        except AttributeError:
                            bone_end_pos = bone_start_pos.copy()
                    else:
                        # account for the model vector and t pose differences

                        # these following offset is armor stand specific
                        child_aec_stand = aec_stand_pairs[child_bone.bone_name]
                        q = child_aec_stand.q_size_to_t_pose.copy()

                        q.parent(parent_rot)
                        if last_stand is not None:

                            q_2 = last_stand_bone_rot.copy()

                            q_3 = last_stand.q_size_to_t_pose.copy()
                            q_3.parent(q_2)

                        else:
                            q_3 = grandparent_rot.copy()

                        offset_finalized = child_aec_stand.offset.copy().rotated_by_quaternion(q_3)

                        bone_start_pos += offset_finalized

                        bone_end_pos = bone_start_pos + child_aec_stand.size.copy().rotated_by_quaternion(q)

                        last_stand_bone_rot = parent_rot.copy()
                        last_stand = child_aec_stand

                elif translate and child_frame_bone.bone_name[0:9] != 'End Site_':
                    try:
                        bone_end_pos += child_frame_bone.position.rotated_by_quaternion(parent_rot) * self.scale
                    except AttributeError:
                        bone_end_pos += child_frame_bone.position * self.scale

                if translate and parent_bone.bone_name == base:
                    translate = False
                    if self._global_offset_fix is None:
                        return bone_end_pos
                if child_frame_bone.bone_name[0:9] != 'End Site_':
                    child_rot = child_frame_bone.rotation.copy()
                    child_rot.parent(parent_rot)
                    possible_global_offset = dfs(child_frame_bone, bone_end_pos, child_rot, parent_rot,
                                                 last_stand_bone_rot,
                                                 last_stand, translate=translate)
                    if possible_global_offset is not None:
                        return possible_global_offset

        initial_frame_bone = frame.frame_bones[self.current_armature.root_bone_name]
        # initial position + offset (defined by function) + shift vector to account for armor stand height
        origin = (initial_frame_bone.position.copy() * self.scale)
        origin_rot = initial_frame_bone.rotation.copy()
        return dfs(initial_frame_bone, origin, origin_rot, translate=base is not None) + Vector3(0.0, -1.4, 0.0)

    def _globalize_frame_armature(self, frame: Frame, aec_stand_pairs: dict[str, AecArmorStandPair],
                                  original_end_bone_names: set, base: str = None,
                                  offset: Vector3 = Vector3(0.0, 0.0, 0.0)) -> list[str]:
        """Return a list of commands that would manipulate the position and rotation of each entity in every
        AecArmorStandPair to make the armature animate the current frame.
          - frame: A Frame object representing the first frame of the animation
          - aec_stand_pairs: A dictionary mapping ending bone names to an AEC-Stand pair.
          - original_end_bone_names: A set containing all initially defined AEC-Stand bones. Used to exclude generated
          bones.
          - base: The base bone of the armature.
          - offset: The global offset of the armature.
        """

        def dfs(parent_frame_bone: FrameBone, parent_pos: Vector3, parent_rot: Quaternion,
                grandparent_rot: Quaternion = None,
                last_stand_bone_rot: Quaternion = None, last_stand: AecArmorStandPair = None,
                translate: bool = False) -> list[str]:
            """Traverse through the Armature from the root until the base is found, rotating bones appropriately
            such that the base bone's location can be accurately found.
              - parent_frame_bone: The current FrameBone object the search is checking.
              - parent_pos: A Vector representing the position of the parent bone
              - parent_rot: A Quaternion representing the rotation of the parent bone
              - grandparent_rot: A Quaternion representing the rotation of the grandparent bone
              - last_stand_bone_rot: A Quaternion representing the rotation of the last visible bone.
              - last_stand: The closest ancestor AecArmorStandPair object.
              - translate: Whether the model will move from its base (e.g. walk around).
            """
            commands = []
            # recursion
            parent_bone = parent_frame_bone.bone
            child_bones = parent_bone.children

            for child_bone in child_bones:
                is_defined_bone = child_bone.bone_name in aec_stand_pairs
                is_generated_bone = child_bone.bone_name not in original_end_bone_names
                child_frame_bone = frame.frame_bones[child_bone.bone_name]

                bone_end_pos = parent_pos.copy()
                if is_defined_bone:
                    bone_start_pos = parent_pos.copy()
                    if is_generated_bone:
                        try:
                            bone_end_pos = bone_start_pos + child_frame_bone.position.rotated_by_quaternion(
                                parent_rot) * self.scale
                        except AttributeError:
                            bone_end_pos = bone_start_pos.copy()
                    else:
                        # account for the model vector and t pose differences

                        # these following offset is armor stand specific
                        child_aec_stand = aec_stand_pairs[child_bone.bone_name]
                        q = child_aec_stand.q_size_to_t_pose.copy()

                        q.parent(parent_rot)
                        if last_stand is not None:

                            q_2 = last_stand_bone_rot.copy()

                            q_3 = last_stand.q_size_to_t_pose.copy()
                            q_3.parent(q_2)

                        else:
                            q_3 = grandparent_rot.copy()

                        offset_finalized = child_aec_stand.offset.copy().rotated_by_quaternion(q_3)

                        bone_start_pos += offset_finalized

                        bone_end_pos = bone_start_pos + child_aec_stand.size.copy().rotated_by_quaternion(q)

                        last_stand_bone_rot = parent_rot.copy()
                        last_stand = child_aec_stand

                    resulting_position = bone_start_pos.copy()
                    resulting_rotation = parent_rot.copy()

                    resulting_position -= self._global_offset_fix

                    resulting_position.rotate_by_quaternion(self._model_rotation)
                    resulting_rotation.parent(self._model_rotation)

                    resulting_position += external_offset

                    commands += aec_stand_pairs[child_bone.bone_name].return_transformation_command(
                        resulting_position,
                        resulting_rotation)

                elif translate and child_frame_bone.bone_name[0:9] != 'End Site_':
                    try:
                        bone_end_pos += child_frame_bone.position.rotated_by_quaternion(parent_rot) * self.scale
                    except AttributeError:
                        bone_end_pos += child_frame_bone.position * self.scale

                if child_frame_bone.bone_name[0:9] != 'End Site_':
                    child_rot = child_frame_bone.rotation.copy()
                    child_rot.parent(parent_rot)
                    if translate and parent_bone.bone_name == base:
                        translate = False
                    commands += dfs(child_frame_bone, bone_end_pos, child_rot, parent_rot, last_stand_bone_rot,
                                    last_stand, translate=translate)

            return commands

        initial_frame_bone = frame.frame_bones[self.current_armature.root_bone_name]
        # initial position + offset (defined by function) + shift vector to account for armor stand height
        external_offset = offset + Vector3(0.0, -1.4, 0.0)
        origin = (initial_frame_bone.position.copy() * self.scale)
        origin_rot = initial_frame_bone.rotation.copy()
        return dfs(initial_frame_bone, origin, origin_rot, translate=base is not None)

    def create_debug_armature(self, function_name: str, uuid: str = None, offset: Vector3 = Vector3(0.0, 0.0, 0.0),
                              rotate: Quaternion = Quaternion(0.0, 0.0, 0.0, 1.0),
                              show_names: bool = False, scale: float = 1.0) -> None:
        """Creates an instance of an debug armature and writes functions that will display blocks where the bones should
        be. The function generated by this is significantly more performance heavy than create_armature(), and thus
        should only be used for debugging or models with little bone count.

        All parameters are same as the parameters in create_armature().
        """
        function_name = function_name + '_debug'
        self.scale = scale
        try:
            os.mkdir(self.function_directory)
        except FileExistsError:
            pass
        try:
            os.mkdir(os.path.join(self.function_directory, function_name))
        except FileExistsError:
            pass
        self._global_offset_fix = None

        frames = self.current_armature.frames
        self._model_rotation = rotate

        for ticks, frame in enumerate(frames):
            if ticks == 0:
                self._global_offset_fix = frame.frame_bones[
                                              self.current_armature.root_bone_name].position * self.scale

            # per function

            complete_path = os.path.join(self.function_directory, function_name, str(ticks) + ".mcfunction")
            open(complete_path, 'w').close()
            g = open(complete_path, "a")

            for command in self._debug_armature_construction(frame, offset - self._global_offset_fix, function_name,
                                                             show_names, uuid):
                g.write(command + "\n")

        self.stage.update(function_name, self.current_armature)

    def _debug_armature_construction(self, frame: Frame, position: Vector3, function_name: str, show_names: bool,
                                     uuid: str = None):
        """Writes commands to display blocks at where each bone should be displayed.
            Parameters are the same as the ones in _globalize_frame_armature().
        """
        commands = ['kill @e[type=falling_block,tag=armature_sand,tag=' + function_name + ']']

        if uuid is None:
            pre_command = 'summon minecraft:falling_block {} {} {} '
        else:
            pre_command = 'execute at ' + uuid + ' run summon minecraft:falling_block ^{} ^{} ^{} '

        def dfs(parent_frame_bone: FrameBone, parent_pos: Vector3, parent_rot: Quaternion) -> None:

            # recursion
            bone = parent_frame_bone.bone
            children = bone.children

            for child_bone in children:
                child_frame_bone = frame.frame_bones[child_bone.bone_name]
                if child_frame_bone.bone_name[0:9] == 'End Site_':
                    child_pos_rel = child_bone.offset.copy()
                    child_rot = Quaternion(0.0, 0.0, 0.0, 1.0)
                else:
                    child_pos_rel = child_frame_bone.position.copy()

                    child_rot = child_frame_bone.rotation.copy()
                    child_rot.parent(parent_rot)

                child_pos_rel.rotate_by_quaternion(parent_rot)

                real_length = (child_pos_rel.magnitude() * self.scale)

                if real_length > 1.0:

                    vector_step = child_pos_rel.normalized()

                    # in between stone
                    for i in range(int(real_length)):
                        resulting_position = parent_pos * self.scale + vector_step * (i + 1.0)

                        resulting_position += position
                        resulting_position.rotate_by_quaternion(self._model_rotation)

                        xyz = ('{:f}'.format(j) for j in resulting_position)

                        commands.append(
                            pre_command.format(*xyz) +
                            ' {Tags:[\'armature_sand\',\'' + function_name + '\'],NoGravity:true,BlockState:{'
                                                                             'Name:"minecraft:stone"}}')

                child_pos = parent_pos + child_pos_rel
                resulting_position = child_pos * self.scale
                resulting_position += position
                resulting_position.rotate_by_quaternion(self._model_rotation)

                xyz = ('{:f}'.format(i) for i in resulting_position)

                # node
                commands.append(
                    pre_command.format(*xyz) +
                    ' {Tags:[\'armature_sand\',\'' + function_name + '\'],NoGravity:true,BlockState:{'
                                                                     'Name:"minecraft:diamond_block"},'
                                                                     'CustomNameVisible: ' + str(1) * show_names +
                    'b, CustomName: \'{"text": " ' + child_bone.bone_name + '"}\'' + '}')

                if child_frame_bone.bone_name[0:9] != 'End Site_':
                    dfs(child_frame_bone, child_pos, child_rot)

        initial_frame_bone = frame.frame_bones[self.current_armature.root_bone_name]
        origin = Vector3(0, 0, 0)
        origin_rot = Quaternion(0, 0, 0, 1)
        dfs(initial_frame_bone, origin, origin_rot)
        return commands

    def search_function(self, selector_objective: str = 'global animation_time') -> None:
        """Write commands to index the correct .mcfunction file to run the animation.
        Search is O(log2(N)) with N being the number of frames (utilizes a binary search).
        """
        max_ticks = self.stage.max_ticks

        try:
            os.mkdir(os.path.join(self.function_directory, 'search'))
        except FileExistsError:
            pass

        for ticks in range(max_ticks):
            search_path = os.path.join(self.function_directory, 'search', str(ticks) + ".mcfunction")
            g = open(search_path, "a")
            for function_name in self.stage.armatures:
                g.write('function ' + utility.get_function_directory(
                    self.function_directory, function_name) + '/' + str(ticks) + '\n')
            g.close()

        def construct_binary_tree(left: int, right: int, os_directory: str, function_directory: str, id: int) -> str:
            if right == left:
                pre_command = 'execute if score ' + selector_objective + ' matches ' + str(right) + ' run '
                return pre_command + 'function ' + function_directory + '/' + str(right) + '\n'
            else:
                complete_path = os.path.join(os_directory, 'b' + str(id) + ".mcfunction")
                f = open(complete_path, "a")

                middle = left + (right - left) // 2
                f.write(construct_binary_tree(left, middle, os_directory, function_directory, id * 2))
                f.write(construct_binary_tree(middle + 1, right, os_directory, function_directory, id * 2 + 1))

                pre_command = 'execute if score ' + selector_objective + ' matches ' + str(left) + '..' + str(
                    right) + ' run '
                return pre_command + 'function ' + function_directory + '/b' + str(id) + '\n'

        complete_path = os.path.join(self.function_directory, 'main' + ".mcfunction")
        f = open(complete_path, "a")
        f.write(construct_binary_tree(
            0, max_ticks, os.path.join(self.function_directory, 'search'), utility.get_function_directory(
                self.function_directory, 'search'), 1))

        f.close()

    def reset_function(self) -> None:
        """Write commands to remove and summon necessary AEC-Stand pairs.
        """
        complete_path = os.path.join(self.function_directory, 'reset' + ".mcfunction")
        f = open(complete_path, "a")
        try:
            tags = next(iter(next(iter(self._aec_stand_pairs.values())).values())).common_tags.copy()
            commands = ['kill @e[tag=' + ',tag='.join(tags) + ']']

            for function_name in self._aec_stand_pairs:
                for aec_stand_pair in self._aec_stand_pairs[function_name]:
                    commands += self._aec_stand_pairs[function_name][aec_stand_pair].return_reset_commands()
                f.write('\n'.join(commands) + '\n')
        except StopIteration:
            f.write('tellraw @a [{"text":"[Debug] ","color":"red"},{"text":"There aren\'t any bones in '
                    'this Armature!","color":"white"}]')
        f.close()

    def remove_function(self) -> None:
        """Write commands to remove necessary AEC-Stand pairs."""
        complete_path = os.path.join(self.function_directory, 'remove' + ".mcfunction")

        f = open(complete_path, "a")
        try:
            tags = next(iter(next(iter(self._aec_stand_pairs.values())).values())).common_tags.copy()
            f.write('kill @e[tag=' + ',tag='.join(tags) + ']')
        except StopIteration:
            f.write('tellraw @a [{"text":"[Debug] ","color":"red"},{"text":"There aren\'t any bones in '
                    'this Armature!","color":"white"}]')
        f.close()
