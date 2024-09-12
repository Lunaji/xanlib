#!/usr/bin/env python3
import numpy as np
import math
import pygame
from pygame.locals import QUIT
from xanlib import load_xbf

def get_vertex_pos(node, frame, vi, transform):    
    posx = node.vertex_animation.body[frame][vi][0]
    posy = node.vertex_animation.body[frame][vi][1]
    posz = node.vertex_animation.body[frame][vi][2]
    np_point = np.array([posx, posy, posz, 1])
    np_result = np_point.dot(transform)
    #testnorm = node.vertex_animation.body[frame][vi][3]
    return np_result
    
class Viewer():   
    
    def __init__(self, width, height):
        if not pygame.get_init():
            pygame.init()            
        self.WINDOW = pygame.display.set_mode((width, height))
        self.looping=True
        self.curframe=0
        self.time = 0
        self.scale = 0.02
        self.rotspeed = 0.001
        marginy = 100
        self.offsetx = width/2.0
        self.offsety = height/2.0+marginy
        
    def transform_vertex(self, p):
        #time = math.pi * 0.5 / rotspeed
        ca=math.cos(self.time * self.rotspeed)
        sa=math.sin(self.time * self.rotspeed)
        rotp = ca * p[0] + sa * p[2]
        return (
            rotp * self.scale + self.offsetx,
            -p[1] * self.scale + self.offsety
            )
        
    def display_frame(self, node, frame, transform):
    
        if node.vertex_animation is None:
            return
        frames = len(node.vertex_animation.body)
        frame = frame%frames
        vertcount = node.vertex_animation.real_count
        
        #time = math.pi * 0.5
        for vi in range(vertcount):

            worldpos = get_vertex_pos(node, frame, vi, transform)
            curpos = self.transform_vertex(worldpos)
            normx = node.vertex_animation.body[frame][vi][3]
            normy = node.vertex_animation.body[frame][vi][4]

            #curpos=(nor1 * 2 + 1280/2.0, nor2 * 2 + 720/10.0)
            #curpos=(vi*10 + 1280/2.0, testnorm * 2 + 720/10.0)
            #if vi>0:
            #    pygame.draw.line(WINDOW, (0,0,255), curpos, prevpos, 2)
            size = 5
            pygame.draw.circle(self.WINDOW, (255,(vi*50)%255,(vi*10)%255), curpos, size)

            normscale = 30
            globalnormpos = (worldpos[0], worldpos[1] + normx*normscale, worldpos[2] + (normy-100.0) * normscale)
            normpos = self.transform_vertex(globalnormpos)
            pygame.draw.line(self.WINDOW, (255,0,0), curpos, normpos)

            prevpos=curpos
        
        for face in node.faces:
            vpos = [self.transform_vertex(get_vertex_pos(
                                            node,
                                            frame,
                                            vi,
                                            transform
                                        )
                                    )
                    for vi in face.vertex_indices]
            
            for i, j in ((0, 1), (0, 2), (2, 1)):
                pygame.draw.line(self.WINDOW, (0, 0, 255), vpos[i], vpos[j])
                
    def recursive_display(self, node, frame, transform=None):
    
        np_transform = np.array(node.transform)
        np_transform.shape=(4,4)

        if transform is not None:
            np_transform = np_transform.dot(transform)

        self.display_frame(node, frame, np_transform)
        for child in node.children:
            self.recursive_display(child, frame, np_transform)
        
    def view(self, scene):
        while self.looping:
            for event in pygame.event.get() :
                if event.type == QUIT:
                    return
            
            self.WINDOW.fill((30, 30, 30))
            
            self.time = pygame.time.get_ticks()
            
            self.curframe = math.floor(self.time*0.01)
            
            for node in scene.nodes:
                self.recursive_display(node, self.curframe)

            pygame.display.update()

if __name__ == '__main__':
    
    filename = 'Data/3DData1/Buildings/AT_conyard_H0.XbF'    
    scene = load_xbf(filename)
    viewer = Viewer(1280, 720)    
    viewer.view(scene)
