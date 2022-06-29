from __future__ import annotations

from typing import Optional

from export_file import DisplayVoxel
from math_objects import Vector3, Quaternion


class Bone:
    start_joint_name: str
    end_joint_name: str

    parent: Optional[Bone]
    children: dict[str, Bone]

    initial_offset: Vector3

    animation_rotation: Quaternion
    animation_offset: Vector3

    display: DisplayVoxel

# class MinecraftArmature:
#     def __init__(self):
