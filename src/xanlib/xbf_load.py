from typing import BinaryIO
from struct import unpack, calcsize, iter_unpack
from xanlib.vertex_animation import CompressedVertex
from xanlib.math_utils import Vector3, UV
from xanlib.vertex import Vertex
from xanlib.face import Face
from xanlib.vertex_animation import VertexAnimation
from xanlib.key_animation import KeyAnimation, KeyAnimationFrame
from xanlib.node import Node, NodeFlags
from xanlib.scene import Scene


def read_vertex(stream: BinaryIO) -> Vertex:
    return Vertex(
        Vector3(*unpack("<3f", stream.read(4 * 3))),
        Vector3(*unpack("<3f", stream.read(4 * 3)))
    )

def read_face(stream: BinaryIO) -> Face:
    return Face(
        unpack("<3i", stream.read(4 * 3)),
        unpack("<1i", stream.read(4 * 1))[0],
        unpack("<1i", stream.read(4 * 1))[0],
        (
            UV(*unpack("<2f", stream.read(4 * 2))),
            UV(*unpack("<2f", stream.read(4 * 2))),
            UV(*unpack("<2f", stream.read(4 * 2)))
        )
    )
        
def read_vertex_animation(stream: BinaryIO) -> VertexAnimation:
    header_fmt = '<3i'
    header_size = calcsize(header_fmt)
    frame_count, count, actual = unpack(header_fmt, stream.read(header_size))
    keys_fmt = f'<{actual}I'
    keys_size = calcsize(keys_fmt)
    keys = list(unpack(keys_fmt, stream.read(keys_size)))
    if count < 0: #compressed
        compressed_header_fmt = '<2I'
        compressed_header_size = calcsize(compressed_header_fmt)
        scale, base_count = unpack(compressed_header_fmt, stream.read(compressed_header_size))
        assert count == -base_count
        real_count = base_count//actual
        frames = [
            [CompressedVertex(*fields) for fields in CompressedVertex.fmt.iter_unpack(
                stream.read(CompressedVertex.fmt.size*real_count
                ))]
            for i in range(actual)]
        if scale & 0x80000000: #interpolated
            interpolation_fmt = f'<{frame_count}I'
            interpolation_size = calcsize(interpolation_fmt)
            interpolation_data = list(unpack(interpolation_fmt, stream.read(interpolation_size)))
            
    return VertexAnimation(
        frame_count,
        count,
        actual,
        keys,
        scale if count<0 else None,
        base_count if count<0 else None,
        real_count if count<0 else None,
        frames if count<0 else None,
        interpolation_data if ((count<0) and (scale & 0x80000000)) else None
    )

def read_key_animation(stream):
    header_fmt = '<2i'
    header_size = calcsize(header_fmt)
    frame_count, flags = unpack(header_fmt, stream.read(header_size))
    if flags==-1:
        matrices = [
            unpack('<16f', stream.read(4*16))
            for i in range(frame_count+1)
        ]
    elif flags==-2:
        matrices = [
            unpack('<12f', stream.read(4*12))
            for i in range(frame_count+1)
        ]
    elif flags==-3:
        extra_fmt = f'i{frame_count + 1}h'
        extra_size = calcsize(extra_fmt)
        actual, *extra_data = unpack(extra_fmt, stream.read(extra_size))
        matrices = [
            unpack('<12f', stream.read(4 * 12))
            for i in range(actual)
        ]
    else:
        frames = []
        for i in range(flags):
            pos_fmt = '<2h'
            pos_size = calcsize(pos_fmt)
            frame_id, flag = unpack(pos_fmt, stream.read(pos_size))
            assert not (flag & 0b1000111111111111)

            if (flag >> 12) & 0b001:
                rotation = unpack('<4f', stream.read(4*4))
            else:
                rotation = None
            if (flag >> 12) & 0b010:
                scale = unpack('<3f', stream.read(4*3))
            else:
                scale = None
            if (flag >> 12) & 0b100:
                translation = unpack('<3f', stream.read(4*3))
            else:
                translation = None

            frames.append(KeyAnimationFrame(
                            frame_id,
                            flag,
                            rotation,
                            scale,
                            translation
                        ))
        
    return KeyAnimation(
        frame_count,
        flags,
        matrices if flags in (-1,-2,-3) else None,
        actual if flags==-3 else None,
        extra_data if flags==-3 else None,
        frames if flags not in (-1,-2,-3) else None
    )        
        
def read_node(stream, parent=None):
    stream_position = stream.tell()
    try:
        vertex_count = unpack('<i', stream.read(4))[0]
        if vertex_count == -1:
            return None
        node = Node()
        node.parent = parent
        header_fmt = '<3i16dI'
        header_size = calcsize(header_fmt)
        flags, face_count, child_count, *tranform, name_length = unpack(header_fmt, stream.read(header_size))
        node.flags = NodeFlags(flags)
        node.transform = tuple(tranform)
        node.name = stream.read(name_length).decode('ascii')
        
        node.children = [read_node(stream, node)   for i in range(child_count)]
        node.vertices = [read_vertex(stream) for i in range(vertex_count)]
        node.faces    = [read_face(stream)   for i in range(face_count)]

        if NodeFlags.PRELIGHT in node.flags:
            rgb_fmt = '<3B'
            rgb_size = calcsize(rgb_fmt)
            node.rgb = [rgb_tuple for rgb_tuple in iter_unpack(rgb_fmt, stream.read(rgb_size*vertex_count))]

        if NodeFlags.FACE_DATA in node.flags:
            faceData_fmt = f'<{face_count}i'
            faceData_size = calcsize(faceData_fmt)
            node.faceData = list(unpack(faceData_fmt, stream.read(faceData_size)))

        if NodeFlags.VERTEX_ANIMATION in node.flags:
            node.vertex_animation = read_vertex_animation(stream)

        if NodeFlags.KEY_ANIMATION in node.flags:
            node.key_animation = read_key_animation(stream)
            
        return node
    except Exception:
        stream.seek(stream_position)
        raise

def load_xbf(filename):
    scene = Scene()
    scene.file = filename  
    with open(filename, 'rb') as f:
        header_fmt = '<2i'
        header_size = calcsize(header_fmt)
        scene.version, fxdata_size = unpack(header_fmt, f.read(header_size))
        scene.FXData = f.read(fxdata_size)
        texture_data_size = unpack('<i', f.read(4))[0]
        scene.textureNameData = f.read(texture_data_size)
        while True:
            try:
                node = read_node(f)
                if node is None:
                    current_position = f.tell()
                    f.seek(0, 2)
                    assert current_position == f.tell(), 'Not at EOF'
                    return scene
                scene.nodes.append(node)
            except Exception as e:
                scene.error = e
                scene.unparsed = f.read()
                return scene
