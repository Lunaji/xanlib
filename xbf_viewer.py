#!/usr/bin/env python3
import numpy as np
import math
import pygame
from pygame.locals import QUIT
from xanlib import load_xbf

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
        vpos = [transform_vertex(get_vertex_pos(
                                        node,
                                        frame,
                                        vi,
                                        transform
                                     )
                                )
                for vi in face.vertex_indices]
        
        for i, j in ((0, 1), (0, 2), (2, 1)):
             pygame.draw.line(WINDOW, (0, 0, 255), vpos[i], vpos[j])
    
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
