from typing import BinaryIO
from collections.abc import Iterator
from dataclasses import dataclass, field
import re
from xanlib.node import Node, traverse
from struct import Struct


@dataclass
class Scene:
    version: int | None = None
    FXData: bytes = b""
    textureNameData: bytes = b""
    nodes: list[Node] = field(default_factory=list)
    error: Exception | None = None
    unparsed: bytes | None = None
    _header = Struct("<2i")

    @property
    def textures(self) -> list[str]:
        return [
            texture.decode("ascii")
            for texture in re.split(b"\x00\x00|\x00\x02", self.textureNameData)
            if texture
        ]

    def __iter__(self) -> Iterator[Node]:
        for node in self.nodes:
            yield from node

    def __getitem__(self, name: str) -> Node:
        return next(node for node in self if node.name == name)

    def __bytes__(self) -> bytes:
        buffer = (
            self._header.pack(self.version, len(self.FXData))
            + self.FXData
            + len(self.textureNameData).to_bytes(4, "little")
            + self.textureNameData
            + b"".join(bytes(node) for node in self.nodes)
        )
        if self.unparsed is not None:
            buffer += self.unparsed
        else:
            buffer += (-1).to_bytes(4, "little", signed=True)  # EOF

        return buffer

    @classmethod
    def fromstream(cls, stream: BinaryIO) -> "Scene":
        scene = Scene()
        scene.version, fxdata_size = cls._header.unpack(stream.read(cls._header.size))
        scene.FXData = stream.read(fxdata_size)
        texture_data_size = int.from_bytes(stream.read(4), "little")
        scene.textureNameData = stream.read(texture_data_size)
        while True:
            try:
                node = Node.fromstream(stream)
                if node.transform is None:
                    current_position = stream.tell()
                    stream.seek(0, 2)
                    assert current_position == stream.tell(), "Not at EOF"
                    return scene
                scene.nodes.append(node)
            except Exception as e:
                scene.error = e
                scene.unparsed = stream.read()
                return scene


def print_node_names(scene: Scene) -> None:
    for node in scene.nodes:
        traverse(node, lambda n, depth, **kwargs: print(" " * depth * 2 + n.name))
