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

class Node:
    def __init__(self):
        self.children = []
        self.vertices = []
        self.faces = []
        self.vertexAnimation=None
        self.vertexAnimationCount=None

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
