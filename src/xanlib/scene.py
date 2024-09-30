from dataclasses import dataclass, field
from typing import Optional, Tuple, List, NamedTuple


class Vector3(NamedTuple):
    x: float
    y: float
    z: float

class Quaternion(NamedTuple):
    w: float
    v: Vector3

class UV(NamedTuple):
    u: float
    v: float

class Vertex(NamedTuple):
    position: Vector3
    normal: Vector3

class Face(NamedTuple):
    vertex_indices: Tuple[int, int, int]
    texture_index: int
    flags: int
    uv_coords: Tuple[UV, UV, UV]

class VertexAnimationFrameDatum(NamedTuple):
    x: int
    y: int
    z: int
    normal_packed: int

class VertexAnimation(NamedTuple):
    frame_count: int
    count: int
    actual: int
    keys: List[int]
    scale: Optional[int]
    base_count: Optional[int]
    real_count: Optional[int]
    frames: Optional[list]
    interpolation_data: Optional[List[int]]

class KeyAnimationFrame(NamedTuple):
    frame_id: int
    flag: int
    rotation: Optional[Quaternion]
    scale: Optional[Vector3]
    translation: Optional[Vector3]
    
class KeyAnimation(NamedTuple):
    frame_count: int
    flags: int
    matrices: list
    actual: Optional[int]
    extra_data: Optional[List[int]]
    frames: Optional[List[KeyAnimationFrame]]

class Node:
    def __init__(self):
        self.children = []
        self.vertices = []
        self.faces = []
        self.vertex_animation=None
        self.key_animation=None
        self.parent = None

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


@dataclass
class Scene:
    nodes: List['Node'] = field(default_factory=list)
    error: Optional[Exception] = None
    unparsed: Optional[Exception] = None

    @property
    def textures(self):
        return [texture.decode() for texture in self.textureNameData.split(b'\x00\x00') if texture]

    def __iter__(self):
        for node in self.nodes:
            yield from node


def traverse(node, func, parent=None, depth=0, **kwargs):
    func(node, parent=parent, depth=depth, **kwargs)

    for child in node.children:
        traverse(child, func, parent=node, depth=depth+1)

def print_node_names(scene):
    for node in scene.nodes:
        traverse(
            node,
            lambda n, depth, **kwargs: print(' ' * depth * 2 + n.name)
        )
