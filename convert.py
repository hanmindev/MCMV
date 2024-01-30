import argparse
import json

from mcmv import utility
from mcmv.armature_formatter import MinecraftModelCreator
from mcmv.armature_objects import DisplayVoxel, ArmatureModel, ArmatureAnimation
from mcmv.export_bedrock import BedrockModelExporter, BedrockGeoFileFormatter, BedrockAnimFileFormatter
from mcmv.export_java import JavaModelExporter
from mcmv.import_file import BvhFileLoader
from mcmv.math_objects import Vector3, Quaternion, Euler

FORMAT_VERSION = "3.0"


class ConfigLoader:
    minecraft_models: dict[str, MinecraftModelCreator]
    armature_model_animations: dict[str, tuple[ArmatureModel, ArmatureAnimation]]
    translations: dict[str, dict[str, str]]

    def __init__(self):
        self.minecraft_models = {}
        self.armature_model_animations = {}
        self.translations = {}

    @staticmethod
    def quaternion_from_list(rotation: list[str, float]):
        if len(rotation) == 3:
            q = Quaternion().set_from_euler(Euler('xyz', *rotation))
        elif isinstance(rotation[0], str):
            q = Quaternion().set_from_euler(Euler(*rotation))
        else:
            q = Quaternion(*rotation)
        return q

    def load_minecraft_model(self, info: dict):
        name = info['model_name']
        model_type = info['type'].lower()

        if model_type == 'mcmv_json':
            new_minecraft_model = self._load_mcmv_json_model(info)
        elif model_type == 'create_from_animation':
            new_minecraft_model = self._load_create_from_anim_model(info)
        else:
            raise model_type + ' is an unsupported type of Minecraft Model!'

        self.minecraft_models[name] = new_minecraft_model

    @staticmethod
    def _load_mcmv_json_model(info: dict) -> MinecraftModelCreator:
        path = info['path']

        f = open(path)

        data = json.load(f)
        f.close()

        if str(data['format_version']) != FORMAT_VERSION:
            raise 'Incorrect Format Version! This converter needs format version 3.0!'

        bone_list = []

        for bone in data['bones']:
            parent_name = bone['parent_name']
            child_name = bone['child_name']
            if 'size' in bone:
                size = Vector3(*bone['size'])
                offset = Vector3(*bone['offset'])

                display_offset = bone['display'].get('offset', None)
                display_size = bone['display'].get('size', None)
                if display_offset is not None:
                    display_offset = Vector3(*display_offset)
                    display_size = Vector3(*display_size)

                display_item = bone['display'].get('item', None)

                bone_info = (
                    parent_name,
                    child_name,
                    size,
                    offset,
                    DisplayVoxel(display_offset, display_size, display_item)
                )
            else:
                bone_info = (parent_name, child_name)

            bone_list.append(bone_info)
        m = MinecraftModelCreator()
        m.set_bones(visible_bone_list=bone_list)

        return m

    def _load_create_from_anim_model(self, info: dict) -> MinecraftModelCreator:
        animation_source = info['animation_name']
        scale = info.get('scale', 1.0)
        base = info.get('base', None)

        animation_model = self.armature_model_animations[animation_source][0]
        m = MinecraftModelCreator()
        m.create_bones(animation_model, scale, base)

        return m

    def load_animation(self, info):
        name = info['animation_name']
        animation_type = info['type'].lower()

        if animation_type == 'bvh':
            new_animation = self._load_bvh_animation(info)
        else:
            raise animation_type + ' is an unsupported type of Animation!'

        self.armature_model_animations[name] = new_animation

    @staticmethod
    def _load_bvh_animation(info: dict) -> tuple[ArmatureModel, ArmatureAnimation]:

        path = info['path']

        scale = info.get('scale', 1.0)
        order = info.get('order', 'xyz')
        face_north = info.get('face_north', [0.0, 0.0, 0.0, 1.0])

        fps = info.get('fps', 20)
        start_frame = info.get('start_frame', 0)
        max_frames = info.get('max_frames', -1)

        north_quaternion = ConfigLoader.quaternion_from_list(face_north)

        file_loader = BvhFileLoader(file_path=path, scale=scale, order=order, face_north=north_quaternion)

        model = file_loader.get_model()
        animation = file_loader.get_animation(fps=fps, start_frame=start_frame, max_frames=max_frames)

        return model, animation

    def load_translation(self, info: dict):
        name = info['translation_name']
        path = info['path']
        f = open(path)

        data = json.load(f)
        f.close()

        translation = data

        self.translations[name] = translation

    def perform_task(self, info: dict):
        minecraft_type = info['type'].lower()
        if minecraft_type == 'java':
            self._java_task(info)
        elif minecraft_type == 'bedrock':
            self._bedrock_task(info)
        else:
            raise minecraft_type + ' is an unsupported type of output!'

    def _java_task(self, info: dict):
        function_path = info['function_path']

        j = JavaModelExporter(function_directory=function_path)

        for armature in info['armatures']:
            self._java_armature_task(j, armature)

        reset_function = info.get('reset_function', True)
        remove_function = info.get('remove_function', True)
        search_function = info.get('search_function', True)

        scoreboard_counter = info.get('scoreboard_counter', 'global animation_time')
        auto = info.get('auto', True)
        loop = info.get('loop', True)
        if reset_function:
            j.write_reset_function()
        if remove_function:
            j.write_remove_function()
        if search_function:
            j.write_search_function(selector_objective=scoreboard_counter, auto=auto, loop=loop)

    def _java_armature_task(self, j: JavaModelExporter, info: dict):
        name = info['name']
        minecraft_model_name = info['model_name']
        minecraft_model_no = info['model_no']
        animation_name = info['animation_name']
        translation_name = info.get('translation_name', None)

        minecraft_model = self.minecraft_models[minecraft_model_name].minecraft_model
        model, animation = self.armature_model_animations[animation_name]
        if translation_name is not None:
            translation = self.translations[translation_name]
        else:
            translation = None

        j.set_model_info(model, minecraft_model, translation)

        animation_info = info['write_animation']
        root = animation_info.get('root', [0.0, 0.0, 0.0])
        if not isinstance(root, str):
            root = Vector3(*root)

        offset = Vector3(*animation_info.get('offset', [0.0, 0.0, 0.0]))
        rotate = ConfigLoader.quaternion_from_list(animation_info.get('rotate', [0.0, 0.0, 0.0, 1.0]))
        allow_rotation = animation_info.get('allow_rotation', True)

        j.write_animation(function_name=name, animation=animation, root=root, allow_rotation=allow_rotation, offset=offset, rotate=rotate, minecraft_model_no=minecraft_model_no)

    def _bedrock_task(self, info: dict):
        b = BedrockModelExporter()

        for armature in info['armatures']:
            self._bedrock_armature_task(b, armature)

    def _bedrock_armature_task(self, b: BedrockModelExporter, info: dict):
        # name = info['name']
        minecraft_model_name = info['model_name']
        animation_name = info['animation_name']
        model_no = info.get('model_no', '')
        translation_name = info.get('translation_name', None)

        minecraft_model = self.minecraft_models[minecraft_model_name].minecraft_model
        model, animation = self.armature_model_animations[animation_name]
        if translation_name is not None:
            translation = self.translations[translation_name]
        else:
            translation = None

        b.set_model_info(model, minecraft_model, translation, model_no)

        if 'write_geo_model' in info:
            model_info = info['write_geo_model']
            geo_model_path = model_info['geo_model_path']
            file_name = model_info['file_name']

            offset = Vector3(*model_info.get('offset', [0.0, 0.0, 0.0]))
            rotate = ConfigLoader.quaternion_from_list(model_info.get('rotate', [0.0, 0.0, 0.0, 1.0]))

            bedrock_format = model_info['bedrock_format']
            format_version = bedrock_format['format_version']
            identifier = bedrock_format['identifier']
            texture_size = tuple(bedrock_format['texture_size'])

            bgf = BedrockGeoFileFormatter(format_version=format_version, identifier=identifier, texture_size=texture_size)

            b.write_geo_model(path=geo_model_path, file_name=file_name, model_header=bgf, offset=offset, rotate=rotate)

        if 'write_animation' in info:
            animation_info = info['write_animation']
            animation_path = animation_info['animation_model_path']
            file_name = animation_info['file_name']

            bedrock_format = animation_info['bedrock_format']
            format_version = bedrock_format['format_version']
            identifier = bedrock_format['identifier']

            baf = BedrockAnimFileFormatter(format_version=format_version, identifier=identifier)

            b.write_animation(path=animation_path, file_name=file_name, model_header=baf, animation=animation)


def load_data(config_path: str):
    f = open(config_path)

    data = json.load(f)
    f.close()

    config_loader = ConfigLoader()

    if str(data['format_version']) != FORMAT_VERSION:
        raise 'Incorrect Format Version! This converter needs format version 3.0!'

    tot = len(data['animation_source'])
    for i, info in enumerate(data['animation_source']):
        print('Loading animation sources... ({}/{})'.format(i + 1, tot))
        config_loader.load_animation(info)

    tot = len(data['model_source'])
    for i, info in enumerate(data['model_source']):
        print('Loading model sources... ({}/{})'.format(i + 1, tot))
        config_loader.load_minecraft_model(info)

    tot = len(data['translation_source'])
    for i, info in enumerate(data['translation_source']):
        print('Loading translation sources... ({}/{})'.format(i + 1, tot))
        config_loader.load_translation(info)

    tot = len(data['tasks'])
    for i, info in enumerate(data['tasks']):
        print('Loading task sources... ({}/{})'.format(i + 1, tot))
        config_loader.perform_task(info)


if __name__ == '__main__':
    config_json = ['main.json']

    parser = argparse.ArgumentParser(description='Python script to convert .bvh files into Minecraft.\nGithub: https://github.com/hanmindev/MCMV')
    parser.add_argument('--config', help='Load a configuration file', nargs='*', default=config_json)

    args = parser.parse_args()
    config_json = args.config

    for config in config_json:
        print('Loading ' + config + '...')
        if config[:7] != 'config/':
            config = 'config/' + config
        if config[-5:] != '.json':
            config = config + '.json'

        load_data(config)
    print('Complete!')
