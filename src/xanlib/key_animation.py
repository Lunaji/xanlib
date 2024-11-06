from dataclasses import dataclass
from typing import BinaryIO, NamedTuple
from xanlib.math_utils import Vector3, Quaternion, Matrix
from struct import Struct


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
    _header_struct = Struct("<2i")
    _matrix16_struct = Struct("<16f")
    _matrix12_struct = Struct("<12f")
    _extra_fmt = "<i{count}h"
    _pos = Struct("<2h")
    _quaternion = Struct("<4f")
    _vector3 = Struct("<3f")

    @classmethod
    def fromstream(cls, stream: BinaryIO) -> "KeyAnimation":
        frame_count, flags = cls._header_struct.unpack(
            stream.read(cls._header_struct.size)
        )
        if flags == -1:
            matrix_buffer = stream.read(cls._matrix16_struct.size * (frame_count + 1))
            matrices = [
                matrix for matrix in cls._matrix16_struct.iter_unpack(matrix_buffer)
            ]
        elif flags == -2:
            matrix_buffer = stream.read(cls._matrix12_struct.size * (frame_count + 1))
            matrices = [
                matrix for matrix in cls._matrix12_struct.iter_unpack(matrix_buffer)
            ]
        elif flags == -3:
            extra_struct = Struct(cls._extra_fmt.format(count=frame_count + 1))
            matrix_count, *extra_data = extra_struct.unpack(
                stream.read(extra_struct.size)
            )
            matrix_buffer = stream.read(cls._matrix12_struct.size * matrix_count)
            matrices = [
                matrix for matrix in cls._matrix12_struct.iter_unpack(matrix_buffer)
            ]
        else:
            frames = []
            for i in range(flags):
                frame_id, flag = cls._pos.unpack(stream.read(cls._pos.size))
                assert not (flag & 0b1000111111111111)

                if (flag >> 12) & 0b001:
                    w, *v = cls._quaternion.unpack(stream.read(cls._quaternion.size))
                    rotation = Quaternion(w, Vector3(*v))
                else:
                    rotation = None
                if (flag >> 12) & 0b010:
                    scale = Vector3(
                        *cls._vector3.unpack(stream.read(cls._vector3.size))
                    )
                else:
                    scale = None
                if (flag >> 12) & 0b100:
                    translation = Vector3(
                        *cls._vector3.unpack(stream.read(cls._vector3.size))
                    )
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
