from dataclasses import dataclass
from struct import Struct
from xanlib.math_utils import Vector3
from xanlib.vertex import Vertex


def convert_signed_5bit(v: int) -> int:
    sign = -1 if (v % 32) > 15 else 1
    return sign * (v % 16)


def convert_to_5bit_signed(v: int) -> int:
    # TODO: unit test
    v_clamped = max(-15, min(15, int(round(v))))
    if v_clamped < 0:
        return v_clamped + 32
    else:
        return v_clamped


@dataclass
class CompressedVertex:
    x: int
    y: int
    z: int
    normal_packed: int
    fmt = Struct("<3hH")

    @property
    def position(self) -> Vector3:
        return Vector3(self.x, self.y, self.z)

    @property
    def normal(self) -> Vector3:
        return Vector3(
            *(
                convert_signed_5bit((self.normal_packed >> shift) & 0x1F)
                for shift in (0, 5, 10)
            )
        )

    def as_vertex(self) -> Vertex:
        return Vertex(self.position, self.normal)

    def from_vertex(self, vertex: Vertex) -> None:
        """Warning: does not roundtrip"""
        # TODO: unit test

        self.x = int(vertex.position[0])
        self.y = int(vertex.position[1])
        self.z = int(vertex.position[2])
        self.normal_packed = sum(
            (convert_to_5bit_signed(int(v)) & 0x1F) << shift
            for v, shift in zip(vertex.normal, [0, 5, 10])
        )

    def as_flag(self) -> bool:
        return bool((self.normal_packed >> 15) & 1)
