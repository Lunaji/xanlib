#!/usr/bin/env python3
import numpy as np
import pygame
from pygame.locals import QUIT
from pygame.math import Vector2, Vector3
from xanlib import load_xbf

def get_vertex_pos(vertex, transform):
    
    transformed = np.array((*vertex[:3], 1)).dot(transform)
    return Vector3(*transformed[:3])/transformed[3]
    
class Viewer():   
    
    def __init__(self, width, height):
        
        if not pygame.get_init():
            pygame.init()            
        self.WINDOW = pygame.display.set_mode((width, height))
        self.curframe=0
        self.time = 0
        self.scale = 0.02
        self.rotspeed = 0.001
        self.origin = Vector2(width/2.0, height/2.0)
        self.offset = Vector2(0, 100)
        
        
    def transform_vertex(self, p):
        
        a = self.time * self.rotspeed
        rotp = np.dot([np.cos(a), np.sin(a)], [p.x, p.z])
        return Vector2(rotp, -p.y)*self.scale+self.origin+self.offset
    
        
    def display_frame(self, faces, va_frame, transform):
        
        transformed_vertices = []
        
        for vi, vertex in enumerate(va_frame):

            worldpos = get_vertex_pos(vertex, transform)
            curpos = self.transform_vertex(worldpos)
            transformed_vertices.append(curpos)

            size = 5
            pygame.draw.circle(self.WINDOW, (255,(vi*50)%255,(vi*10)%255), curpos, size)

            normscale = 30
            norm = Vector2(*vertex[3:5])
            globalnormpos = worldpos+Vector3(0, *(norm-self.offset)*normscale)
            normpos = self.transform_vertex(globalnormpos)
            pygame.draw.line(self.WINDOW, (255,0,0), curpos, normpos)
            
        
        for face in faces:
            vpos = [transformed_vertices[vi] for vi in face.vertex_indices]
            
            pygame.draw.lines(self.WINDOW, (0, 0, 255), True, vpos)
                
                
    def recursive_display(self, node, frame, parent_transform=None):
    
        node_transform = np.array(node.transform).reshape(4,4)

        if parent_transform is not None:
            node_transform = node_transform.dot(parent_transform)
            
        if node.vertex_animation is not None:
            frames = len(node.vertex_animation.body)
            frame = frame%frames
            self.display_frame(node.faces, node.vertex_animation.body[frame], node_transform)
            
        for child in node.children:
            self.recursive_display(child, frame, node_transform)
            
        
    def view(self, scene):
        
        while True:
            for event in pygame.event.get() :
                if event.type == QUIT:
                    return
            
            self.WINDOW.fill((30, 30, 30))
            
            self.time = pygame.time.get_ticks()
            
            self.curframe = int(np.floor(self.time*0.01))
            
            for node in scene.nodes:
                self.recursive_display(node, self.curframe)

            pygame.display.update()
            

if __name__ == '__main__':
    
    filename = 'Data/3DData1/Buildings/AT_MGT_H0.xbf'    
    scene = load_xbf(filename)
    viewer = Viewer(1280, 720)    
    viewer.view(scene)
