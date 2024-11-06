from typing import BinaryIO
from dataclasses import dataclass
from xanlib.math_utils import UV
from struct import pack, Struct


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

    def tostream(self, stream: BinaryIO) -> None:
        stream.write(pack("<3i", *self.vertex_indices))
        stream.write(pack("<1i", self.texture_index))
        stream.write(pack("<1i", self.flags))
        for uv in self.uv_coords:
            stream.write(pack("2f", *uv))
