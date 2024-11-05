from typing import BinaryIO
from dataclasses import dataclass
from xanlib.math_utils import Vector3
from struct import Struct


@dataclass
class Vertex:
    position: Vector3
    normal: Vector3
    _struct = Struct("<6f")

    @classmethod
    def fromstream(cls, stream: BinaryIO) -> "Vertex":
        buffer = stream.read(cls._struct.size)
        coords = cls._struct.unpack(buffer)
        return cls(
            Vector3(*coords[:3]),
            Vector3(*coords[3:]),
        )
