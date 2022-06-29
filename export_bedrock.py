import json
import math
import os
from typing import Optional

from armature_formatter import MinecraftModelFormatter
from armature_objects import ArmatureModel, MinecraftModel, DisplayVoxel, ArmatureAnimation, VisibleBone
from converter import Converter
from math_objects import Vector3, Euler, Quaternion
from utility import tuple_to_m_list


class BedrockUtility:
    @staticmethod
    def get_bedrock_position(position: Vector3) -> Vector3:
        new_position = position.copy()
        new_position.k *= -1
        return new_position

    @staticmethod
    def get_bedrock_rotation(quaternion: Quaternion) -> Euler:
        rotation = Euler('zyx').set_from_quaternion(quaternion)
        rotation.y *= -1
        rotation.z *= -1

        return rotation


class BedrockGeoFileFormatter:
    def __init__(self, format_version: str, identifier: str, texture_size: tuple[int, int],
                 visible_bounds_size: tuple[int, int] = (1, 2),
                 visible_bounds_offset: Vector3 = Vector3(0.0, 0.0, 0.0)):

        self.format_version = format_version
        self.identifier = identifier
        self.texture_size = texture_size
        self.visible_bounds_size = visible_bounds_size
        self.visible_bounds_offset = visible_bounds_offset

        self._bone_list = []

        self._json_info = {
            "format_version": self.format_version,
            "minecraft:geometry": [
                {
                    "description": {
                        "identifier": self.identifier,
                        "texture_width": self.texture_size[0],
                        "texture_height": self.texture_size[1],
                        "visible_bounds_width": self.visible_bounds_size[0],
                        "visible_bounds_height": self.visible_bounds_size[1],
                        "visible_bounds_offset": [
                            self.visible_bounds_offset.i,
                            self.visible_bounds_offset.j,
                            self.visible_bounds_offset.k
                        ]
                    },
                    "bones": self._bone_list
                }
            ]
        }

    def add_bone(self, name: str, parent_name: Optional[str], pivot: Vector3, display: DisplayVoxel):
        bone = {'name': name}
        if parent_name is not None:
            bone['parent'] = parent_name
        bone['pivot'] = list(pivot.to_tuple())
        if display is not None:
            bone['cubes'] = []
            cube_info = {
                'origin': list((pivot + display.offset).to_tuple()),
                'size': list(display.size.to_tuple()),
                'uv': [0, 0]
            }
            bone['cubes'].append(cube_info)

        self._bone_list.append(bone)

    def get_json_info(self):
        return self._json_info


class BedrockAnimFileFormatter:
    def __init__(self, format_version: str, identifier: str):
        self.format_version = format_version
        self.identifier = identifier
        self.animation_length = 0

        self._bone_dict = {}

        self._json_info = {
            "format_version": format_version,
            "animations": {
                identifier: {
                    "animation_length": self.animation_length,
                    "bones": self._bone_dict
                }
            }
        }

    def add_keyframe(self, bone_name: str, time: float, position: Vector3 = None, rotation: Quaternion = None):
        if bone_name not in self._bone_dict:
            self._bone_dict[bone_name] = {'rotation': {}, 'position': {}}
        bone_info = self._bone_dict[bone_name]
        if position is not None:
            bone_info['position'][str(time)] = list(BedrockUtility.get_bedrock_position(position).to_tuple())

        if rotation is not None:
            bone_info['rotation'][str(time)] = list(BedrockUtility.get_bedrock_rotation(rotation).to_tuple())

    def get_json_info(self):
        return self._json_info


class BedrockModelExporter:
    minecraft_model: MinecraftModel
    original_model: ArmatureModel

    def __init__(self, minecraft_model: MinecraftModel):
        self.translation = None
        self.fps = 20
        self.minecraft_model = minecraft_model

    def write_geo_model(self, path: str, file_name: str, model_header: BedrockGeoFileFormatter) -> None:
        """Write the bone information from self.minecraft_model to a .geo.json file."""

        bones = self.minecraft_model.bones

        global_transformation = MinecraftModelFormatter.get_model_global(self.minecraft_model)

        for bone_name in bones:
            bone = bones[bone_name]
            if isinstance(bone, VisibleBone):
                display = bone.display
            else:
                display = None

            if bone.parent is not None:
                parent_name = bone.parent.name
            else:
                parent_name = None
            # parent_name = None
            model_header.add_bone(bone.name, parent_name, global_transformation[bone.name][0], display)

        complete_path = os.path.join(path, file_name + ".geo.json")
        open(complete_path, 'w').close()
        g = open(complete_path, "a", encoding="utf-8")
        # Write the header

        g.write(json.dumps(model_header.get_json_info()))

    def set_model_info(self, model: ArmatureModel, translation: dict[str, str]):
        self.original_model = model.copy()
        self.translation = translation

    def write_animation(self, path: str, file_name: str, model_header: BedrockAnimFileFormatter, animation: ArmatureAnimation):
        complete_path = os.path.join(path, file_name + ".json")
        open(complete_path, 'w').close()
        g = open(complete_path, "a", encoding="utf-8")
        model_header.animation_length = math.ceil(len(animation.frames) / animation.fps)

        for i, frame in enumerate(animation.frames):
            frame_time = i / animation.fps

            Converter.set_animation_frame(self.original_model, frame)
            Converter.set_minecraft_transformation(self.minecraft_model, self.original_model, self.translation)

            for bone_name in self.minecraft_model.bones:
                bone = self.minecraft_model.bones[bone_name]
                model_header.add_keyframe(bone_name, frame_time, None, bone.local_animation_rotation)

        g.write(json.dumps(model_header.get_json_info()))
