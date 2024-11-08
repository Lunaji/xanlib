from dataclasses import dataclass
from typing import NamedTuple
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

    def __bytes__(self) -> bytes:
        extra_data = b""
        if self.flags in (-1, -2, -3):
            if self.flags == -1:
                matrix_struct = self._matrix16_struct
            elif self.flags == -2:
                matrix_struct = self._matrix12_struct
            else:
                extra_struct = Struct(
                    self._extra_fmt.format(count=self.frame_count + 1)
                )
                extra_data = extra_struct.pack(len(self.matrices), *self.extra_data)
                matrix_struct = self._matrix12_struct
            return (
                self._header_struct.pack(self.frame_count, self.flags)
                + extra_data
                + b"".join(matrix_struct.pack(*matrix) for matrix in self.matrices)
            )
        else:
            buffer = self._header_struct.pack(self.frame_count, self.flags)
            for frame in self.frames:
                buffer += self._pos.pack(frame.frame_id, frame.flag)
                if frame.rotation is not None:
                    buffer += self._quaternion.pack(frame.rotation.w, *frame.rotation.v)
                if frame.scale is not None:
                    buffer += self._vector3.pack(*frame.scale)
                if frame.translation is not None:
                    buffer += self._vector3.pack(*frame.translation)
            return buffer

    @classmethod
    def frombuffer(cls, buffer: bytes, offset: int = 0) -> "KeyAnimation":
        frame_count, flags = cls._header_struct.unpack_from(buffer, offset)
        if flags in (-1, -2, -3):
            extra_size = 0
            if flags == -1:
                matrix_struct = cls._matrix16_struct
                real_count = frame_count + 1
            elif flags == -2:
                matrix_struct = cls._matrix12_struct
                real_count = frame_count + 1
            else:
                extra_struct = Struct(cls._extra_fmt.format(count=frame_count + 1))
                real_count, *extra_data = extra_struct.unpack_from(
                    buffer, offset + cls._header_struct.size
                )
                matrix_struct = cls._matrix12_struct
                extra_size = extra_struct.size
            matrices = [
                matrix_struct.unpack_from(
                    buffer,
                    offset
                    + cls._header_struct.size
                    + extra_size
                    + matrix_struct.size * i,
                )
                for i in range(real_count)
            ]
        else:
            frames = []
            offset += cls._header_struct.size
            for i in range(flags):
                frame_id, flag = cls._pos.unpack_from(buffer, offset)
                offset += cls._pos.size
                assert not (flag & 0b1000111111111111)

                rotation = scale = translation = None
                if (flag >> 12) & 0b001:
                    w, *v = cls._quaternion.unpack_from(buffer, offset)
                    rotation = Quaternion(w, Vector3(*v))
                    offset += cls._quaternion.size
                if (flag >> 12) & 0b010:
                    scale = Vector3(*cls._vector3.unpack_from(buffer, offset))
                    offset += cls._vector3.size
                if (flag >> 12) & 0b100:
                    translation = Vector3(*cls._vector3.unpack_from(buffer, offset))
                    offset += cls._vector3.size

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
