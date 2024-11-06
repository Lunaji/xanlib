from collections.abc import Buffer
from typing import BinaryIO
from dataclasses import dataclass
from xanlib.math_utils import UV
from struct import pack, Struct


@dataclass
class Face:
    vertex_indices: tuple[int, int, int]
    texture_index: int
    flags: int
    uv_coords: tuple[UV, UV, UV]
    cstruct = Struct("<5i6f")

    @classmethod
    def frombuffer(cls, buffer: Buffer) -> "Face":
        data = cls.cstruct.unpack(buffer)
        return Face(
            vertex_indices=(data[0], data[1], data[2]),
            texture_index=data[3],
            flags=data[4],
            uv_coords=(
                UV(data[5], data[6]),
                UV(data[7], data[8]),
                UV(data[9], data[10]),
            ),
        )

    @classmethod
    def fromstream(cls, stream: BinaryIO) -> "Face":
        return cls.frombuffer(stream.read(cls.cstruct.size))

    def tostream(self, stream: BinaryIO) -> None:
        stream.write(pack("<3i", *self.vertex_indices))
        stream.write(pack("<1i", self.texture_index))
        stream.write(pack("<1i", self.flags))
        for uv in self.uv_coords:
            stream.write(pack("2f", *uv))
