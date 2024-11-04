from typing import NamedTuple, Tuple
from xanlib.math_utils import UV

class Face(NamedTuple):
    vertex_indices: Tuple[int, int, int]
    texture_index: int
    flags: int
    uv_coords: Tuple[UV, UV, UV]
