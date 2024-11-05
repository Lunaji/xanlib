from dataclasses import dataclass, field
from typing import Optional
from os import PathLike
import re
from xanlib.node import Node, traverse


@dataclass
class Scene:
    file: str | PathLike
    version: Optional[int] = None
    FXData: bytes = b''
    textureNameData: bytes = b''
    nodes: list[Node] = field(default_factory=list)
    error: Optional[Exception] = None
    unparsed: Optional[bytes] = None

    @property
    def textures(self):
        return [texture.decode('ascii') for texture in re.split(b'\x00\x00|\x00\x02', self.textureNameData) if texture]

    def __iter__(self):
        for node in self.nodes:
            yield from node

    def __getitem__(self, name):
        return next(node for node in self if node.name == name)


def print_node_names(scene):
    for node in scene.nodes:
        traverse(
            node,
            lambda n, depth, **kwargs: print(' ' * depth * 2 + n.name)
        )
