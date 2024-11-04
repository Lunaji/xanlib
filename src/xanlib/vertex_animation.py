from dataclasses import dataclass
from typing import Optional
from xanlib.compressed_vertex import CompressedVertex

@dataclass
class VertexAnimation:
    frame_count: int
    count: int
    actual: int
    keys: list[int]
    scale: Optional[int]
    base_count: Optional[int]
    real_count: Optional[int]
    frames: list[list[CompressedVertex]]
    interpolation_data: list[int]
