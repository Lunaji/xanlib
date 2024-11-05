from dataclasses import dataclass
from xanlib.compressed_vertex import CompressedVertex

@dataclass
class VertexAnimation:
    frame_count: int
    count: int
    actual: int
    keys: list[int]
    scale: int | None
    base_count: int | None
    real_count: int | None
    frames: list[list[CompressedVertex]]
    interpolation_data: list[int]
