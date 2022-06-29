import json
import math
import os
import shutil
import sys
from typing import Optional, Union

import mc_search_function
import utility
from armature_formatter import MinecraftModelFormatter
from armature_objects import ArmatureModel, MinecraftModel, DisplayVoxel, ArmatureAnimation, VisibleBone, PositionalBone, Bone
from converter import Converter, RotationFixer
from math_objects import Vector3, Euler, Quaternion


class JavaUtility:
    @staticmethod
    def get_animation_position(position: Vector3) -> Vector3:
        new_position = position
        return new_position

    @staticmethod
    def get_rotation(quaternion: Quaternion) -> Euler:
        rotation = Euler('zyx').set_from_quaternion(quaternion)
        rotation.x *= -1
        rotation.y *= -1
        quaternion = Quaternion().set_from_euler(rotation)

        # account for the fact that y angle 0 is south
        rotation = Euler('zyx').set_from_quaternion(quaternion.parented(Quaternion(0.0, 1.0, 0.0, 0.0)))

        return rotation


class AecStandPair:
    def __init__(self, name: str, seed_prefix: tuple[str, str], root: Union[str, Vector3], item: str, allow_rotation: bool):
        self.name = name
        self._seed_prefix = utility.get_function_directory(*seed_prefix).replace(' ', '_')

        if root is None:
            self.root = Vector3()
        else:
            self.root = root

        self.aec_uuid, self.stand_uuid = utility.get_joint_uuids(*seed_prefix, self.name)
        self.item = item

        tag = self._seed_prefix.split('/')
        self.common_tags = {'armature_stands', 'path_' + tag[0].replace(':', '_'), 'path_' + self._seed_prefix.replace(':', '_').replace('/', '_')}

        self._update = False

        self.show_names = False
        self.allow_rotation = allow_rotation

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

        if self.root is not None and isinstance(self.root, str):
            commands.append(
                'execute at ' + self.stand_uuid + ' rotated as ' + self.root + ' run tp ' + self.stand_uuid + ' ~ ~ ~ ~ ~')
        return commands

    def return_remove_commands(self) -> list[str]:
        """Return a list of commands to remove the AEC-Stand pair."""

        tags = self.common_tags.copy()
        tags.add('bn_' + self.name.replace(' ', '_'))

        commands = ['kill ' + self.aec_uuid,
                    'kill ' + self.stand_uuid]
        return commands

    def return_transformation_command(self, offset: Vector3 = Vector3(), rotate: Quaternion = Quaternion()) -> str:
        position = JavaUtility.get_animation_position(offset)
        rotation = JavaUtility.get_rotation(rotate)

        if type(self.root) is Vector3:
            commands = [
                'tp ' + self.aec_uuid + ' {} {} {}'.format(
                    *('{:f}'.format(i) for i in (position - Vector3(0.0, 1.9, 0.0) + self.root).to_tuple()))
            ]
        else:
            commands = [
                'execute at ' + self.root + ' run tp ' + self.aec_uuid + ' ^{} ^{} ^{}'.format(
                    *('{:f}'.format(i) for i in (position - Vector3(0.0, 1.9, 0.0)).to_tuple())) + ' ~ ~'
            ]
            if self.allow_rotation:
                commands.append(
                    'execute at ' + self.stand_uuid + ' rotated as ' + self.
                    root + ' run tp ' + self.stand_uuid + ' ~ ~ ~ ~ ~'
                )

        commands.append('data merge entity ' + self.aec_uuid + ' {Air: ' + str(int(self._update)) + '}')
        self._update = not self._update

        commands.append(
            'data merge entity ' + self.stand_uuid + ' {Pose:{Head:' + utility.tuple_to_m_list(rotation.to_tuple(), 'f') + '}}')

        return '\n'.join(commands)


class JavaModelExporter:
    minecraft_model: MinecraftModel
    original_model: ArmatureModel

    aec_stand_pairs: dict[str, dict[str, AecStandPair]]

    def __init__(self, function_directory: str):
        self.max_ticks = 0
        self.translation = None
        self.fps = 20
        self.function_directory = ''
        self.aec_stand_pairs = {}

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

        self.function_directory = function_directory

        try:
            os.mkdir(function_directory)
        except FileExistsError:
            pass

    def set_model_info(self, model: ArmatureModel, minecraft_model: MinecraftModel, translation: dict[str, str]):
        self.original_model = model.copy()
        self.minecraft_model = minecraft_model
        self.translation = translation

    def write_animation(self, function_name: str, animation: ArmatureAnimation, root: Union[str, Vector3] = Vector3().copy(), allow_rotation: bool = False, offset: Vector3 = Vector3().copy(), rotate: Quaternion = Quaternion().copy()):
        try:
            os.mkdir(os.path.join(self.function_directory, function_name))
        except FileExistsError:
            pass

        self.aec_stand_pairs[function_name] = {}

        for bone_name in self.minecraft_model.bones:
            bone = self.minecraft_model.bones[bone_name]
            if isinstance(bone, VisibleBone):
                self.aec_stand_pairs[function_name][bone_name] = AecStandPair(bone.name, (self.function_directory, function_name), root, bone.display.item, allow_rotation)

        for tick, frame in enumerate(animation.frames):
            complete_path = os.path.join(self.function_directory, function_name, str(tick) + ".mcfunction")
            open(complete_path, 'w').close()
            g = open(complete_path, "a")

            Converter.set_animation_frame(self.original_model, frame)
            Converter.set_minecraft_transformation(self.minecraft_model, self.original_model, self.translation)
            global_transformation = Converter.get_global_minecraft(self.minecraft_model)

            for bone_name in self.aec_stand_pairs[function_name]:
                aec_stand = self.aec_stand_pairs[function_name][bone_name]
                position, rotation = global_transformation[bone_name]

                commands = aec_stand.return_transformation_command(position, rotation)

                g.write(commands + '\n')
        self.max_ticks = max(self.max_ticks, len(animation))

    def write_reset_function(self):
        """Write commands to remove and summon necessary AEC-Stand pairs.
        """
        if self.function_directory == '':
            raise FileNotFoundError

        complete_path = os.path.join(self.function_directory, 'reset' + ".mcfunction")
        f = open(complete_path, "a")
        try:
            tags = next(iter(next(iter(self.aec_stand_pairs.values())).values())).common_tags.copy()
            commands = ['kill @e[tag=' + ',tag='.join(tags) + ']']

            for function_name in self.aec_stand_pairs:
                for aec_stand_pair in self.aec_stand_pairs[function_name]:
                    commands += self.aec_stand_pairs[function_name][aec_stand_pair].return_reset_commands()
            f.write('\n'.join(commands) + '\n')
        except StopIteration:
            f.write('tellraw @a [{"text":"[Debug] ","color":"red"},{"text":"There aren\'t any bones in '
                    'this Armature!","color":"white"}]')
        f.close()

    def write_remove_function(self):
        """Write commands to remove necessary AEC-Stand pairs.
        """
        if self.function_directory == '':
            raise FileNotFoundError

        complete_path = os.path.join(self.function_directory, 'remove' + ".mcfunction")
        f = open(complete_path, "a")
        try:
            tags = next(iter(next(iter(self.aec_stand_pairs.values())).values())).common_tags.copy()
            commands = ['kill @e[tag=' + ',tag='.join(tags) + ']']

            for function_name in self.aec_stand_pairs:
                for aec_stand_pair in self.aec_stand_pairs[function_name]:
                    commands += self.aec_stand_pairs[function_name][aec_stand_pair].return_remove_commands()
            f.write('\n'.join(commands) + '\n')
        except StopIteration:
            f.write('tellraw @a [{"text":"[Debug] ","color":"red"},{"text":"There aren\'t any bones in '
                    'this Armature!","color":"white"}]')
        f.close()

    def write_search_function(self, selector_objective: str = 'global animation_time') -> None:

        def commands(tick):
            command_list = []

            for function_name in self.aec_stand_pairs:
                command_list.append('function ' + utility.get_function_directory(self.function_directory, function_name) + '/' + str(tick))

            return command_list

        mc_search_function.create_search_function(os.path.join(self.function_directory, 'search'), utility.get_function_directory(self.function_directory, 'search'), selector_objective, commands,
                                                  (0, self.max_ticks), (True, True), divisions=8)

        complete_path = os.path.join(self.function_directory, 'main' + ".mcfunction")
        f = open(complete_path, "a")
        f.write('function ' + utility.get_function_directory(self.function_directory, 'search') + '/' + 'main' + '\n')
        f.write('scoreboard players add ' + selector_objective + ' 1' + '\n')
        f.write('execute if score ' + selector_objective + ' matches ' + str(self.max_ticks) + '.. run scoreboard players set ' + selector_objective + ' 0')

        f.close()