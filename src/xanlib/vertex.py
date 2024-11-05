from typing import BinaryIO
from dataclasses import dataclass
from xanlib.math_utils import Vector3
from struct import unpack


@dataclass
class Vertex:
    position: Vector3
    normal: Vector3

    @classmethod
    def fromstream(cls, stream: BinaryIO) -> "Vertex":
        return Vertex(
            Vector3(*unpack("<3f", stream.read(4 * 3))),
            Vector3(*unpack("<3f", stream.read(4 * 3))),
        )
