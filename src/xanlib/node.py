from collections.abc import Iterator, Callable
from typing import BinaryIO, Any, Optional
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
    _header = Struct("<3i16dI")
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
        buffer = len(self.vertices).to_bytes(4, "little", signed=True)

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
        buffer += self._header.pack(
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
    def frombuffer(cls, buffer: bytes) -> "Node":
        node = cls()
        vertex_count = int.from_bytes(buffer[:4], "little", signed=True)
        buffer = buffer[4:]

        flags, face_count, child_count, *transform, name_length = cls._header.unpack(
            buffer[: cls._header.size]
        )
        flags = Node.Flags(flags)
        buffer = buffer[cls._header.size :]
        node.transform = tuple(transform)
        node.name = buffer[:name_length].decode("ascii")
        buffer = buffer[name_length:]

        for _ in range(child_count):
            child = cls.frombuffer(buffer)
            node.children.append(child)
            buffer = buffer[len(bytes(child)) :]

        vertices_size = Vertex.cstruct.size * vertex_count
        faces_size = Face.cstruct.size * face_count
        mesh_buffer = buffer[: vertices_size + faces_size]
        buffer = buffer[vertices_size + faces_size :]

        vertices_buffer = mesh_buffer[:vertices_size]
        node.vertices = [
            Vertex(*coords) for coords in Vertex.cstruct.iter_unpack(vertices_buffer)
        ]

        faces_buffer = mesh_buffer[vertices_size:]
        node.faces = [
            Face(*fields) for fields in Face.cstruct.iter_unpack(faces_buffer)
        ]

        if Node.Flags.PRELIGHT in flags:
            rgb_buffer = buffer[: cls._rgb.size * vertex_count]
            buffer = buffer[cls._rgb.size * vertex_count :]
            node.rgb = [rgb_tuple for rgb_tuple in cls._rgb.iter_unpack(rgb_buffer)]

        if Node.Flags.SMOOTHING_GROUPS in flags:
            smoothing_groups = Struct(
                cls._smoothing_groups.format(face_count=face_count)
            )
            node.smoothing_groups = list(
                smoothing_groups.unpack(buffer[: smoothing_groups.size])
            )
            buffer = buffer[smoothing_groups.size :]

        if Node.Flags.VERTEX_ANIMATION in flags:
            node.vertex_animation = VertexAnimation.frombuffer(buffer)
            buffer = buffer[len(bytes(node.vertex_animation)) :]

        if Node.Flags.KEY_ANIMATION in flags:
            node.key_animation = KeyAnimation.frombuffer(buffer)

        return node

    @classmethod
    def fromstream(cls, stream: BinaryIO, parent: Optional["Node"] = None) -> "Node":
        stream_position = stream.tell()
        try:
            node = cls()
            vertex_count = int.from_bytes(stream.read(4), "little", signed=True)
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
                rgb_buffer = stream.read(cls._rgb.size * vertex_count)
                node.rgb = [rgb_tuple for rgb_tuple in cls._rgb.iter_unpack(rgb_buffer)]

            if Node.Flags.SMOOTHING_GROUPS in flags:
                smoothing_groups = Struct(
                    cls._smoothing_groups.format(face_count=face_count)
                )
                node.smoothing_groups = list(
                    smoothing_groups.unpack(stream.read(smoothing_groups.size))
                )

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
