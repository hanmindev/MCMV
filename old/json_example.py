from main import MainConverter
from math_objects import Vector3, Euler, Quaternion
import json


def return_rotation(rot_list: list) -> Quaternion:
    """Determines whether the given list represents values of a quaternion or an euler rotation and
    returns a quaternion object representing the rotation. """
    if len(rot_list) == 3:
        return Quaternion().set_from_euler(Euler('xyz', *rot_list[0:3]))
    elif type(rot_list[0]) is float and type(rot_list[3]) is float:
        return Quaternion(*rot_list[0:4])
    else:
        if type(rot_list[0]) is str:
            return Quaternion().set_from_euler(Euler(rot_list[0], *rot_list[1:4]))
        else:
            return Quaternion().set_from_euler(Euler(rot_list[3], *rot_list[0:3]))


if __name__ == '__main__':
    """This code is very messy. It's just for json importing. I'll clean it up in the future."""
    f = open('example.json')

    data = json.load(f)
    if data['format_version'] != '2.0':
        assert 'Wrong format version!'

    for stage in data['stages']:
        converter = MainConverter(stage['function_path'])

        reset_function = stage['reset_function'] if 'reset_function' in stage else False
        remove_function = stage['remove_function'] if 'remove_function' in stage else False
        search_function = stage['search_function'] if 'search_function' in stage else False
        for file in stage['files']:
            bvh_path = file['bvh_path']

            scale = file['scale'] if 'scale' in file else 1.0
            order = file['order'] if 'order' in file else 'xyz'
            max_frames = file['max_frames'] if 'max_frames' in file else None

            if 'face_north' in file:
                face_north = return_rotation(file['face_north'])
            else:
                face_north = Quaternion(0.0, 0.0, 0.0, 1.0)

            armatures = file['armatures'] if 'armatures' in file else None

            converter.load_file(bvh_path, scale, order, max_frames, face_north)

            for armature in armatures:
                function_name = armature['name']
                debug = armature['debug'] if 'debug' in armature else False
                show_names = armature['show_names'] if 'show_names' in armature else False

                transformation_defaults = (None, Vector3(0.0, 0.0, 0.0), Quaternion(0.0, 0.0, 0.0, 1.0), 1.0)
                if 'transformation' in armature:
                    root_uuid = armature['transformation']['root_uuid'] if 'root_uuid' in armature[
                        'transformation'] else transformation_defaults[0]
                    position = Vector3(*armature['transformation']['offset']) if 'offset' in armature[
                        'transformation'] else transformation_defaults[1]

                    if 'rotation' in armature['transformation']:
                        rotation = return_rotation(armature['transformation']['rotation'])
                    else:
                        rotation = Quaternion(0.0, 0.0, 0.0, 1.0)

                    scale = armature['transformation']['scale'] if 'scale' in armature['transformation'] else \
                        transformation_defaults[3]
                else:
                    root_uuid, position, rotation, scale = transformation_defaults

                if debug:
                    converter.create_debug_armature(function_name=function_name, uuid=root_uuid, offset=position,
                                                    rotate=rotation, show_names=show_names, scale=scale)
                else:
                    stands = armature['stands'] if 'stands' in armature else None
                    stand_list = []
                    if stands is not None:
                        for stand in stands:
                            start_bone = stand['start_bone'] if 'start_bone' in stand else None
                            end_bone = stand['end_bone'] if 'end_bone' in stand else None
                            display_item = stand['display_item'] if 'display_item' in stand else None
                            size = Vector3(*stand['size']).scaled_pixels_to_meter() if 'size' in stand else None
                            offset = Vector3(*stand['offset']).scaled_pixels_to_meter() if 'offset' in stand else None

                            stand_list.append((start_bone, end_bone, display_item, size, offset))

                    fill_in = armature['fill_in'] if 'fill_in' in armature else None
                    transformation_defaults = (None, None, None)
                    if 'transformation' in armature:
                        base = armature['transformation']['base'] if 'base' in armature['transformation'] else \
                            transformation_defaults[0]
                        center = armature['transformation']['center'] if 'center' in armature['transformation'] else \
                            transformation_defaults[1]
                        allow_rotation = armature['transformation']['allow_rotation'] if 'allow_rotation' in armature[
                            'transformation'] else transformation_defaults[2]
                    else:
                        base, center, allow_rotation = transformation_defaults

                    converter.create_armature(function_name=function_name, uuid=root_uuid, offset=position,
                                              rotate=rotation, show_names=show_names, scale=scale, stands=stand_list,
                                              fill_in=fill_in, base=base, center=center, allow_rotation=allow_rotation)
        if reset_function:
            converter.reset_function()
        if remove_function:
            converter.remove_function()
        if search_function:
            scoreboard_counter = stage[
                'scoreboard_counter'] if 'scoreboard_counter' in stage else 'global animation_time'
            converter.search_function(scoreboard_counter)
