from dataclasses import dataclass, field
from enum import IntFlag
from xanlib.math_utils import Matrix
from xanlib.vertex import Vertex
from xanlib.face import Face
from xanlib.vertex_animation import VertexAnimation
from xanlib.key_animation import KeyAnimation


@dataclass
class Node:

    class Flags(IntFlag):
        PRELIGHT = 1,
        FACE_DATA = 2,
        VERTEX_ANIMATION = 4,
        KEY_ANIMATION = 8

    parent: 'Node | None' = None
    transform: Matrix | None = None
    name: str = ''
    children: list['Node'] = field(default_factory=list)
    vertices: list[Vertex] = field(default_factory=list)
    faces: list[Face] = field(default_factory=list)
    rgb: list[tuple[int, int, int]] | None = None
    faceData: list[int] | None = None
    vertex_animation: VertexAnimation | None = None
    key_animation: KeyAnimation | None = None

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
