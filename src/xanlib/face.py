from typing import BinaryIO
from dataclasses import dataclass
from xanlib.math_utils import UV
from struct import unpack


@dataclass
class Face:
    vertex_indices: tuple[int, int, int]
    texture_index: int
    flags: int
    uv_coords: tuple[UV, UV, UV]

    @classmethod
    def fromstream(cls, stream: BinaryIO) -> "Face":
        return Face(
            unpack("<3i", stream.read(4 * 3)),
            unpack("<1i", stream.read(4 * 1))[0],
            unpack("<1i", stream.read(4 * 1))[0],
            (
                UV(*unpack("<2f", stream.read(4 * 2))),
                UV(*unpack("<2f", stream.read(4 * 2))),
                UV(*unpack("<2f", stream.read(4 * 2))),
            ),
        )
