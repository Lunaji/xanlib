from typing import BinaryIO
from dataclasses import dataclass
from xanlib.math_utils import UV
from struct import unpack, pack


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

    def tostream(self, stream: BinaryIO) -> None:
        stream.write(pack("<3i", *self.vertex_indices))
        stream.write(pack("<1i", self.texture_index))
        stream.write(pack("<1i", self.flags))
        for uv in self.uv_coords:
            stream.write(pack("2f", *uv))
