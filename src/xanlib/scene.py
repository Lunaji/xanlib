from dataclasses import dataclass, field
from typing import Optional, Tuple, List, NamedTuple, Union
from pathlib import Path
from .xbf_base import NodeFlags
import re
from struct import Struct
from xanlib.math_utils import Vector3, Quaternion, UV, Matrix
from xanlib.vertex import Vertex


class Face(NamedTuple):
    vertex_indices: Tuple[int, int, int]
    texture_index: int
    flags: int
    uv_coords: Tuple[UV, UV, UV]

def convert_signed_5bit(v):
    sign=-1 if (v%32)>15 else 1
    return sign*(v%16)

def convert_to_5bit_signed(v):
    #TODO: unit test
    v_clamped = max(-15, min(15, int(round(v))))
    if v_clamped < 0:
        return v_clamped + 32
    else:
        return v_clamped

@dataclass()
class CompressedVertex:
    x: int
    y: int
    z: int
    normal_packed: int
    fmt = Struct('<3hH')

    @property
    def position(self):
        return Vector3(self.x, self.y, self.z)

    @property
    def normal(self):
        return Vector3(*(convert_signed_5bit((self.normal_packed >> shift) & 0x1F)
                         for shift in (0, 5, 10)))

    def as_vertex(self):
        return Vertex(self.position, self.normal)

    def from_vertex(self, vertex):
        """Warning: does not roundtrip"""
        # TODO: unit test

        self.x = vertex.position[0]
        self.y = vertex.position[1]
        self.z = vertex.position[2]
        self.normal_packed = sum(
            (convert_to_5bit_signed(v) & 0x1F) << shift for v, shift in zip(vertex.normal, [0, 5, 10]))

    def as_flag(self):
        return bool((self.normal_packed >> 15) & 1)

class VertexAnimation(NamedTuple):
    frame_count: int
    count: int
    actual: int
    keys: List[int]
    scale: Optional[int]
    base_count: Optional[int]
    real_count: Optional[int]
    frames: Optional[list[CompressedVertex]]
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
        return [texture.decode('ascii') for texture in re.split(b'\x00\x00|\x00\x02', self.textureNameData) if texture]

    def __iter__(self):
        for node in self.nodes:
            yield from node

    def __getitem__(self, name):
        return next(node for node in self if node.name == name)


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
