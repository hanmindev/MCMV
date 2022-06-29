from typing import Optional

from armature_formatter import ArmatureFormatter
from armature_objects import ArmatureModel, MinecraftModel, ArmatureFrame, Joint, Bone
from math_objects import Vector3, Quaternion


class Converter:

    @staticmethod
    def set_animation_frame(model: ArmatureModel, frame: ArmatureFrame = None):
        ArmatureFormatter.set_frame(model, frame)

    @staticmethod
    def set_minecraft_transformation(minecraft_model: MinecraftModel, model: ArmatureModel, translation: dict[str, str]):
        global_transformation = ArmatureFormatter.get_model_global(model)

        def dfs(bone: Bone):
            try:
                parent_rotation_name = model.joints[translation[bone.name]].parent.name
                parent_global_rotation = global_transformation[parent_rotation_name][1]
            except KeyError:
                parent_global_rotation = Quaternion()

            for child_name in bone.children:
                child = bone.children[child_name]

                child_rotation_name = model.joints[translation[child_name]].parent.name
                child_global_rotation = global_transformation[child_rotation_name][1]
                try:
                    parent_real_rotation = Quaternion().between_vectors(bone.size, model.joints[translation[bone.name]].initial_offset).parented(parent_global_rotation)
                except KeyError:
                    parent_real_rotation = parent_global_rotation
                child.local_animation_rotation = Quaternion().between_vectors(child.size, model.joints[translation[child.name]].initial_offset).parented(child_global_rotation).parented(
                    parent_real_rotation.conjugate())

                dfs(child)

        dfs(minecraft_model.root)
        pass
