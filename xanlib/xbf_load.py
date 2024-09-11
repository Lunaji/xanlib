import struct
from .scene import Scene, Node, VertexAnimation, Face, Vertex
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
        body = [[[readInt16(buffer), readInt16(buffer), readInt16(buffer), readUInt8(buffer), readUInt8(buffer)] for i in range(real_count)] for i in range(actual)]
        if (scale & 0x80000000): #interpolated
            interpolationData = [readUInt(buffer) for i in range(frameCount)]
            
    return VertexAnimation(
        frameCount,
        count,
        actual,
        keyList,
        scale,
        base_count,
        real_count,
        body,
        interpolationData if (scale & 0x80000000) else None
    )
        
        
def read_node(file):
    vertexCount = readInt(file)
    if vertexCount == -1:
        return None
    node = Node()
    node.flags = NodeFlags(readInt(file))
    faceCount = readInt(file)
    childCount = readInt(file)
    node.transform = readMatrix(file)
    nameLength = readInt(file)
    node.name = file.read(nameLength).decode()
    
    node.children = [read_node(file)   for i in range(childCount)]
    node.vertices = [read_vertex(file) for i in range(vertexCount)]
    node.faces    = [read_face(file)   for i in range(faceCount)]

    if NodeFlags.PRELIGHT in node.flags:
        node.rgb = [(readByte(file) for i in range(3)) for j in range(vertexCount)]

    if NodeFlags.FACE_DATA in node.flags:
        node.faceData = [readInt(file) for i in range(faceCount)]

    if NodeFlags.VERTEX_ANIMATION in node.flags:
        node.vertex_animation = read_vertex_animation(file)


    if NodeFlags.KEY_ANIMATION in node.flags:
        frameCount = readInt(file)
        keynimationflags = readInt(file)
        if keynimationflags==-1:
            for i in range(frameCount+1):
                for j in range(16): readInt(file)
        elif keynimationflags==-2:
            for i in range(frameCount+1):
                for j in range(12): readInt(file)
        else:
            actual = readInt(file)
            for i in range(frameCount+1):
                readInt16(file)
            for i in range(actual):
                struct.unpack("<12f", file.read(4 * 12))
                
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
