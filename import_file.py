from typing import Union

from math_objects import Vector3, Quaternion, Euler
from armature import Armature, ArmatureFrame, ArmatureAnimation, Bone, ArmatureFrameBone

import math


def load_bvh(file_path: str, scale: float, order: str = 'xyz', max_frames: int = None,
             face_north: Quaternion = Quaternion(0.0, 0.0, 0.0, 1.0), fps: Union[float, int] = 20) -> tuple[
    Armature, ArmatureAnimation]:
    name = '_'.join(file_path.split('/')[1:]).replace('.', '_').replace(' ', '_')
    new_armature = Armature(name)
    new_animation = ArmatureAnimation(fps)

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
        parent_name_stack = []
        new_bone = None
        mode = 0
        frame = 0
        for line in file:
            words = line.split()
            if mode == 0:
                if words[0] == 'HIERARCHY':
                    continue

                elif words[0] == 'ROOT' or words[0] == 'JOINT' or words[0] == 'End':
                    if words[0] == 'End':
                        # TODO bone_name = 'End Site_' + current_bone_data[0]
                        bone_name = 'mcf_End Site_' + bone_name
                    else:
                        bone_name = ' '.join(words[1:len(words)])
                    new_bone = Bone(bone_name)
                elif words[0] == '{':
                    try:
                        parent_name = parent_name_stack[-1]
                    except IndexError:
                        parent_name = 'mcf_root_' + name
                    new_armature.add_bone(new_bone, parent_name)
                    parent_name_stack.append(bone_name)

                elif words[0] == '}':
                    parent_name_stack.pop()
                    # new_armature.add_bone(new_bone, parent_name_stack.pop())

                elif words[0] == 'OFFSET':
                    offset = Vector3(*map(float, words[1: 4])) * scale
                    offset.rotate_by_quaternion(face_north)
                    new_bone.original_size = offset

                elif words[0] == 'CHANNELS':
                    pass

                if len(parent_name_stack) == 0 and len(new_armature.bones) > 2:
                    mode = 1
            else:
                if words[0] == 'MOTION':
                    pass
                elif words[0] == 'Frames:':
                    total_frames = int(words[1])
                elif words[0] == 'Frame' and words[1] == 'Time:':
                    animation_fps = 1 / float(words[2])

                    skip_frames = animation_fps / fps

                    total_minecraft_frames = math.ceil(total_frames / skip_frames)
                    include_frames = {int(i * skip_frames) for i in range(total_minecraft_frames)}

                elif len(words[0]) == 0:
                    pass
                else:
                    if max_frames is not None and len(new_animation.frames) >= max_frames >= 0:
                        break
                    if frame in include_frames:
                        index_start = 0

                        new_frame = ArmatureFrame()

                        for bone_name in new_armature.bones:
                            if bone_name[0:4] == 'mcf_':
                                continue
                            bone = new_armature.bones[bone_name]

                            # TODO should we account for .bvh files that do not have 6 channels

                            index_end = index_start + 6

                            # read channels
                            x_pos, y_pos, z_pos, x_rot, y_rot, z_rot = tuple(map(float, words[index_start:index_end]))

                            # set position
                            offset = Vector3(x_pos, y_pos, z_pos) * scale
                            offset.rotate_by_quaternion(face_north)

                            # set rotation
                            rotation = Quaternion().set_from_euler(Euler(order, x_rot, y_rot, z_rot))

                            rotation.x, rotation.y = rot_matrix_z(rotation.x, rotation.y)
                            rotation.x, rotation.z = rot_matrix_y(rotation.x, rotation.z)
                            rotation.y, rotation.z = rot_matrix_x(rotation.y, rotation.z)

                            # set new frame
                            new_frame.bone_channels[bone_name] = ArmatureFrameBone(offset, rotation)

                            index_start = index_end

                        new_animation.frames.append(new_frame)
                    frame += 1

    return new_armature, new_animation