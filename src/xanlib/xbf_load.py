from typing import BinaryIO
from os import PathLike
from struct import unpack, calcsize, iter_unpack
from xanlib.vertex import Vertex
from xanlib.face import Face
from xanlib.vertex_animation import VertexAnimation
from xanlib.key_animation import KeyAnimation
from xanlib.node import Node
from xanlib.scene import Scene


def read_node(stream: BinaryIO, parent: Node | None = None) -> Node:
    stream_position = stream.tell()
    try:
        node = Node()
        vertex_count = unpack("<i", stream.read(4))[0]
        if vertex_count == -1:
            return node
        node.parent = parent
        header_fmt = "<3i16dI"
        header_size = calcsize(header_fmt)
        flags, face_count, child_count, *transform, name_length = unpack(
            header_fmt, stream.read(header_size)
        )
        flags = Node.Flags(flags)
        node.transform = tuple(transform)
        node.name = stream.read(name_length).decode("ascii")

        node.children = [read_node(stream, node) for _ in range(child_count)]

        vertices_size = Vertex.cstruct.size * vertex_count
        faces_size = Face.cstruct.size * face_count
        mesh_buffer = stream.read(vertices_size + faces_size)

        vertices_buffer = mesh_buffer[:vertices_size]
        node.vertices = [
            Vertex(*coords) for coords in Vertex.cstruct.iter_unpack(vertices_buffer)
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


def load_xbf(filename: str | PathLike) -> Scene:
    scene = Scene(file=filename)
    with open(filename, "rb") as f:
        header_fmt = "<2i"
        header_size = calcsize(header_fmt)
        scene.version, fxdata_size = unpack(header_fmt, f.read(header_size))
        scene.FXData = f.read(fxdata_size)
        texture_data_size = unpack("<i", f.read(4))[0]
        scene.textureNameData = f.read(texture_data_size)
        while True:
            try:
                node = read_node(f)
                if node.transform is None:
                    current_position = f.tell()
                    f.seek(0, 2)
                    assert current_position == f.tell(), "Not at EOF"
                    return scene
                scene.nodes.append(node)
            except Exception as e:
                scene.error = e
                scene.unparsed = f.read()
                return scene
