from typing import NamedTuple, Optional
from xanlib.math_utils import Vector3, Quaternion, Matrix

class KeyAnimationFrame(NamedTuple):
    frame_id: int
    flag: int
    rotation: Optional[Quaternion]
    scale: Optional[Vector3]
    translation: Optional[Vector3]


class KeyAnimation(NamedTuple):
    frame_count: int
    flags: int
    matrices: Optional[list[Matrix]]
    actual: Optional[int]
    extra_data: Optional[list[int]]
    frames: Optional[list[KeyAnimationFrame]]
