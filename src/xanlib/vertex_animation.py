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
    def frombuffer(cls, buffer: bytes, offset: int = 0) -> "VertexAnimation":
        frame_count, count, actual = cls._header_struct.unpack_from(buffer, offset)
        keys_struct = Struct(cls._key_fmt.format(actual=actual))
        keys = list(keys_struct.unpack_from(buffer, offset + cls._header_struct.size))
        if count < 0:
            scale, base_count = cls._compressed_header_struct.unpack_from(
                buffer, offset + cls._header_struct.size + keys_struct.size
            )
            assert count == -base_count
            real_count = base_count // actual
            frames = [
                [
                    CompressedVertex(
                        *CompressedVertex.cstruct.unpack_from(
                            buffer,
                            offset
                            + cls._header_struct.size
                            + keys_struct.size
                            + cls._compressed_header_struct.size
                            + CompressedVertex.cstruct.size * i,
                        )
                    )
                    for i in range(j * real_count, (j + 1) * real_count)
                ]
                for j in range(actual)
            ]
            if scale & 0x80000000:
                interpolation_struct = Struct(
                    cls._interpolation_fmt.format(frame_count=frame_count)
                )
                interpolation_data = list(
                    interpolation_struct.unpack_from(
                        buffer,
                        offset
                        + cls._header_struct.size
                        + keys_struct.size
                        + cls._compressed_header_struct.size
                        + CompressedVertex.cstruct.size * real_count * actual,
                    )
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
