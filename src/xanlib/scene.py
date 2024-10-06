from dataclasses import dataclass, field
from typing import Optional, Tuple, List, TypeAlias

Vector3: TypeAlias = Tuple[float, float, float]
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
class KeyAnimation:
    frame_count: int
    flags: int
    matrices: list
    actual: Optional[int]
    extra_data: Optional[List[int]]

@dataclass    
class AnimationRange:
    repeat: int
    unknown1 : int
    unknown2 : int
    start: int
    end: int
    
@dataclass    
class Animation:
    name: str
    args: List[int]
    ranges: List['AnimationRange']


@dataclass    
class FXEvent:
    type: int
    typename: str
    unknown : int
    is_long : int
    head_args : List[int]
    name1 : str
    name2 : str
    tail_args : List[int]
    frame_index: int

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
    animations : List['Animation'] = field(default_factory=list)
    events : List['FXEvent'] = field(default_factory=list)
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
