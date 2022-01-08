import math
import os
import shutil
import sys
from typing import Optional

import utility
from entities import AecArmorStandPair, Bone, FrameBone, Frame, GlobalBone
from math_objects import Euler, Vector3, Quaternion


class MainConverter:
    """The main converter class.

    Instance Attributes:
      - function_directory: The full directory for where all the functions are going to be placed.
      - scale: A float representing the scale of the .bvh model to Minecraft.
      - bones: A dictionary mapping bone_name strings to Bone objects.
      - frames: A list of Frame objects, such that the index is the frame number.
    """
    # Private Instance Attributes:
    # - _bone_list: A list of strings of bone names in the order they were read.
    # - _aec_stand_pairs: A dictionary mapping the function name to a dictionary mapping the minecraft
    # bone name to an AecArmorStandPair object
    # - _global_offset_fix: The position of the first AecArmorStandPair in the first frame. Later used
    # to offset coordinates such that the created armature is positioned at the root entity.
    # - _commands_to_index: A dictionary mapping function name to an integer representing the length of
    # the animation in ticks,
    # - _useful_bones: A set of all bones to be read in the program.
    # - _order: The Euler rotation order for this file.
    # - _frame_time: Seconds between frames.
    # - _root_bone: The root bone.

    function_directory: str
    scale: float
    bones: dict[str, Bone]
    frames: list[Frame]

    _bone_list: list[str]
    _aec_stand_pairs: dict[str: dict[str: AecArmorStandPair]]
    _global_offset_fix: Optional[Vector3]
    _commands_to_index: dict[str: int]
    _useful_bones: set
    _order: Optional[str]
    _frame_time: Optional[float]
    _root_bone: Optional[str]

    def __init__(self, function_directory: str) -> None:
        """Initialize a new MainConverter class.
            This will remove all folders in the directory

            function_directory: A string of the function directory (absolute).
        """
        self.function_directory = function_directory
        self.bones = {}
        self._bone_list = []
        self.frames = []
        self._aec_stand_pairs = {}
        self._global_offset_fix = None
        self._commands_to_index = {}
        self.scale = 1.0
        self._useful_bones = set()
        self._order = None
        self._frame_time = None
        self._root_bone = None
        self._fix_orientation = Quaternion(0.0, 0.0, 0.0, 1.0)

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

    def load_file(self, file_path: str, scale: float, order: str = 'xyz', up: str = 'y') -> None:
        """Loads a .bvh file.

            file_path: A string of the location of the .bvh file (relative).
            scale: A float representing the scale that the .bvh file should be
            scaled to in Minecraft.
        """
        self.bones = {}
        self._bone_list = []
        self.frames = []
        self.scale = scale
        self._global_offset_fix = None
        self._order = order
        self._root_bone = None
        self._fix_orientation = Quaternion(0.0, 0.0, 0.0, 1.0)

        unit_vectors = {
            'x': Vector3(1.0, 0.0, 0.0),
            'y': Vector3(0.0, 1.0, 0.0),
            'z': Vector3(0.0, 0.0, 1.0),
            '-x': Vector3(-1.0, 0.0, 0.0),
            '-y': Vector3(0.0, -1.0, 0.0),
            '-z': Vector3(0.0, 0.0, -1.0)
        }

        if up != 'y':
            rotate_from = unit_vectors[up].copy()
            rotate_to = Vector3(0.0, 1.0, 0.0)
            self._fix_orientation = Quaternion().between_vectors(rotate_from, rotate_to)

        with open(file_path, encoding='utf-8') as file:
            parent_stack = []
            mode = 0
            for line in file:
                words = line.split()
                if mode == 0:
                    if words[0] == 'HIERARCHY':
                        continue

                    elif words[0] == 'ROOT' or words[0] == 'JOINT' or words[0] == 'End':
                        bone_name = ' '.join(words[1:len(words)])
                        if words[0] == 'ROOT':
                            self._root_bone = bone_name

                        self.bones[bone_name] = Bone(bone_name)
                        if len(parent_stack) > 0:
                            self.bones[bone_name].parent = parent_stack[-1]
                            self.bones[parent_stack[-1]].children.add(bone_name)
                        self._bone_list.append(bone_name)
                        parent_stack.append(bone_name)

                    elif words[0] == '{':
                        continue
                    elif words[0] == '}':
                        parent_stack.pop()

                    elif words[0] == 'OFFSET':
                        offset = list(map(float, words[1: 4]))
                        try:
                            self.bones[parent_stack[-1]].offset = Vector3(*offset)
                        except IndexError:
                            pass
                        try:
                            self.bones[parent_stack[-2]].size = Vector3(*offset)
                        except IndexError:
                            pass

                    elif words[0] == 'CHANNELS':
                        count = int(words[1])
                        channels = tuple(words[2:count + 2])

                        this_bone = self.bones[parent_stack[-1]]
                        this_bone.channel_count = count
                        this_bone.channel_names = channels
                    if len(parent_stack) == 0 and len(self.bones) > 2:
                        mode = 1
                else:
                    if words[0] == 'MOTION' or words[0] == 'Frames:':
                        pass
                    elif words[0] == 'Frame' and words[1] == 'Time:':
                        self._frame_time = float(words[2])
                    elif len(words[0]) == 0:
                        pass
                    else:
                        index_start = 0
                        self.frames.append(Frame())
                        for bone_name in self._bone_list:
                            if bone_name == 'Site':
                                continue
                            bone = self.bones[bone_name]
                            index_end = index_start + bone.channel_count

                            channels = tuple(map(float, words[index_start:index_end]))

                            channel_mapper = {bone.channel_names[i]: channels[i] for i in range(bone.channel_count)}

                            x_pos = channel_mapper['Xposition']
                            y_pos = channel_mapper['Yposition']
                            z_pos = channel_mapper['Zposition']

                            x_rot = channel_mapper['Xrotation']
                            y_rot = channel_mapper['Yrotation']
                            z_rot = channel_mapper['Zrotation']

                            index_start = index_end

                            position = Vector3(x_pos, y_pos, z_pos)
                            rotation = Quaternion().set_from_euler(Euler(self._order, x_rot, y_rot, z_rot))

                            self.frames[-1].frame_bones[bone.bone_name] = FrameBone(bone.bone_name, position, rotation)

    def globalize_frame_armature(self, function_name: str, frame: Frame, initial_frame_bone_name: str) -> \
            dict[str, GlobalBone]:
        """Loads a .bvh file.

            function_name: Name of the Minecraft function (e.g. could be name of the character, armature_001, etc)
            frame: A single Frame object used to create the armature.
            initial_frame_bone_name: Name of the root bone (e.g. Root, PositionOffset, etc.)
            Should be dependent on the .bvh file.
        """
        armorstand_bone_set = set(self._aec_stand_pairs[function_name].keys())
        global positioned
        positioned = False
        fix_position = False
        if self._global_offset_fix is None:
            self._global_offset_fix = Vector3(0.0, 0.0, 0.0)
            fix_position = True

        def dfs(frame_bone: FrameBone, parent_pos: Vector3, parent_rot: Quaternion, fix_position: bool) -> None:
            global positioned
            # skip extra bones
            if frame_bone.bone_name not in self._useful_bones:
                return None

            # Fix the new rotation
            child_rot = frame_bone.rotation.copy()
            child_rot.parent(parent_rot)

            if positioned and frame_bone.bone_name not in armorstand_bone_set:
                # go deeper into graph with parent stuff. i.e. ignore this bone's rotation and stuff
                bone = self.bones[frame_bone.bone_name]
                children = bone.children

                for child in children:
                    if child == 'Site':
                        continue
                    dfs(frame.frame_bones[child], parent_pos, parent_rot, fix_position)
            else:
                if frame_bone.bone_name in armorstand_bone_set:
                    positioned = True

                    # Rotate the bone by the parent
                    this_aec_stand_pair = self._aec_stand_pairs[function_name][frame_bone.bone_name]
                    bone_offset_vector = this_aec_stand_pair.offset.copy()
                    bone_size_vector = this_aec_stand_pair.size.copy()
                    t_pose_vector = this_aec_stand_pair.t_pose.copy()

                    if bone_size_vector.magnitude() != 0 and t_pose_vector.magnitude() != 0:
                        # account for bone size and t pose differences
                        q = Quaternion().between_vectors(bone_size_vector, t_pose_vector)
                        q.parent(child_rot)
                        bone_size_vector.rotate_by_quaternion(q)
                else:
                    # Rotate the bone by the parent
                    bone_offset_vector = frame_bone.position * self.scale
                    if fix_position:
                        self._global_offset_fix += bone_offset_vector
                    bone_size_vector = Vector3(0.0, 0.0, 0.0)

                if bone_offset_vector.magnitude() < 0.0001:
                    bone_offset_vector = Vector3(0.0, 0.0, 0.0)
                else:
                    bone_offset_vector.rotate_by_quaternion(parent_rot)

                child_pos = parent_pos + bone_offset_vector

                # pack
                frame_armature[frame_bone.bone_name] = GlobalBone(frame_bone.bone_name,
                                                                  child_pos, child_rot)

                # recursion
                bone = self.bones[frame_bone.bone_name]
                children = bone.children

                for child in children:
                    if child == 'Site':
                        continue
                    dfs(frame.frame_bones[child], child_pos + bone_size_vector, child_rot, fix_position)

        origin = Vector3(0, -1.25, 0)
        origin_rot = Quaternion(0, 0, 0, 1)
        frame_armature = {}

        initial_frame_bone = frame.frame_bones[initial_frame_bone_name]
        dfs(initial_frame_bone, origin, origin_rot, fix_position)

        return frame_armature

    def globalize_armature(self, function_name: str, root_uuid: str,
                           stands: list[tuple[str, str,
                                              Vector3,
                                              Vector3,
                                              Optional[Vector3]]], fill_in: bool = False, show_names: bool = False) -> None:
        """Loads a .bvh file.

            function_name: Name of the Minecraft function (e.g. could be name of the character, armature_001, etc)
            root_uuid: UUID of the root entity that the armature is positioned at.
            (e.g. 54e5e739-9221-45fc-a06f-b5326d174cf7)
            stands: A list of tuples containing information for an AEC-ArmorStand Pair:
                Name of the bone (Should be the same name used in the .bvh file.)
                UUID of the AEC (e.g. 2f9d6e9a-aaca-4964-9059-ec43f2016499)
                UUID of the Armor Stand (e.g. 19c4830d-8714-4e62-b041-0cde12b6de96)
                A string representation of the Minecraft item to be displayed. (e.g. diamond_hoe{CustomModelData:100})
                The size of the bone as a Vector3 object
                The offset of the bone as a Vector3 object
                The initial direction that the bone is facing
                    (e.g. in a T-Pose the right arm would be pointing directly right). This parameter is optional as
                    the .bvh file gives an approximation of what direction the bone is facing. However, you might want
                    to set your own if a bone seems to be rotated incorrectly.
        """
        # Calculates how many frames to skip since Minecraft commands run on 20Hz.
        minecraft_frames = 20
        initial_frame_bone_name = self._root_bone

        original_frames = 1 / self._frame_time
        skip_frames = round(original_frames / minecraft_frames)
        ticks = 0
        # import all the armor stands
        self._aec_stand_pairs[function_name] = {}

        self._useful_bones = set()
        stand_bone_names = set()

        for stand in stands:
            if stand[4] is None:
                self._aec_stand_pairs[function_name][stand[0]] = AecArmorStandPair(utility.get_function_directory(
                    self.function_directory, function_name), stand[0], stand[1], stand[2],
                    stand[3], self.bones[stand[0]].offset, show_names)
            else:
                self._aec_stand_pairs[function_name][stand[0]] = AecArmorStandPair(function_name, *stand[0:5], show_names)
            stand_bone_names.add(stand[0])

        if fill_in:
            remainder = set(self.bones.keys()).difference(stand_bone_names)
            for stand in remainder:
                if stand != 'Site':
                    self._aec_stand_pairs[function_name][stand] = AecArmorStandPair(utility.get_function_directory(
                        self.function_directory, function_name), stand, 'end_rod',
                        Vector3(0.0, math.sqrt(2), math.sqrt(2)) * self.bones[stand].offset.magnitude() * self.scale,
                        self.bones[stand].size * self.scale,
                        self.bones[stand].offset, show_names)
                    stand_bone_names.add(stand)

        def add_parents(bone_name: str) -> None:
            if bone_name not in self._useful_bones:
                self._useful_bones.add(bone_name)
                parent_bone = self.bones[bone_name].parent
                if parent_bone is not None:
                    add_parents(parent_bone)

        for stand_bone_name in stand_bone_names:
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

        for i in range(0, len(self.frames), skip_frames):

            # per tick file
            frame = self.frames[i]
            frame_armature = self.globalize_frame_armature(function_name, frame, initial_frame_bone_name)

            commands = []

            for stand_name in self._aec_stand_pairs[function_name]:
                aec_stand_pair = self._aec_stand_pairs[function_name][stand_name]
                global_bone = frame_armature[stand_name]

                command = aec_stand_pair.return_transformation_command(global_bone.position - self._global_offset_fix,
                                                                       global_bone.rotation, root_uuid,
                                                                       self._fix_orientation)

                commands.append(command)

            command = '\n'.join(commands)

            complete_path = os.path.join(self.function_directory, function_name, str(ticks) + ".mcfunction")
            open(complete_path, 'w').close()
            g = open(complete_path, "a")
            g.write(command)
            g.close()

            ticks += 1

        if function_name not in self._commands_to_index or self._commands_to_index[function_name] > ticks - 1:
            self._commands_to_index[function_name] = ticks - 1

    def reset_function(self) -> None:
        """Write commands to remove and summon necessary AEC-Stand pairs.
        """
        complete_path = os.path.join(self.function_directory, 'reset' + ".mcfunction")
        f = open(complete_path, "a")

        commands = []
        for function_name in self._aec_stand_pairs:
            for aec_stand_pair in self._aec_stand_pairs[function_name]:
                commands += self._aec_stand_pairs[function_name][aec_stand_pair].return_reset_commands()
            f.write('\n'.join(commands) + '\n')
        f.close()

    def debug_armature_construction(self, frame: Frame, position: Vector3, function_name: str, show_names: bool):
        commands = ['kill @e[type=falling_block,tag=armature_sand,tag=' + function_name + ']']

        def dfs(frame_bone: FrameBone, parent_pos: Vector3, parent_rot: Quaternion) -> None:
            # skip extra bones
            # if frame_bone.bone_name not in useful_bones:
            #     return None

            # Rotate the bone by the parent
            bone_vector = frame_bone.position.copy()
            if bone_vector.magnitude() != 0.0:
                bone_vector.rotate_by_quaternion(parent_rot)
            else:
                bone_vector = Vector3(0.0, 0.0, 0.0)

            # Fix the new rotation
            child_rot = frame_bone.rotation.copy()
            child_rot.parent(parent_rot)

            child_pos = parent_pos + bone_vector

            # display
            if frame_bone.bone_name not in {'Hip', 'PositionOffset'}:
                real_length = (bone_vector.magnitude() * self.scale)
                if real_length > 1.0:

                    vector_step = bone_vector.normalized()

                    # in between stone
                    for i in range(int(real_length)):
                        resulting_position = parent_pos * self.scale + vector_step * (i + 0.5)

                        resulting_position.rotate_by_quaternion(self._fix_orientation)

                        resulting_position += position

                        xyz = ('{:f}'.format(j) for j in resulting_position)

                        commands.append(
                            'summon minecraft:falling_block ' + ' '.join(xyz) +
                            ' {Tags:[\'armature_sand\',\'' + function_name + '\'],NoGravity:true,BlockState:{'
                                                                             'Name:"minecraft:stone"}}')

                resulting_position = child_pos * self.scale

                resulting_position.rotate_by_quaternion(self._fix_orientation)

                resulting_position += position

                xyz = ('{:f}'.format(i) for i in resulting_position)

                # node
                commands.append(
                    'summon minecraft:falling_block ' + ' '.join(xyz) +
                    ' {Tags:[\'armature_sand\',\'' + function_name + '\'],NoGravity:true,BlockState:{'
                                                                     'Name:"minecraft:diamond_block"}, '
                                                                     'CustomNameVisible: '+str(1) * show_names+'b, '
                                                                     'CustomName: \'{"text": "'
                                                                     '' + frame_bone.bone_name + '"}\'' + '}')

            # recursion
            bone = self.bones[frame_bone.bone_name]
            children = bone.children

            for child in children:
                if child == 'Site':
                    continue
                dfs(frame.frame_bones[child], child_pos, child_rot)

        initial_frame_bone = frame.frame_bones[self._root_bone]
        origin = Vector3(0, 0, 0)
        origin_rot = Quaternion(0, 0, 0, 1)
        dfs(initial_frame_bone, origin, origin_rot)
        return commands

    def create_debug_armature(self, function_name: str, position: Vector3, show_names: bool = False) -> None:
        # Calculates how many frames to skip since Minecraft commands run on 20Hz.
        minecraft_frames = 20
        initial_frame_bone_name = self._root_bone

        original_frames = 1 / self._frame_time
        skip_frames = round(original_frames / minecraft_frames)
        ticks = 0

        try:
            os.mkdir(self.function_directory)
        except FileExistsError:
            pass
        try:
            os.mkdir(os.path.join(self.function_directory, function_name))
        except FileExistsError:
            pass
        self._global_offset_fix = None

        for i in range(0, len(self.frames), skip_frames):
            frame = self.frames[i]
            if i == 0:
                self._global_offset_fix = frame.frame_bones[self._root_bone].position * self.scale

            # per function

            complete_path = os.path.join(self.function_directory, function_name, str(ticks) + ".mcfunction")
            open(complete_path, 'w').close()
            g = open(complete_path, "a")

            for command in self.debug_armature_construction(frame, position - self._global_offset_fix, function_name, show_names):
                g.write(command + "\n")

            ticks += 1

        if function_name not in self._commands_to_index or self._commands_to_index[function_name] > ticks - 1:
            self._commands_to_index[function_name] = ticks - 1

    def search_function(self, selector_objective: str = 'global animation_time') -> None:
        """Write commands to index the correct .mcfunction file to run the animation.
        Search is O(log2(N)) with N being the number of frames.
        """
        max_ticks = max(self._commands_to_index.values())

        try:
            os.mkdir(os.path.join(self.function_directory, 'search'))
        except FileExistsError:
            pass

        for ticks in range(max_ticks):
            search_path = os.path.join(self.function_directory, 'search', str(ticks) + ".mcfunction")
            g = open(search_path, "a")
            for function_name in self._commands_to_index:
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
