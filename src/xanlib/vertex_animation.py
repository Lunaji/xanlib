from typing import NamedTuple, Optional
from xanlib.compressed_vertex import CompressedVertex

class VertexAnimation(NamedTuple):
    frame_count: int
    count: int
    actual: int
    keys: list[int]
    scale: Optional[int]
    base_count: Optional[int]
    real_count: Optional[int]
    frames: Optional[list[CompressedVertex]]
    interpolation_data: Optional[list[int]]
