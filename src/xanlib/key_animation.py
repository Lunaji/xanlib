from dataclasses import dataclass
from typing import BinaryIO, NamedTuple
from xanlib.math_utils import Vector3, Quaternion, Matrix
from struct import unpack, calcsize


class KeyAnimationFrame(NamedTuple):
    frame_id: int
    flag: int
    rotation: Quaternion | None
    scale: Vector3 | None
    translation: Vector3 | None


@dataclass
class KeyAnimation:
    frame_count: int
    flags: int
    matrices: list[Matrix]
    extra_data: list[int]
    frames: list[KeyAnimationFrame]

    @classmethod
    def fromstream(cls, stream: BinaryIO) -> "KeyAnimation":
        header_fmt = "<2i"
        header_size = calcsize(header_fmt)
        frame_count, flags = unpack(header_fmt, stream.read(header_size))
        if flags == -1:
            matrices = [
                unpack("<16f", stream.read(4 * 16)) for _ in range(frame_count + 1)
            ]
        elif flags == -2:
            matrices = [
                unpack("<12f", stream.read(4 * 12)) for _ in range(frame_count + 1)
            ]
        elif flags == -3:
            extra_fmt = f"i{frame_count + 1}h"
            extra_size = calcsize(extra_fmt)
            matrix_count, *extra_data = unpack(extra_fmt, stream.read(extra_size))
            matrices = [
                unpack("<12f", stream.read(4 * 12)) for _ in range(matrix_count)
            ]
        else:
            frames = []
            for i in range(flags):
                pos_fmt = "<2h"
                pos_size = calcsize(pos_fmt)
                frame_id, flag = unpack(pos_fmt, stream.read(pos_size))
                assert not (flag & 0b1000111111111111)

                if (flag >> 12) & 0b001:
                    w, *v = unpack("<4f", stream.read(4 * 4))
                    rotation = Quaternion(w, Vector3(*v))
                else:
                    rotation = None
                if (flag >> 12) & 0b010:
                    scale = Vector3(*unpack("<3f", stream.read(4 * 3)))
                else:
                    scale = None
                if (flag >> 12) & 0b100:
                    translation = Vector3(*unpack("<3f", stream.read(4 * 3)))
                else:
                    translation = None

                frames.append(
                    KeyAnimationFrame(frame_id, flag, rotation, scale, translation)
                )

        return KeyAnimation(
            frame_count,
            flags,
            matrices if flags in (-1, -2, -3) else [],
            extra_data if flags == -3 else [],
            frames if flags not in (-1, -2, -3) else [],
        )
