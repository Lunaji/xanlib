from typing import BinaryIO
from collections.abc import Buffer
from dataclasses import dataclass
from xanlib.math_utils import Vector3
from struct import Struct


@dataclass
class Vertex:
    position: Vector3
    normal: Vector3
    _struct = Struct("<6f")

    @classmethod
    def frombytes(cls, buffer: Buffer) -> "Vertex":
        coords = cls._struct.unpack(buffer)
        return cls(
            Vector3(*coords[:3]),
            Vector3(*coords[3:]),
        )

    @classmethod
    def fromstream(cls, stream: BinaryIO) -> "Vertex":
        buffer = stream.read(cls._struct.size)
        return cls.frombytes(buffer)
