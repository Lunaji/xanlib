from typing import NamedTuple
from xanlib.math_utils import Vector3


class Vertex(NamedTuple):
    position: Vector3
    normal: Vector3
