from typing import BinaryIO
from dataclasses import dataclass
from xanlib.math_utils import UV
from struct import Struct


@dataclass
class Face:
    cstruct = Struct("<5i6f")

    def __init__(
        self,
        vertex_index_1: int,
        vertex_index_2: int,
        vertex_index_3: int,
        texture_index: int,
        flags: int,
        uv1u: float,
        uv1v: float,
        uv2u: float,
        uv2v: float,
        uv3u: float,
        uv3v: float,
    ) -> None:
        self.vertex_indices = (vertex_index_1, vertex_index_2, vertex_index_3)
        self.texture_index = texture_index
        self.flags = flags
        self.uv_coords = (UV(uv1u, uv1v), UV(uv2u, uv2v), UV(uv3u, uv3v))

    def __bytes__(self):
        uv_coords = (coord for uv in self.uv_coords for coord in uv)
        return self.cstruct.pack(
            *self.vertex_indices,
            self.texture_index,
            self.flags,
            *uv_coords,
        )

    def tostream(self, stream: BinaryIO) -> None:
        stream.write(bytes(self))
