from dataclasses import dataclass, field
from typing import Optional
from enum import IntFlag
from xanlib.math_utils import Matrix
from xanlib.vertex import Vertex
from xanlib.face import Face
from xanlib.vertex_animation import VertexAnimation
from xanlib.key_animation import KeyAnimation


class NodeFlags(IntFlag):
    PRELIGHT = 1,
    FACE_DATA = 2,
    VERTEX_ANIMATION = 4,
    KEY_ANIMATION = 8

@dataclass
class Node:
    parent: Optional['Node'] = None
    flags: Optional[NodeFlags] = None
    transform: Optional[Matrix] = None
    name: Optional[str] = None
    children: list['Node'] = field(default_factory=list)
    vertices: list[Vertex] = field(default_factory=list)
    faces: list[Face] = field(default_factory=list)
    rgb: Optional[list[tuple[int, int, int]]] = None
    faceData: Optional[list[int]] = None
    vertex_animation: Optional[VertexAnimation] = None
    key_animation: Optional[KeyAnimation] = None

    def __iter__(self):
        yield self
        for child in self.children:
            yield from child

    @property
    def ancestors(self):
        node = self
        while node.parent is not None:
            yield node.parent
            node = node.parent


def traverse(node, func, parent=None, depth=0, **kwargs):
    func(node, parent=parent, depth=depth, **kwargs)

    for child in node.children:
        traverse(child, func, parent=node, depth=depth+1)
