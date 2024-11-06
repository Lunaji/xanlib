from typing import BinaryIO
from dataclasses import dataclass
from xanlib.compressed_vertex import CompressedVertex
from struct import Struct, pack


@dataclass
class VertexAnimation:
    frame_count: int
    count: int
    keys: list[int]
    scale: int | None
    base_count: int | None
    real_count: int | None
    frames: list[list[CompressedVertex]]
    interpolation_data: list[int]
    _header_struct = Struct("<3i")
    _key_fmt = "<{actual}I"
    _compressed_header_struct = Struct("<2I")
    _interpolation_fmt = "<{frame_count}I"

    def __bytes__(self) -> bytes:
        buffer = self._header_struct.pack(self.frame_count, self.count, len(self.keys))
        buffer += pack(self._key_fmt.format(actual=len(self.keys)), *self.keys)
        if self.frames:
            buffer += self._compressed_header_struct.pack(self.scale, self.base_count)
            buffer += b"".join(
                bytes(vertex) for frame in self.frames for vertex in frame
            )
            if self.interpolation_data:
                buffer += pack(
                    self._interpolation_fmt.format(frame_count=self.frame_count),
                    *self.interpolation_data,
                )

        return buffer

    @classmethod
    def fromstream(cls, stream: BinaryIO) -> "VertexAnimation":
        header_buffer = stream.read(cls._header_struct.size)
        frame_count, count, actual = cls._header_struct.unpack(header_buffer)
        keys_struct = Struct(cls._key_fmt.format(actual=actual))
        keys_buffer = stream.read(keys_struct.size)
        keys = list(keys_struct.unpack(keys_buffer))
        if count < 0:  # compressed
            scale, base_count = cls._compressed_header_struct.unpack(
                stream.read(cls._compressed_header_struct.size)
            )
            assert count == -base_count
            real_count = base_count // actual
            frames_buffer = stream.read(
                CompressedVertex.cstruct.size * real_count * actual
            )
            frames = [
                [
                    CompressedVertex(
                        *CompressedVertex.cstruct.unpack_from(
                            frames_buffer, i * CompressedVertex.cstruct.size
                        )
                    )
                    for i in range(j * real_count, (j + 1) * real_count)
                ]
                for j in range(actual)
            ]
            if scale & 0x80000000:  # interpolated
                interpolation_struct = Struct(
                    cls._interpolation_fmt.format(frame_count=frame_count)
                )
                interpolation_buffer = stream.read(interpolation_struct.size)
                interpolation_data = list(
                    interpolation_struct.unpack(interpolation_buffer)
                )

        return VertexAnimation(
            frame_count,
            count,
            keys,
            scale if count < 0 else None,
            base_count if count < 0 else None,
            real_count if count < 0 else None,
            frames if count < 0 else [],
            interpolation_data if count < 0 and scale & 0x80000000 else [],
        )
