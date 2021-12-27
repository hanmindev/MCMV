import os
import shutil
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
            quit()

    def load_file(self, file_path: str, scale: float, order: str = 'xyz') -> None:
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
        with open(file_path, encoding='utf-8') as file:
            parent_stack = []
            mode = 0
            for line in file:
                words = line.split()
                if mode == 0:
                    if words[0] == 'HIERARCHY':
                        continue

                    elif words[0] == 'ROOT' or words[0] == 'JOINT' or words[0] == 'End':
                        bone_name = words[1]
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
                        self.bones[parent_stack[-1]].offset = offset

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

                            index_start = index_end

                            self.frames[-1].frame_bones[bone.bone_name] = FrameBone(bone.bone_name, channels)

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

        def dfs(frame_bone, parent_pos, parent_rot, fix_position) -> None:
            global positioned
            # skip extra bones
            if frame_bone.bone_name not in self._useful_bones:
                return None

            # Fix the new rotation
            child_rot = Quaternion().set_from_euler(Euler(self._order, *frame_bone.channels[3:6]))
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

                    # account for bone size and t pose differences
                    q = Quaternion().between_vectors(bone_size_vector, t_pose_vector)
                    q.parent(child_rot)
                    bone_size_vector.rotate_by_quaternion(q)
                else:
                    # Rotate the bone by the parent
                    bone_offset_vector = Vector3(*frame_bone.channels[0:3]) * self.scale
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
                           stands: list[tuple[str, str, str,
                                              Optional[Vector3],
                                              Optional[Vector3],
                                              Optional[Vector3],
                                              str]]) -> None:
        """Loads a .bvh file.

            function_name: Name of the Minecraft function (e.g. could be name of the character, armature_001, etc)
            root_uuid: UUID of the root entity that the armature is positioned at.
            (e.g. 54e5e739-9221-45fc-a06f-b5326d174cf7)
            stands: A list of tuples containing information for an AEC-ArmorStand Pair:
                Name of the bone (Should be the same name used in the .bvh file.)
                UUID of the AEC (e.g. 2f9d6e9a-aaca-4964-9059-ec43f2016499)
                UUID of the Armor Stand (e.g. 19c4830d-8714-4e62-b041-0cde12b6de96)
                The size of the bone as a Vector3 object
                The offset of the bone as a Vector3 object
                The initial direction of the bone as a Vector3 object (The vector that the bone would
                    be pointing towards as default (e.g. if your .bvh model initially is doing a T-Pose,
                    the right arm would have the vector (-1.0, 0.0, 0.0).)
                A string representation of the Minecraft item to be displayed. (e.g. diamond_hoe{CustomModelData:100}
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
            self._aec_stand_pairs[function_name][stand[0]] = AecArmorStandPair(*stand[0:7])
            stand_bone_names.add(stand[0])

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

                command = aec_stand_pair.return_transformation_command(
                    global_bone.position - self._global_offset_fix, global_bone.rotation, root_uuid)

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

    def reset_function(self, function_name: str) -> None:
        """Write commands to remove and summon necessary AEC-Stand pairs.
        This will not overwrite the function so reset_function can be called with different
        function_names.

            function_name: name of the function group (e.g. armature_001)
        """
        complete_path = os.path.join(self.function_directory, 'reset' + ".mcfunction")
        f = open(complete_path, "a")

        commands = []
        for aec_stand_pair in self._aec_stand_pairs[function_name]:
            commands += self._aec_stand_pairs[function_name][aec_stand_pair].return_reset_commands()
        f.write('\n'.join(commands) + '\n')
        f.close()

    def search_function(self, function_name: str) -> None:
        """Write commands to index the correct .mcfunction file to run the animation.
        Currently the search used is linear. Could be drastically improved by using a
        binary search but currently it runs fine on my machine so it'll be something
        I'll do in the future.

            function_name: name of the function group (e.g. armature_001)
        """
        complete_path = os.path.join(self.function_directory, 'main' + ".mcfunction")
        f = open(complete_path, "a")

        for ticks in range(self._commands_to_index[function_name]):
            # function indexing
            pre_command = 'execute if score global animation_time matches ' + str(ticks) + ' run '
            f.write(pre_command + 'function ' + utility.get_function_directory(self.function_directory,
                                                                               function_name) + '/' + str(ticks) + '\n')
        f.close()
