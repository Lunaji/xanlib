from collections.abc import Iterator, Callable
from typing import Any
from dataclasses import dataclass, field
from enum import IntFlag
from xanlib.math_utils import Matrix
from xanlib.vertex import Vertex
from xanlib.face import Face
from xanlib.vertex_animation import VertexAnimation
from xanlib.key_animation import KeyAnimation
from struct import Struct


@dataclass
class Node:

    class Flags(IntFlag):
        PRELIGHT = 1
        SMOOTHING_GROUPS = 2
        VERTEX_ANIMATION = 4
        KEY_ANIMATION = 8

    parent: "Node | None" = None
    transform: Matrix | None = None
    name: str = ""
    children: list["Node"] = field(default_factory=list)
    vertices: list[Vertex] = field(default_factory=list)
    faces: list[Face] = field(default_factory=list)
    rgb: list[tuple[int, int, int]] | None = None
    smoothing_groups: list[int] | None = None
    vertex_animation: VertexAnimation | None = None
    key_animation: KeyAnimation | None = None
    _header = Struct("<4i16dI")
    _rgb = Struct("<3B")
    _smoothing_groups = "<{face_count}i"

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

    def __bytes__(self) -> bytes:
        extras = b""
        flags = Node.Flags(0)
        if self.rgb is not None:
            flags |= self.Flags.PRELIGHT
            extras += b"".join(self._rgb.pack(*rgb) for rgb in self.rgb)
        if self.smoothing_groups is not None:
            flags |= self.Flags.SMOOTHING_GROUPS
            smoothing_groups = Struct(
                self._smoothing_groups.format(face_count=len(self.faces))
            )
            extras += smoothing_groups.pack(*self.smoothing_groups)
        if self.vertex_animation is not None:
            flags |= self.Flags.VERTEX_ANIMATION
            extras += bytes(self.vertex_animation)
        if self.key_animation is not None:
            flags |= self.Flags.KEY_ANIMATION
            extras += bytes(self.key_animation)

        assert self.transform is not None
        buffer = self._header.pack(
            len(self.vertices),
            flags,
            len(self.faces),
            len(self.children),
            *self.transform,
            len(self.name),
        ) + self.name.encode("ascii")

        buffer += b"".join(bytes(child) for child in self.children)
        buffer += b"".join(bytes(vertex) for vertex in self.vertices)
        buffer += b"".join(bytes(face) for face in self.faces)

        return buffer + extras

    @classmethod
    def frombuffer(
        cls, buffer: bytes, offset: int = 0, parent: "Node | None" = None
    ) -> "Node":
        node = cls(parent=parent)

        vertex_count, flags, face_count, child_count, *transform, name_length = (
            cls._header.unpack_from(buffer, offset)
        )
        offset += cls._header.size
        flags = Node.Flags(flags)
        node.transform = tuple(transform)
        node.name = buffer[offset : offset + name_length].decode("ascii")
        offset += name_length

        for _ in range(child_count):
            child = cls.frombuffer(buffer, offset, parent=node)
            node.children.append(child)
            offset += len(bytes(child))

        vertices_size = Vertex.cstruct.size * vertex_count
        vertex_buffer = buffer[offset : offset + vertices_size]
        node.vertices = [
            Vertex(*coords) for coords in Vertex.cstruct.iter_unpack(vertex_buffer)
        ]
        offset += vertices_size

        faces_size = Face.cstruct.size * face_count
        face_buffer = buffer[offset : offset + faces_size]
        node.faces = [Face(*fields) for fields in Face.cstruct.iter_unpack(face_buffer)]
        offset += faces_size

        if Node.Flags.PRELIGHT in flags:
            rgb_buffer = buffer[offset : offset + cls._rgb.size * vertex_count]
            node.rgb = [rgb_tuple for rgb_tuple in cls._rgb.iter_unpack(rgb_buffer)]
            offset += cls._rgb.size * vertex_count

        if Node.Flags.SMOOTHING_GROUPS in flags:
            smoothing_groups = Struct(
                cls._smoothing_groups.format(face_count=face_count)
            )
            node.smoothing_groups = list(smoothing_groups.unpack_from(buffer, offset))
            offset += smoothing_groups.size

        if Node.Flags.VERTEX_ANIMATION in flags:
            node.vertex_animation = VertexAnimation.frombuffer(buffer, offset)
            offset += len(bytes(node.vertex_animation))

        if Node.Flags.KEY_ANIMATION in flags:
            node.key_animation = KeyAnimation.frombuffer(buffer, offset)
            offset += len(bytes(node.key_animation))

        return node


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
