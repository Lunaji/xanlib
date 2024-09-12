import struct
from .scene import Scene, Node, VertexAnimation, KeyAnimation, Face, Vertex
from .xbf_base import NodeFlags

def readInt(file):
	return struct.unpack("<i", file.read(4))[0]

def readUInt(file):
	return struct.unpack("<I", file.read(4))[0]

def readInt16(file):
    return struct.unpack("<h", file.read(2))[0]

def readInt8(file):
    return struct.unpack("<b", file.read(1))[0]

def readUInt8(file):
    return struct.unpack("<B", file.read(1))[0]

def readUInt16(file):
    return struct.unpack("<H", file.read(2))[0]

def readMatrix(file):
	return struct.unpack("<16d", file.read(8*16))

def readByte(file):
    return struct.unpack("<c", file.read(1))[0]

def read_vertex(buffer):
    return Vertex(
        struct.unpack("<3f", buffer.read(4 * 3)),
        struct.unpack("<3f", buffer.read(4 * 3))
    )

def read_face(buffer):
    return Face(
        struct.unpack("<3i", buffer.read(4 * 3)),
        struct.unpack("<1i", buffer.read(4 * 1))[0],
        struct.unpack("<1i", buffer.read(4 * 1))[0],
        tuple(
            struct.unpack("<2f", buffer.read(4 * 2))
            for i in range(3)
        )
    )
        
def read_vertex_animation(buffer):
    frameCount = readInt(buffer)
    count = readInt(buffer)
    actual = readInt(buffer)
    keyList = [readUInt(buffer) for i in range(actual)]
    if count < 0: #compressed
        scale = readUInt(buffer)
        base_count = readUInt(buffer)
        real_count = base_count//actual
        body = [[[readInt16(buffer), readInt16(buffer), readInt16(buffer), readUInt8(buffer), readUInt8(buffer)] for j in range(real_count)] for i in range(actual)]
        if (scale & 0x80000000): #interpolated
            interpolationData = [readUInt(buffer) for i in range(frameCount)]
            
    return VertexAnimation(
        frameCount,
        count,
        actual,
        keyList,
        scale if count<0 else None,
        base_count if count<0 else None,
        real_count if count<0 else None,
        body if count<0 else None,
        interpolationData if ((count<0) and (scale & 0x80000000)) else None
    )

def read_key_animation(buffer):
    frameCount = readInt(buffer)
    flags = readInt(buffer)
    if flags==-1:
        matrices = [
            struct.unpack('<16f', buffer.read(4*16))
            for i in range(frameCount+1)
        ]
    elif flags==-2:
        matrices = [
            struct.unpack('<12f', buffer.read(4*12))
            for i in range(frameCount+1)
        ]
    else: #assuming -3 ?
        actual = readInt(buffer)
        extra_data = [readInt16(buffer) for i in range(frameCount+1)]
        matrices = [
            struct.unpack('<12f', buffer.read(4 * 12))
            for i in range(actual)
        ]
        
    return KeyAnimation(
        frameCount,
        flags,
        matrices,
        actual if flags==-3 else None,
        extra_data if flags==-3 else None
    )        
        
def read_node(buffer):
    vertexCount = readInt(buffer)
    if vertexCount == -1:
        return None
    node = Node()
    node.flags = NodeFlags(readInt(buffer))
    faceCount = readInt(buffer)
    childCount = readInt(buffer)
    node.transform = readMatrix(buffer)
    nameLength = readInt(buffer)
    node.name = buffer.read(nameLength).decode()
    
    node.children = [read_node(buffer)   for i in range(childCount)]
    node.vertices = [read_vertex(buffer) for i in range(vertexCount)]
    node.faces    = [read_face(buffer)   for i in range(faceCount)]

    if NodeFlags.PRELIGHT in node.flags:
        node.rgb = [tuple(readUInt8(buffer) for i in range(3)) for j in range(vertexCount)]

    if NodeFlags.FACE_DATA in node.flags:
        node.faceData = [readInt(buffer) for i in range(faceCount)]

    if NodeFlags.VERTEX_ANIMATION in node.flags:
        node.vertex_animation = read_vertex_animation(buffer)

    if NodeFlags.KEY_ANIMATION in node.flags:
        node.key_animation = read_key_animation(buffer)
        
    return node

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
                    #Verify eof?
                    return scene
                scene.nodes.append(node)
            except Exception as e:
                scene.error = e
                scene.unparsed = f.read()
                return scene
