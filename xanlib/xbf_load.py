import struct
from .scene import Scene, Node, Face, Vertex

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
        struct.unpack("<1i", buffer.read(4 * 1)),
        struct.unpack("<1i", buffer.read(4 * 1)),
        tuple(
            struct.unpack("<2f", buffer.read(4 * 2))
            for i in range(3)
        )
    )
        
def read_node(file):
    vertexCount = readInt(file)
    if vertexCount == -1:
        return None
    node = Node()
    node.flags = readInt(file)
    faceCount = readInt(file)
    childCount = readInt(file)
    node.transform = readMatrix(file)
    nameLength = readInt(file)
    node.name = file.read(nameLength).decode()
    
    node.children = [read_node(file)   for i in range(childCount)]
    node.vertices = [read_vertex(file) for i in range(vertexCount)]
    node.faces    = [read_face(file)   for i in range(faceCount)]
        
    hasPrelight = bool(node.flags & 1)
    hasFaceData = bool(node.flags & 2)
    hasVertexAnimation = bool(node.flags & 4)
    hasKeyAnimation = bool(node.flags & 8)

    if hasPrelight:
        rgb = [readInt(file) for i in range(vertexCount)]

    if hasFaceData:
        faceData = [readInt(file) for i in range(faceCount)]

    if hasVertexAnimation:
        frameCount = readInt(file)
        count = readInt(file)
        actual = readInt(file)
        keyList = [readUInt(file) for i in range(actual)]
        if count < 0: #compressed
            scale = readUInt(file)
            node.vertexAnimationCount = int(readUInt(file)/actual)
            node.vertexAnimation = [[[readInt16(file), readInt16(file), readInt16(file), readUInt8(file), readUInt8(file)] for i in range(node.vertexAnimationCount)] for i in range(actual)]
            if (scale & 0x80000000): #interpolated
                interpolationData = [readUInt(file) for i in range(frameCount)]

    if hasKeyAnimation:
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
