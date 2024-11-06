from typing import BinaryIO
from dataclasses import dataclass
from xanlib.compressed_vertex import CompressedVertex
from struct import unpack, calcsize, Struct


@dataclass
class VertexAnimation:
    frame_count: int
    count: int
    actual: int
    keys: list[int]
    scale: int | None
    base_count: int | None
    real_count: int | None
    frames: list[list[CompressedVertex]]
    interpolation_data: list[int]
    _header_struct = Struct("<3i")
    _key_fmt = "{actual}I"

    @classmethod
    def fromstream(cls, stream: BinaryIO) -> "VertexAnimation":
        header_buffer = stream.read(cls._header_struct.size)
        frame_count, count, actual = cls._header_struct.unpack(header_buffer)
        keys_struct = Struct(cls._key_fmt.format(actual=actual))
        keys_buffer = stream.read(keys_struct.size)
        keys = list(keys_struct.unpack(keys_buffer))
        if count < 0:  # compressed
            compressed_header_fmt = "<2I"
            compressed_header_size = calcsize(compressed_header_fmt)
            scale, base_count = unpack(
                compressed_header_fmt, stream.read(compressed_header_size)
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
                interpolation_fmt = f"<{frame_count}I"
                interpolation_size = calcsize(interpolation_fmt)
                interpolation_data = list(
                    unpack(interpolation_fmt, stream.read(interpolation_size))
                )

        return VertexAnimation(
            frame_count,
            count,
            actual,
            keys,
            scale if count < 0 else None,
            base_count if count < 0 else None,
            real_count if count < 0 else None,
            frames if count < 0 else [],
            interpolation_data if count < 0 and scale & 0x80000000 else [],
        )
