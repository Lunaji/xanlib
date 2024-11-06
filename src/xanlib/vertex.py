from collections.abc import Buffer
from dataclasses import dataclass
from xanlib.math_utils import Vector3
from struct import Struct


@dataclass
class Vertex:
    position: Vector3
    normal: Vector3
    cstruct = Struct("<6f")

    @classmethod
    def frombuffer(cls, buffer: Buffer) -> "Vertex":
        coords = cls.cstruct.unpack(buffer)
        return cls(
            Vector3(*coords[:3]),
            Vector3(*coords[3:]),
        )

    def __bytes__(self) -> bytes:
        return self.cstruct.pack(*self.position, *self.normal)
