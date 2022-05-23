from __future__ import annotations

from typing import Optional

from math_objects import Vector3, Quaternion


class Armature:
    def __init__(self):
        pass


class DisplayVoxel:
    pass


class Bone:
    local_offset: Vector3
    display: DisplayVoxel
    parent: Optional[Bone]
    children: list[Bone]

    animation_rotation: Quaternion
    animation_displacement: Vector3

    def __init__(self):
        self.local_offset = Vector3()
        self.display = DisplayVoxel()

