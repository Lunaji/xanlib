from collections.abc import Iterator, Callable
from typing import BinaryIO, Any, Optional
from dataclasses import dataclass, field
from enum import IntFlag
from xanlib.math_utils import Matrix
from xanlib.vertex import Vertex
from xanlib.face import Face
from xanlib.vertex_animation import VertexAnimation
from xanlib.key_animation import KeyAnimation
from struct import unpack, calcsize, iter_unpack, Struct


@dataclass
class Node:

    class Flags(IntFlag):
        PRELIGHT = 1
        FACE_DATA = 2
        VERTEX_ANIMATION = 4
        KEY_ANIMATION = 8

    parent: "Node | None" = None
    transform: Matrix | None = None
    name: str = ""
    children: list["Node"] = field(default_factory=list)
    vertices: list[Vertex] = field(default_factory=list)
    faces: list[Face] = field(default_factory=list)
    rgb: list[tuple[int, int, int]] | None = None
    faceData: list[int] | None = None
    vertex_animation: VertexAnimation | None = None
    key_animation: KeyAnimation | None = None
    _header = Struct("<3i16dI")

    def __iter__(self) -> Iterator["Node"]:
        yield self
        for child in self.children:
            yield from child

    @property
    def ancestors(self) -> Iterator["Node"]:
        node = self
        while node.parent is not None:
            yield node.parent
            node = node.parent

    @classmethod
    def fromstream(cls, stream: BinaryIO, parent: Optional["Node"] = None) -> "Node":
        stream_position = stream.tell()
        try:
            node = cls()
            vertex_count = unpack("<i", stream.read(4))[0]
            if vertex_count == -1:
                return node
            node.parent = parent
            flags, face_count, child_count, *transform, name_length = (
                cls._header.unpack(stream.read(cls._header.size))
            )
            flags = Node.Flags(flags)
            node.transform = tuple(transform)
            node.name = stream.read(name_length).decode("ascii")

            node.children = [cls.fromstream(stream, node) for _ in range(child_count)]

            vertices_size = Vertex.cstruct.size * vertex_count
            faces_size = Face.cstruct.size * face_count
            mesh_buffer = stream.read(vertices_size + faces_size)

            vertices_buffer = mesh_buffer[:vertices_size]
            node.vertices = [
                Vertex(*coords)
                for coords in Vertex.cstruct.iter_unpack(vertices_buffer)
            ]

            faces_buffer = mesh_buffer[vertices_size:]
            node.faces = [
                Face(*fields) for fields in Face.cstruct.iter_unpack(faces_buffer)
            ]

            if Node.Flags.PRELIGHT in flags:
                rgb_fmt = "<3B"
                rgb_size = calcsize(rgb_fmt)
                node.rgb = [
                    rgb_tuple
                    for rgb_tuple in iter_unpack(
                        rgb_fmt, stream.read(rgb_size * vertex_count)
                    )
                ]

            if Node.Flags.FACE_DATA in flags:
                faceData_fmt = f"<{face_count}i"
                faceData_size = calcsize(faceData_fmt)
                node.faceData = list(unpack(faceData_fmt, stream.read(faceData_size)))

            if Node.Flags.VERTEX_ANIMATION in flags:
                node.vertex_animation = VertexAnimation.fromstream(stream)

            if Node.Flags.KEY_ANIMATION in flags:
                node.key_animation = KeyAnimation.fromstream(stream)

            return node
        except Exception:
            stream.seek(stream_position)
            raise


def traverse(
    node: Node,
    func: Callable[..., None],
    parent: Node | None = None,
    depth: int = 0,
    **kwargs: Any,
) -> None:
    func(node, parent=parent, depth=depth, **kwargs)

    for child in node.children:
        traverse(child, func, parent=node, depth=depth + 1)
