from typing import BinaryIO
from collections.abc import Iterator
from dataclasses import dataclass, field
import re
from xanlib.node import Node, traverse
from struct import unpack, calcsize


@dataclass
class Scene:
    version: int | None = None
    FXData: bytes = b""
    textureNameData: bytes = b""
    nodes: list[Node] = field(default_factory=list)
    error: Exception | None = None
    unparsed: bytes | None = None

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

    @classmethod
    def fromstream(cls, stream: BinaryIO) -> "Scene":
        scene = Scene()
        header_fmt = "<2i"
        header_size = calcsize(header_fmt)
        scene.version, fxdata_size = unpack(header_fmt, stream.read(header_size))
        scene.FXData = stream.read(fxdata_size)
        texture_data_size = unpack("<i", stream.read(4))[0]
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
