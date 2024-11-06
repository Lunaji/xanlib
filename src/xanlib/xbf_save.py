from typing import BinaryIO
from os import PathLike
from struct import pack, Struct
from xanlib.compressed_vertex import CompressedVertex
from xanlib.vertex_animation import VertexAnimation
from xanlib.key_animation import KeyAnimation
from xanlib.node import Node
from xanlib.scene import Scene


def write_vertex_animation(stream: BinaryIO, va: VertexAnimation) -> None:
    header_fmt = Struct(f"<3i{len(va.keys)}I")
    stream.write(header_fmt.pack(va.frame_count, va.count, va.actual, *va.keys))

    if va.count < 0:
        compressed_header_fmt = Struct("<2I")
        stream.write(compressed_header_fmt.pack(va.scale, va.base_count))
        for frame in va.frames:
            for vertex in frame:
                stream.write(CompressedVertex.fmt.pack(*vars(vertex).values()))
        if va.interpolation_data:
            stream.write(pack(f"{len(va.interpolation_data)}I", *va.interpolation_data))


def write_key_animation(stream: BinaryIO, ka: KeyAnimation) -> None:
    header_fmt = Struct("<2i")
    stream.write(header_fmt.pack(ka.frame_count, ka.flags))
    if ka.flags == -1:
        for matrix in ka.matrices:
            stream.write(pack("<16f", *matrix))
    elif ka.flags == -2:
        for matrix in ka.matrices:
            stream.write(pack("<12f", *matrix))
    elif ka.flags == -3:
        extra_fmt = Struct(f"i{len(ka.extra_data)}h")
        stream.write(extra_fmt.pack(len(ka.matrices), *ka.extra_data))
        for matrix in ka.matrices:
            stream.write(pack("<12f", *matrix))
    else:
        for frame in ka.frames:
            pos_fmt = Struct("<2h")
            stream.write(pos_fmt.pack(frame.frame_id, frame.flag))
            if frame.rotation is not None:
                stream.write(
                    pack(
                        "<4f",
                        frame.rotation.w,
                        frame.rotation.v.x,
                        frame.rotation.v.y,
                        frame.rotation.v.z,
                    )
                )
            if frame.scale is not None:
                stream.write(pack("<3f", *frame.scale))
            if frame.translation is not None:
                stream.write(pack("<3f", *frame.translation))


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

    stream.write(b"".join(bytes(vertex) for vertex in node.vertices))
    stream.write(b"".join(bytes(face) for face in node.faces))

    if node.rgb is not None:
        rgb_fmt = Struct(f"<{3*len(node.rgb)}B")
        stream.write(rgb_fmt.pack(*(c for rgb in node.rgb for c in rgb)))

    if node.faceData is not None:
        stream.write(pack(f"<{len(node.faceData)}i", *node.faceData))

    if node.vertex_animation is not None:
        write_vertex_animation(stream, node.vertex_animation)

    if node.key_animation is not None:
        write_key_animation(stream, node.key_animation)


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
