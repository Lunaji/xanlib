from dataclasses import dataclass, field
from typing import Optional, Tuple, List, TypeAlias


Vector3: TypeAlias = Tuple[float, float, float]
Quaternion: TypeAlias = Tuple[float, Vector3]
UV: TypeAlias = Tuple[float, float]


@dataclass
class Vertex:
    position: Vector3
    normal: Vector3

@dataclass
class Face:
    vertex_indices: Tuple[int, int, int]
    texture_index: int
    flags: int
    uv_coords: Tuple[UV, UV, UV]

@dataclass    
class VertexAnimation:
    frame_count: int
    count: int
    actual: int
    keys: List[int]
    scale: Optional[int]
    base_count: Optional[int]
    real_count: Optional[int]
    body: Optional[list]
    interpolation_data: Optional[List[int]]

@dataclass
class KeyAnimationFrame:
    frame_id: int
    flag: int
    rotation: Optional[Quaternion]
    scale: Optional[Vector3]
    translation: Optional[Vector3]
    
@dataclass
class KeyAnimation:
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

@dataclass
class Scene:
    nodes: List['Node'] = field(default_factory=list)
    error: Optional[Exception] = None
    unparsed: Optional[Exception] = None
    

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
