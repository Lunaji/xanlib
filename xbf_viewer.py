#!/usr/bin/env python3
import struct
import numpy as np
import math
import pygame
from pygame.locals import QUIT

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

class Vertex:
    def __init__(self):
        self.vertices = None

    def readFrom(self, file):
        self.vertices = struct.unpack("<6f", file.read(4 * 6))

class Face:
    def __init__(self):
        self.longs = []
        self.floats = []

    def readFrom(self, file):
        self.longs = struct.unpack("<5i", file.read(4 * 5))
        self.floats = struct.unpack("<6f", file.read(4 * 6))

class Node:
    def __init__(self):
        self.children = []
        self.vertices = []
        self.faces = []
        self.vertexAnimation=None
        self.vertexAnimationCount=None

def read_node(file):
    vertexCount = readInt(file)
    if vertexCount == -1:
        return None
    node = Node()
    flags = readInt(file)
    faceCount = readInt(file)
    childCount = readInt(file)
    node.transform = readMatrix(file)
    nameLength = readInt(file)
    node.name = file.read(nameLength)
    
    for i in range(childCount):
        child = read_node(file)
        node.children.append(child)

    for i in range(vertexCount):
        vertex = Vertex()
        vertex.readFrom(file)
        node.vertices.append(vertex)

    for i in range(faceCount):
        face = Face()
        face.readFrom(file)
        node.faces.append(face)
        
    hasPrelight = bool(flags & 1)
    hasFaceData = bool(flags & 2)
    hasVertexAnimation = bool(flags & 4)
    hasKeyAnimation = bool(flags & 8)

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

class Scene:
    def __init__(self):
        self.nodes = []

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
                print('Error while parsing node:')
                print(e)
                scene.unparsed = f.read()
                return scene

def recursive_display(node, frame, transform=None):
    
    np_transform = np.array(node.transform)
    np_transform.shape=(4,4)

    if transform is not None:
        np_transform = np_transform.dot(transform)

    display_frame(node, frame, np_transform)
    for child in node.children:
        recursive_display(child, frame, np_transform)

offsetx = 1280/2.0
offsety = 720/2.0+100
scale = 0.02
time = 0
rotspeed = 0.001

def transform_vertex(p):
    #time = math.pi * 0.5 / rotspeed
    ca=math.cos(time * rotspeed)
    sa=math.sin(time * rotspeed)
    rotp = ca * p[0] + sa * p[2]
    return (rotp * scale + offsetx, -p[1] * scale + offsety)

def get_vertex_pos(node, frame, ver, transform):    
    posx = node.vertexAnimation[frame][ver][0]
    posy = node.vertexAnimation[frame][ver][1]
    posz = node.vertexAnimation[frame][ver][2]
    np_point = np.array([posx, posy, posz, 1])
    np_result = np_point.dot(transform)
    #testnorm = node.vertexAnimation[frame][ver][3]
    return np_result

def display_frame(node, frame, transform):
    
    if node.vertexAnimation is None:
        return
    frames = len(node.vertexAnimation)
    frame = frame%frames
    vertcount = node.vertexAnimationCount

    #time = math.pi * 0.5
    for ver in range(vertcount):

        worldpos = get_vertex_pos(node, frame, ver, transform)
        curpos = transform_vertex(worldpos)
        normx = node.vertexAnimation[frame][ver][3]
        normy = node.vertexAnimation[frame][ver][4]

        #curpos=(nor1 * 2 + 1280/2.0, nor2 * 2 + 720/10.0)
        #curpos=(ver*10 + 1280/2.0, testnorm * 2 + 720/10.0)
        #if ver>0:
        #    pygame.draw.line(WINDOW, (0,0,255), curpos, prevpos, 2)
        size = 5
        pygame.draw.circle(WINDOW, (255,(ver*50)%255,(ver*10)%255), curpos, size)

        normscale = 30
        globalnormpos = (worldpos[0], worldpos[1] + normx*normscale, worldpos[2] + (normy-100.0) * normscale)
        normpos = transform_vertex(globalnormpos)
        pygame.draw.line(WINDOW, (255,0,0), curpos, normpos)

        prevpos=curpos
    
    for face in node.faces:
        v0 = face.longs[0]
        v1 = face.longs[1]
        v2 = face.longs[2]
        v0pos = transform_vertex(get_vertex_pos(node, frame, v0, transform))
        v1pos = transform_vertex(get_vertex_pos(node, frame, v1, transform))
        v2pos = transform_vertex(get_vertex_pos(node, frame, v2, transform))
        pygame.draw.line(WINDOW, (0,0,255), v0pos, v1pos)
        pygame.draw.line(WINDOW, (0,0,255), v0pos, v2pos)
        pygame.draw.line(WINDOW, (0,0,255), v2pos, v1pos)
    
def viewer(node):
    pygame.init()
    global WINDOW
    WINDOW = pygame.display.set_mode((1280, 720))
    looping=True
    curframe=0
    while looping:
        for event in pygame.event.get() :
            if event.type == QUIT :
                pygame.quit()
                return
            
        WINDOW.fill((30, 30, 30))
        
        global time
        time = pygame.time.get_ticks()
        
        curframe = math.floor(time*0.01)
        recursive_display(node, curframe)

        pygame.display.update()

if __name__ == '__main__':
    
    filename = 'Data/3DData1/Buildings/AT_conyard_H0.XbF'
    
    scene = load_xbf(filename)
    
    viewer(scene.nodes[0]) #assuming it exists and treating it as root
