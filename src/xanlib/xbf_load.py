from struct import unpack, calcsize
from .scene import Scene, Node, CompressedVertex, VertexAnimation, KeyAnimationFrame, KeyAnimation, Face, Vertex, Vector3
from .xbf_base import NodeFlags


def readInt(file):
        return unpack("<i", file.read(4))[0]

def readUInt(file):
        return unpack("<I", file.read(4))[0]

def readInt16(file):
    return unpack("<h", file.read(2))[0]

def readInt8(file):
    return unpack("<b", file.read(1))[0]

def readUInt8(file):
    return unpack("<B", file.read(1))[0]

def readUInt16(file):
    return unpack("<H", file.read(2))[0]

def readMatrix(file):
        return unpack("<16d", file.read(8*16))

def readByte(file):
    return unpack("<c", file.read(1))[0]

def read_vertex(stream):
    return Vertex(
        unpack("<3f", stream.read(4 * 3)),
        unpack("<3f", stream.read(4 * 3))
    )

def read_compressed_vertex(stream):
    format_string = '<3hH'
    byte_count_to_read = calcsize(format_string)
    bytes_read = stream.read(byte_count_to_read)
    unpacked = unpack(format_string, bytes_read)
    return CompressedVertex(*unpacked)

def read_face(stream):
    return Face(
        unpack("<3i", stream.read(4 * 3)),
        unpack("<1i", stream.read(4 * 1))[0],
        unpack("<1i", stream.read(4 * 1))[0],
        tuple(
            unpack("<2f", stream.read(4 * 2))
            for i in range(3)
        )
    )
        
def read_vertex_animation(stream):
    frameCount = readInt(stream)
    count = readInt(stream)
    actual = readInt(stream)
    keyList = [readUInt(stream) for i in range(actual)]
    if count < 0: #compressed
        scale = readUInt(stream)
        base_count = readUInt(stream)
        assert count == -base_count
        real_count = base_count//actual
        frames = [[read_compressed_vertex(stream) for j in range(real_count)] for i in range(actual)]
        if (scale & 0x80000000): #interpolated
            interpolationData = [readUInt(stream) for i in range(frameCount)]
            
    return VertexAnimation(
        frameCount,
        count,
        actual,
        keyList,
        scale if count<0 else None,
        base_count if count<0 else None,
        real_count if count<0 else None,
        frames if count<0 else None,
        interpolationData if ((count<0) and (scale & 0x80000000)) else None
    )

def read_key_animation(stream):
    frameCount = readInt(stream)
    flags = readInt(stream)
    if flags==-1:
        matrices = [
            unpack('<16f', stream.read(4*16))
            for i in range(frameCount+1)
        ]
    elif flags==-2:
        matrices = [
            unpack('<12f', stream.read(4*12))
            for i in range(frameCount+1)
        ]
    elif flags==-3:
        actual = readInt(stream)
        extra_data = [readInt16(stream) for i in range(frameCount+1)]
        matrices = [
            unpack('<12f', stream.read(4 * 12))
            for i in range(actual)
        ]
    else:
        frames = []
        for i in range(flags):
            frame_id = readInt16(stream)
            flag = readInt16(stream)
            assert not (flag & 0b1000111111111111)

            if ((flag >> 12) & 0b001):
                rotation = unpack('<4f', stream.read(4*4))
            else:
                rotation = None
            if ((flag >> 12) & 0b010):
                scale = unpack('<3f', stream.read(4*3))
            else:
                scale = None
            if ((flag >> 12) & 0b100):
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
        frameCount,
        flags,
        matrices if flags in (-1,-2,-3) else None,
        actual if flags==-3 else None,
        extra_data if flags==-3 else None,
        frames if flags not in (-1,-2,-3) else None
    )        
        
def read_node(stream, parent=None):
    stream_position = stream.tell()
    try:
        vertexCount = readInt(stream)
        if vertexCount == -1:
            return None
        node = Node()
        node.parent = parent
        node.flags = NodeFlags(readInt(stream))
        faceCount = readInt(stream)
        childCount = readInt(stream)
        node.transform = readMatrix(stream)
        nameLength = readInt(stream)
        node.name = stream.read(nameLength).decode()
        
        node.children = [read_node(stream, node)   for i in range(childCount)]
        node.vertices = [read_vertex(stream) for i in range(vertexCount)]
        node.faces    = [read_face(stream)   for i in range(faceCount)]

        if NodeFlags.PRELIGHT in node.flags:
            node.rgb = [tuple(readUInt8(stream) for i in range(3)) for j in range(vertexCount)]

        if NodeFlags.FACE_DATA in node.flags:
            node.faceData = [readInt(stream) for i in range(faceCount)]

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
        scene.version = readInt(f)
        FXDataSize = readInt(f)
        scene.FXData = f.read(FXDataSize)
        textureNameDataSize = readInt(f)
        scene.textureNameData = f.read(textureNameDataSize)
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
