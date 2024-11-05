from typing import NamedTuple
from xanlib.math_utils import Vector3, Quaternion, Matrix


class KeyAnimationFrame(NamedTuple):
    frame_id: int
    flag: int
    rotation: Quaternion | None
    scale: Vector3 | None
    translation: Vector3 | None


class KeyAnimation(NamedTuple):
    frame_count: int
    flags: int
    matrices: list[Matrix]
    extra_data: list[int]
    frames: list[KeyAnimationFrame]
