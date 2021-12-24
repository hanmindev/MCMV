import os

import utility
from entities import AecArmorStandPair, Bone, FrameBone, Frame, GlobalBone
from math_objects import Euler, Vector3, Quaternion


def quick_euler_shortcut(tup: tuple[float, float, float]) -> tuple[float, float, float]:
    e = Euler('yxz', *tup)
    e.change_order('xyz')
    return e.to_tuple()


# Maps .bvh names to names that this python script understands.
BONE_MAPPER = {
    'main': 'PositionOffset',
    'hip': 'Hip',
    'left_thigh': 'Left_Thigh',
    'left_knee': 'Left_Knee',
    'left_foot': 'Left_Ankle',
    'right_thigh': 'Right_Thigh',
    'right_knee': 'Right_Knee',
    'right_foot': 'Right_Ankle',
    'back_0': 'Waist',
    'back_1': 'Spine',
    'back_2': 'Chest',
    'left_shoulder': 'Left_Shoulder',
    'left_arm': 'Left_Arm',
    'left_elbow': "Left_Elbow",
    'left_wrist': "Left_Wrist",
    'right_shoulder': 'Right_Shoulder',
    'right_arm': 'Right_Arm',
    'right_elbow': 'Right_Elbow',
    'right_wrist': 'Right_Wrist',
    'head': 'Neck',
    'body': 'Waist'

}


class MainConverter:
    """The main converter class.
    """
    bones: dict[str, Bone]
    frame_time = None
    frames: list[Frame]

    def __init__(self) -> None:
        self.bones = {}
        self.bone_list = []
        self.frames = []

    def load_file(self, file_path: str) -> None:
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
                        self.bones[bone_name] = Bone(bone_name)
                        if len(parent_stack) > 0:
                            self.bones[bone_name].parent = parent_stack[-1]
                            self.bones[parent_stack[-1]].children.add(bone_name)
                        self.bone_list.append(bone_name)
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
                        self.frame_time = float(words[2])
                    elif len(words[0]) == 0:
                        pass
                    else:
                        index_start = 0
                        self.frames.append(Frame())
                        for bone_name in self.bone_list:
                            if bone_name == 'Site':
                                continue
                            bone = self.bones[bone_name]
                            index_end = index_start + bone.channel_count

                            channels = tuple(map(float, words[index_start:index_end]))

                            index_start = index_end

                            self.frames[-1].frame_bones[bone.bone_name] = FrameBone(bone.bone_name, channels)

    def convert_data(self, output_directory: str) -> None:
        original_frames = 1 / self.frame_time
        minecraft_frames = 20
        skip_frames = round(original_frames / minecraft_frames)

        ticks = 0
        try:
            os.mkdir(output_directory)
        except FileExistsError:
            pass
        complete_path = os.path.join(output_directory, 'test' + ".mcfunction")
        open(complete_path, 'w').close()
        f = open(complete_path, "a")

        for i in range(0, len(self.frames), skip_frames):
            frame = self.frames[i]

            # function indexing
            pre_command = 'execute if score global animation_time matches ' + str(ticks) + ' run '
            f.write(pre_command + 'function animate:armature/test' + str(ticks) + '\n')

            # per function
            complete_path = os.path.join(output_directory, 'test' + str(ticks) + ".mcfunction")
            open(complete_path, 'w').close()
            g = open(complete_path, "a")

            for command in self.armature_construction(frame):
                g.write(command + "\n")

            ticks += 1

            g.close()
        f.close()

    def armature_construction(self, frame: Frame) -> list[str]:
        commands = []
        useful_bones = set(BONE_MAPPER.values())

        def dfs(frame_bone, parent_pos, parent_rot) -> None:
            # skip extra bones
            if frame_bone.bone_name not in useful_bones:
                return None

            # Rotate the bone by the parent
            bone_vector = Vector3(*frame_bone.channels[0:3])
            bone_vector.rotate_by_quaternion(parent_rot)

            # Fix the new rotation
            child_rot = Quaternion().set_from_euler(Euler('xyz', *frame_bone.channels[3:6]))
            child_rot.parent(parent_rot)

            child_pos = parent_pos + bone_vector

            # display
            if frame_bone.bone_name not in {'Hip', 'PositionOffset'}:
                vector_step = bone_vector * 0.1

                # in between stone
                for i in range(10):
                    xyz = ('{:f}'.format(j * 100) for j in parent_pos + vector_step * (i + 0.5))

                    commands.append(
                        'summon minecraft:falling_block ' + ' '.join(xyz) +
                        ' {NoGravity:true,BlockState:{Name:"minecraft:stone"}}')
                xyz = ('{:f}'.format(i * 100) for i in child_pos)

                # node
                commands.append(
                    'summon minecraft:falling_block ' + ' '.join(xyz) +
                    ' {NoGravity:true,BlockState:{Name:"minecraft:diamond_block"},'
                    'CustomNameVisible: 1b, CustomName: \'{"text": "' + frame_bone.bone_name + '"}\'' + '}')

            # recursion
            bone = self.bones[frame_bone.bone_name]
            children = bone.children

            for child in children:
                if child == 'Site':
                    continue
                dfs(frame.frame_bones[child], child_pos, child_rot)

        initial_frame_bone = frame.frame_bones[BONE_MAPPER['main']]
        origin = Vector3(0, 1, 0)
        origin_rot = Quaternion(0, 0, 0, 1)
        dfs(initial_frame_bone, origin, origin_rot)
        return commands

    def globalize_frame_armature(self, frame: Frame, initial_frame_bone_name: str) -> dict[str, GlobalBone]:

        def dfs(frame_bone, parent_pos, parent_rot) -> None:
            # skip extra bones
            if frame_bone.bone_name not in useful_bones:
                return None

            # Rotate the bone by the parent
            bone_vector = Vector3(*frame_bone.channels[0:3])
            bone_vector.rotate_by_quaternion(parent_rot)

            # Fix the new rotation
            child_rot = Quaternion().set_from_euler(Euler('xyz', *frame_bone.channels[3:6]))
            child_rot.parent(parent_rot)

            # ending position
            child_pos = parent_pos + bone_vector

            # pack
            frame_armature[frame_bone.bone_name] = GlobalBone(frame_bone.bone_name,
                                                              Vector3(*child_pos), parent_rot,
                                                              Vector3(*frame_bone.channels[0:3]))

            # recursion
            bone = self.bones[frame_bone.bone_name]
            children = bone.children

            for child in children:
                if child == 'Site':
                    continue
                dfs(frame.frame_bones[child], child_pos, child_rot)

        useful_bones = set(BONE_MAPPER.values())
        origin = Vector3(0, 1, 0)
        origin_rot = Quaternion(0, 0, 0, 1)
        frame_armature = {}

        initial_frame_bone = frame.frame_bones[initial_frame_bone_name]
        dfs(initial_frame_bone, origin, origin_rot)

        return frame_armature

    def globalize_armature(self, output_directory: str, root: str, stands: list[tuple[str, str, str]]):
        minecraft_frames = 20
        initial_frame_bone_name = BONE_MAPPER['main']

        original_frames = 1 / self.frame_time
        skip_frames = round(original_frames / minecraft_frames)
        ticks = 0
        # import all the armor stands
        stand_dict = {}
        for stand in stands:
            stand_dict[stand[0]] = AecArmorStandPair(stand[1], stand[2])

        try:
            os.mkdir(output_directory)
        except FileExistsError:
            pass
        complete_path = os.path.join(output_directory, 'test' + ".mcfunction")
        open(complete_path, 'w').close()
        f = open(complete_path, "a")

        for i in range(0, len(self.frames), skip_frames):
            # function indexing
            pre_command = 'execute if score global animation_time matches ' + str(ticks) + ' run '
            f.write(pre_command + 'function animate:armor_stand/test' + str(ticks) + '\n')

            # per tick file
            frame = self.frames[i]
            frame_armature = self.globalize_frame_armature(frame, initial_frame_bone_name)

            commands = []

            for stand_name in stand_dict:
                aec_stand_pair = stand_dict[stand_name]
                global_bone = frame_armature[BONE_MAPPER[stand_name]]
                command = aec_stand_pair.return_command(global_bone.position, global_bone.rotation, 5.0, root)
                commands.append(command)

            command = '\n'.join(commands)

            complete_path = os.path.join(output_directory, 'test' + str(ticks) + ".mcfunction")
            open(complete_path, 'w').close()
            g = open(complete_path, "a")
            g.write(command)
            g.close()

            ticks += 1
        f.close()


if __name__ == '__main__':
    converter = MainConverter()
    converter.load_file('data/untitled_short.bvh')
    converter.convert_data('C:/Users/Hanmin/AppData/Roaming/.minecraft/saves/Project '
                           'Sekai/datapacks/prsk/data/animate/functions/armature')
    converter.globalize_armature('C:/Users/Hanmin/AppData/Roaming/.minecraft/saves/Project '
                                 'Sekai/datapacks/prsk/data/animate/functions/armor_stand',
                                 '54e5e739-9221-45fc-a06f-b5326d174cf7',
                                 [('head',
                                   '2f9d6e9a-aaca-4964-9059-ec43f2016499',
                                   '19c4830d-8714-4e62-b041-0cde12b6de96'
                                   ),
                                  ('right_arm',
                                   '11dc3ca9-72b0-41e5-a25e-732749eb5370',
                                   'ad9573a4-361e-417c-8494-bf93c1cf44ef'
                                   ),
                                  ('left_arm',
                                   'd931c78e-ef11-4f37-92f6-d10a7c595f9c',
                                   'fe0ebeb5-9553-4455-8a78-1759237a1ae1'
                                   ),
                                  ('body',
                                   '41451f74-0acb-4406-a42f-cc90a4a04c9b',
                                   '530b439d-1760-4652-93a7-3320f269358a'
                                   ),
                                  ('left_thigh',
                                   'dada4315-783e-45d9-990d-418a3284db9a',
                                   '3c49fedd-ad2d-46dc-a3fd-fed469eb6d02'
                                   ),
                                  ('right_thigh',
                                   '1f4134e3-2608-4d8d-8f10-d687549cb46d',
                                   '2ea57372-4206-428f-9b4c-7c946d247270'
                                   )
                                  ]
                                 )
