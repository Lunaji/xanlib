from dataclasses import dataclass, field
from typing import Optional, Tuple, List, NamedTuple, Union, TypeAlias
from pathlib import Path
from .xbf_base import NodeFlags
import re


Matrix: TypeAlias = Tuple[float, float, float, float, float, float, float, float, float, float, float, float, float, float, float, float]

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
    frames: Optional[List[VertexAnimationFrameDatum]]
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
    matrices: Optional[List[Matrix]]
    actual: Optional[int]
    extra_data: Optional[List[int]]
    frames: Optional[List[KeyAnimationFrame]]

@dataclass
class Node:
    parent: Optional['Node'] = None
    flags: Optional[NodeFlags] = None
    transform: Optional[Matrix] = None
    name: Optional[str] = None
    children: List['Node'] = field(default_factory=list)
    vertices: List[Vertex] = field(default_factory=list)
    faces: List[Face] = field(default_factory=list)
    rgb: Optional[List[Tuple[int, int, int]]] = None
    faceData: Optional[List[int]] = None
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

@dataclass
class Scene:
    file: Optional[Union[str, Path]] = None
    version: Optional[int] = None
    FXData: Optional[bytes] = None
    textureNameData: Optional[bytes] = None
    nodes: List[Node] = field(default_factory=list)
    error: Optional[Exception] = None
    unparsed: Optional[bytes] = None

    @property
    def textures(self):
        return [texture.decode() for texture in re.split(b'\x00\x00|\x00\x02', self.textureNameData) if texture]

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
