import math
from typing import Union

from math_objects import Quaternion, Vector3, Euler
from armature_objects import ArmatureModel, ArmatureAnimation, ArmatureFrame, Joint


class BvhFileLoader:
    def __init__(self, file_path: str, scale: float, order: str = 'xyz', face_north: Quaternion = Quaternion()):
        self.name = '_'.join(file_path.split('/')[1:]).replace('.', '_').replace(' ', '_')

        self.file_path = file_path
        self.scale = scale
        self.order = order
        self.face_north = face_north

        self.start_animation_line = -1
        self.joint_name_list = []

        face_north_euler = Euler('xyz').set_from_quaternion(face_north)

        angle_x = math.radians(face_north_euler.x)
        angle_y = math.radians(face_north_euler.y)
        angle_z = math.radians(face_north_euler.z)

        def rot_matrix_x(y: float, z: float) -> tuple[float, float]:
            return y * math.cos(angle_x) - z * math.sin(angle_x), z * math.cos(angle_x) + y * math.sin(angle_x)

        def rot_matrix_y(x: float, z: float) -> tuple[float, float]:
            return x * math.cos(angle_y) + z * math.sin(angle_y), z * math.cos(angle_y) - x * math.sin(angle_y)

        def rot_matrix_z(x: float, y: float) -> tuple[float, float]:
            return x * math.cos(angle_z) - y * math.sin(angle_z), y * math.cos(angle_z) + x * math.sin(angle_z)

        # is this cursed?
        self.rot_matrix_x = rot_matrix_x
        self.rot_matrix_y = rot_matrix_y
        self.rot_matrix_z = rot_matrix_z

    def get_model(self) -> ArmatureModel:
        new_armature = ArmatureModel(self.name)
        new_armature.add_joint(Joint('mcf_root_' + self.name))

        with open(self.file_path, encoding='utf-8') as file:
            parent_name_stack = []
            new_joint = None

            for i, line in enumerate(file):
                words = line.split()
                if len(words) == 0:
                    continue

                if words[0] == 'HIERARCHY':
                    continue

                elif words[0] == 'ROOT' or words[0] == 'JOINT' or words[0] == 'End':
                    if words[0] == 'End':
                        joint_name = 'mcf_End Site_' + joint_name
                    else:
                        joint_name = ' '.join(words[1:len(words)])
                    new_joint = Joint(joint_name)
                elif words[0] == '{':
                    try:
                        parent_name = parent_name_stack[-1]
                    except IndexError:
                        parent_name = 'mcf_root_' + self.name
                    new_armature.add_joint(new_joint, parent_name)
                    parent_name_stack.append(joint_name)

                elif words[0] == '}':
                    parent_name_stack.pop()

                elif words[0] == 'OFFSET':
                    offset = Vector3(*map(float, words[1: 4])) * self.scale
                    offset.rotate_by_quaternion(self.face_north)
                    new_joint.initial_offset = offset

                elif words[0] == 'CHANNELS':
                    channels = words[2:]
                    self.joint_name_list.append((new_joint.name, channels))

                elif words[0] == 'MOTION':
                    self.start_animation_line = i
                    break
        return new_armature

    def get_animation(self, fps: Union[float, int] = 20, start_frame: int = 0, max_frames: int = None) -> ArmatureAnimation:
        if self.start_animation_line == -1:
            raise Exception('Get the armature model first!')

        new_animation = ArmatureAnimation(fps)

        frame = 0
        include_frames = None
        with open(self.file_path, encoding='utf-8') as file:
            for i, line in enumerate(file):
                if len(line) == 0 or i < self.start_animation_line:
                    continue

                if line[:6] == 'MOTION':
                    continue
                elif line[:8] == 'Frames: ':
                    total_frames = int(line[8:])
                elif line[:12] == 'Frame Time: ':
                    animation_fps = 1 / float(line[12:])

                    skip_frames = animation_fps / fps

                    total_minecraft_frames = math.ceil(total_frames / skip_frames)
                    include_frames = {int(i * skip_frames) for i in range(total_minecraft_frames)}
                else:
                    if max_frames is not None and len(new_animation.frames) >= max_frames >= 0:
                        break
                    elif start_frame > 0:
                        start_frame -= 1
                        continue
                    elif frame in include_frames:
                        new_animation.frames.append(self.get_frame_from_line(line))
                    frame += 1
        return new_animation

    def get_frame_from_line(self, line: str) -> ArmatureFrame:
        words = line.split()

        index_start = 0

        new_frame = ArmatureFrame()

        for joint_name, channels in self.joint_name_list:
            if joint_name[0:4] == 'mcf_':
                continue

            index_end = index_start + len(channels)
            offset = Vector3()
            rotation_euler = Euler(self.order)

            # read channels
            for i, channel_name in enumerate(channels):
                value = float(words[index_start + i])
                if channel_name == 'Xposition':
                    offset.i = value
                elif channel_name == 'Yposition':
                    offset.j = value
                elif channel_name == 'Zposition':
                    offset.k = value
                elif channel_name == 'Xrotation':
                    rotation_euler.x = value
                elif channel_name == 'Yrotation':
                    rotation_euler.y = value
                elif channel_name == 'Zrotation':
                    rotation_euler.z = value

            offset.rotate_by_quaternion(self.face_north)

            # set rotation
            rotation = Quaternion().set_from_euler(rotation_euler)

            rotation.x, rotation.y = self.rot_matrix_z(rotation.x, rotation.y)
            rotation.x, rotation.z = self.rot_matrix_y(rotation.x, rotation.z)
            rotation.y, rotation.z = self.rot_matrix_x(rotation.y, rotation.z)

            # set new frame
            new_frame.joint_channels[joint_name] = (offset, rotation)

            index_start = index_end

        return new_frame

    def get_single_animation(self, frame_number: int = -1) -> ArmatureFrame:
        pass
