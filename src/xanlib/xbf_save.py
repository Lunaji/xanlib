from typing import BinaryIO
from os import PathLike
from struct import pack, Struct
from xanlib.node import Node
from xanlib.scene import Scene


def write_node(stream: BinaryIO, node: Node) -> None:
    header_fmt = Struct(f"<4i16dI{len(node.name)}s")

    flags = Node.Flags(0)
    if node.rgb is not None:
        flags |= Node.Flags.PRELIGHT
    if node.faceData is not None:
        flags |= Node.Flags.FACE_DATA
    if node.vertex_animation is not None:
        flags |= Node.Flags.VERTEX_ANIMATION
    if node.key_animation is not None:
        flags |= Node.Flags.KEY_ANIMATION

    assert node.transform is not None
    stream.write(
        header_fmt.pack(
            len(node.vertices),
            flags,
            len(node.faces),
            len(node.children),
            *node.transform,
            len(node.name),
            node.name.encode("ascii"),
        )
    )

    for child in node.children:
        write_node(stream, child)

    vertices = b"".join(bytes(vertex) for vertex in node.vertices)
    faces = b"".join(bytes(face) for face in node.faces)
    stream.write(vertices + faces)

    if node.rgb is not None:
        rgb_fmt = Struct(f"<{3*len(node.rgb)}B")
        stream.write(rgb_fmt.pack(*(c for rgb in node.rgb for c in rgb)))

    if node.faceData is not None:
        stream.write(pack(f"<{len(node.faceData)}i", *node.faceData))

    if node.vertex_animation is not None:
        stream.write(bytes(node.vertex_animation))

    if node.key_animation is not None:
        stream.write(bytes(node.key_animation))


def save_xbf(scene: Scene, filename: str | PathLike) -> None:
    with open(filename, "wb") as f:
        header_fmt = Struct(f"<2i{len(scene.FXData)}si{len(scene.textureNameData)}s")
        f.write(
            header_fmt.pack(
                scene.version,
                len(scene.FXData),
                scene.FXData,
                len(scene.textureNameData),
                scene.textureNameData,
            )
        )
        for node in scene.nodes:
            write_node(f, node)
        if scene.unparsed is not None:
            f.write(scene.unparsed)
        else:
            f.write(pack("i", -1))
