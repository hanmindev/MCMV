from armature_formatter import ArmatureFormatter
from armature_objects import ArmatureModel, MinecraftModel, ArmatureFrame, Bone, PositionalBone
from math_objects import Vector3, Quaternion, Euler


class RotationFixer:
    """Fixes the issue of quaternions not being able to represent beyond 180 degrees, which causes issues when interpolating between angles close to 180."""
    _last_rotations: dict[str, tuple[Euler, Vector3]]

    # previous, bias

    def __init__(self):
        self._last_rotations = {}

    def fix_rotation(self, identifier: str, angle: Euler):
        if identifier not in self._last_rotations:
            self._last_rotations[identifier] = (angle.copy(), Vector3())
            return angle

        rotation = angle.copy()
        prev, bias = self._last_rotations[identifier]

        rotation.x += bias.x
        rotation.y += bias.y
        rotation.z += bias.z

        if prev.x is not None and abs(prev.x - rotation.x) > 180:
            if prev.x < bias.x < rotation.x:
                rotation.x -= 360.0
                bias.x -= 360.0
            elif prev.x > bias.x > rotation.x:
                rotation.x += 360.0
                bias.x += 360.0
        prev.x = rotation.x

        if prev.y is not None and abs(prev.y - rotation.y) > 180:
            if prev.y < bias.y < rotation.y:
                rotation.y -= 360.0
                bias.y -= 360.0
            elif prev.y > bias.y > rotation.y:
                rotation.y += 360.0
                bias.y += 360.0
        prev.y = rotation.y

        if prev.z is not None and abs(prev.z - rotation.z) > 180:
            if prev.z < bias.z < rotation.z:
                rotation.z -= 360.0
                bias.z -= 360.0
            elif prev.z > bias.z > rotation.z:
                rotation.z += 360.0
                bias.z += 360.0
        prev.z = rotation.z

        return rotation


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

                child_real_rotation = Quaternion().between_vectors(child.size, model.joints[translation[child.name]].initial_offset).parented(child_global_rotation)

                child.local_animation_rotation = child_real_rotation.parented(parent_real_rotation.conjugate())
                if isinstance(child, PositionalBone):
                    try:
                        parent_global_position = global_transformation[translation[bone.name]][0]
                    except KeyError:
                        parent_global_position = Vector3()
                    child.local_animation_position = global_transformation[translation[child_name]][0] - parent_global_position

                dfs(child)

        dfs(minecraft_model.root)

    @staticmethod
    def get_global_minecraft(minecraft_model: MinecraftModel) -> dict[str, tuple[Vector3, Quaternion]]:
        global_transformation = {minecraft_model.root.name: (Vector3(), Quaternion())}

        def dfs(bone: Bone):
            parent_translation, parent_rotation = global_transformation[bone.name]

            for child_name in bone.children:
                child = bone.children[child_name]

                if isinstance(child, PositionalBone):
                    child_translation_offset = child.local_animation_position
                else:
                    child_translation_offset = Vector3()

                child_rotation = child.local_animation_rotation.parented(parent_rotation)
                child_translation = parent_translation + (bone.size + child.offset).rotated_by_quaternion(parent_rotation) + child_translation_offset

                global_transformation[child_name] = (child_translation, child_rotation)

                dfs(child)

        dfs(minecraft_model.root)

        return global_transformation
