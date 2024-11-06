from collections.abc import Buffer
from dataclasses import dataclass
from xanlib.math_utils import Vector3
from struct import Struct


@dataclass(init=False)
class Vertex:
    cstruct = Struct("<6f")

    def __init__(
        self, x: float, y: float, z: float, nx: float, ny: float, nz: float
    ) -> None:
        self.position = Vector3(x, y, z)
        self.normal = Vector3(nx, ny, nz)

    @classmethod
    def frombuffer(cls, buffer: Buffer) -> "Vertex":
        coords = cls.cstruct.unpack(buffer)
        return cls(*coords)

    def __bytes__(self) -> bytes:
        return self.cstruct.pack(*self.position, *self.normal)
