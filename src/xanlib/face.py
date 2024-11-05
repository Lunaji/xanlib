from typing import NamedTuple
from xanlib.math_utils import UV

class Face(NamedTuple):
    vertex_indices: tuple[int, int, int]
    texture_index: int
    flags: int
    uv_coords: tuple[UV, UV, UV]
