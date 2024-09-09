#!/usr/bin/env python3
import struct
import numpy as np
import argparse
import os
import sys
import math
import pygame
from pygame.locals import *

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
        self.vertices = struct.unpack("<6f", xbfFile.read(4 * 6))

class Face:
    def __init__(self):
        self.longs = []
        self.floats = []

    def readFrom(self, file):
        self.longs = struct.unpack("<5i", xbfFile.read(4 * 5))
        self.floats = struct.unpack("<6f", xbfFile.read(4 * 6))

VertexTotal = 0 #for writing out to obj

class Object:
    def __init__(self):
        self.children = []
        self.vertices = []
        self.faces = []

    def readFrom(self, file):
        vertexCount = readInt(file)
        flags = readInt(file)
        hasPrelight = bool(flags & 1)
        hasFaceData = bool(flags & 2)
        hasVertexAnimation = bool(flags & 4)
        hasKeyAnimation = bool(flags & 8)
        faceCount = readInt(file)
        childCount = readInt(file)
        self.transform = readMatrix(file)
        nameLength = readInt(file)
        self.name = file.read(nameLength)

        for i in range(childCount):
            child = Object()
            child.readFrom(file)
            self.children.append(child)

        for i in range(vertexCount):
            vertex = Vertex()
            vertex.readFrom(file)
            self.vertices.append(vertex)

        for i in range(faceCount):
            face = Face()
            face.readFrom(file)
            self.faces.append(face)

        if hasPrelight:
            rgb = [readInt(file) for i in range(vertexCount)]

        if hasFaceData:
            faceData = [readInt(file) for i in range(faceCount)]

        self.vertexAnimation=None
        self.vertexAnimationCount=None
        if hasVertexAnimation:
            frameCount = readInt(file)
            count = readInt(file)
            actual = readInt(file)
            keyList = [readUInt(file) for i in range(actual)]
            if count < 0: #compressed
                scale = readUInt(file)
                self.vertexAnimationCount = int(readUInt(file)/actual)
                self.vertexAnimation = [[[readInt16(file), readInt16(file), readInt16(file), readUInt8(file), readUInt8(file)] for i in range(self.vertexAnimationCount)] for i in range(actual)]
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

    def writeToObj(self, file, transform=None, resetTotal=True):
        global VertexTotal
        if resetTotal:
            VertexTotal = 0

        np_transform = np.array(self.transform)
        np_transform.shape=(4,4)

        if transform is not None:
            np_transform = np_transform.dot(transform)

        name = self.name.decode()
        file.write("o "+name+"\n")

        for vertex in self.vertices:
            np_point = np.array([vertex.vertices[0], vertex.vertices[1], vertex.vertices[2], 1])
            np_result = np_point.dot(np_transform)
            file.write("v "+str(np_result[0])+" "+str(np_result[1])+" "+str(np_result[2])+" "+str(np_result[3])+"\n")
        file.write("\n")
        for face in self.faces:
            file.write("f "+str(face.longs[0]+1+VertexTotal)+" "+str(face.longs[1]+1+VertexTotal)+" "+str(face.longs[2]+1+VertexTotal)+"\n")
        file.write("\n")
        VertexTotal += len(self.vertices)

        for child in self.children:
            child.writeToObj(file, np_transform, False)

def recursive_display(obj, frame, transform=None):
    
    np_transform = np.array(obj.transform)
    np_transform.shape=(4,4)

    if transform is not None:
        np_transform = np_transform.dot(transform)

    display_frame(obj, frame, np_transform)
    for child in obj.children:
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

def get_vertex_pos(obj, frame, ver, transform):    
    posx = obj.vertexAnimation[frame][ver][0]
    posy = obj.vertexAnimation[frame][ver][1]
    posz = obj.vertexAnimation[frame][ver][2]
    np_point = np.array([posx, posy, posz, 1])
    np_result = np_point.dot(transform)
    #testnorm = obj.vertexAnimation[frame][ver][3]
    return np_result

def display_frame(obj, frame, transform):
    
    if obj.vertexAnimation == None:
        return
    frames = len(obj.vertexAnimation)
    frame = frame%frames
    vertcount = obj.vertexAnimationCount

    #time = math.pi * 0.5
    for ver in range(vertcount):

        worldpos = get_vertex_pos(obj, frame, ver, transform)
        curpos = transform_vertex(worldpos)
        normx = obj.vertexAnimation[frame][ver][3]
        normy = obj.vertexAnimation[frame][ver][4]

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
    
    for face in obj.faces:
        v0 = face.longs[0]
        v1 = face.longs[1]
        v2 = face.longs[2]
        v0pos = transform_vertex(get_vertex_pos(obj, frame, v0, transform))
        v1pos = transform_vertex(get_vertex_pos(obj, frame, v1, transform))
        v2pos = transform_vertex(get_vertex_pos(obj, frame, v2, transform))
        pygame.draw.line(WINDOW, (0,0,255), v0pos, v1pos)
        pygame.draw.line(WINDOW, (0,0,255), v0pos, v2pos)
        pygame.draw.line(WINDOW, (0,0,255), v2pos, v1pos)
        #file.write("f "+str()+" "+str(face.longs[1]+1+VertexTotal)+" "+str(face.longs[2]+1+VertexTotal)+"\n")
    
def viewer(obj):
    pygame.init()
    global WINDOW
    WINDOW = pygame.display.set_mode((1280, 720))
    looping=True
    curframe=0
    while looping:
        for event in pygame.event.get() :
            if event.type == QUIT :
                pygame.quit()
                sys.exit()
            
        # Processing
        # This section will be built out later
    
        # Render elements of the game
        WINDOW.fill((30, 30, 30))
        
        global time
        time = pygame.time.get_ticks()
        
        curframe = math.floor(time*0.01)
        recursive_display(obj, curframe)

        pygame.display.update()

if __name__ == '__main__':
    # parser = argparse.ArgumentParser()
    # parser.add_argument("file")
    # args = parser.parse_args()

    wd=os.path.dirname(os.path.realpath(__file__))
    #filename = "GU_wormhead_H0_base.xbf"
    #filename = "AT_MGT_H0_base.xbf"
    filename = "AT_conyard_H0_base.xbf"
    file = os.path.join(wd,filename)

    with open(file, "rb") as xbfFile:
        version = readInt(xbfFile)
        appDataSize = readInt(xbfFile)
        xbfFile.read(appDataSize)
        textureNameDataSize = readInt(xbfFile)
        xbfFile.read(textureNameDataSize)

        xbfObject = Object()
        xbfObject.readFrom(xbfFile)

        viewer(xbfObject)

        # xbfname = os.path.splitext(file)[0]
        # with open(xbfname+".obj", "w") as f:
        #     xbfObject.writeToObj(f)

