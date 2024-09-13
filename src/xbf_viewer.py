#!/usr/bin/env python3
import numpy as np
import pygame
from pygame.locals import QUIT
from pygame.math import Vector2, Vector3
from xanlib import load_xbf


def convert_signed_5bit(v):
    sign=-1 if (v%32)>15 else 1
    return sign*(v%16)

def get_vertex_pos(vertex, transform):
    
    transformed = np.array((*vertex[:3], 1)).dot(transform)
    return Vector3(*transformed[:3])/transformed[3]

def get_vertex_norm(vertex, transform):
    
    transformed = np.array((*vertex[:3], 0)).dot(transform)
    return Vector3(*transformed[:3])

draw_index = 0

class Viewer():   
    
    def __init__(self, width, height):
        
        if not pygame.get_init():
            pygame.init()            
        self.WINDOW = pygame.display.set_mode((width, height))
        self.curframe=0
        self.time = 0
        self.bounds_min = None
        self.bounds_max = None
        self.scale = 0.02
        self.rotspeed = 0.001
        self.screen_half = Vector2(width/2.0, height/2.0)
        self.offset = Vector3(0, 0, 0)
        
        
    def transform_vertex(self, p):
        a = self.time * self.rotspeed
        rotp = np.dot([np.cos(a), np.sin(a)], [p.x - self.offset.x, p.z - self.offset.z])
        return Vector2(rotp, -p.y + self.offset.y)*self.scale+self.screen_half
    
    def display_frame(self, faces, va_frame, transform):
        
        transformed_vertices = []

        if self.bounds_min is not None and self.bounds_max is not None:
            self.offset = (self.bounds_max + self.bounds_min) * 0.5
            bound_size = self.bounds_max - self.bounds_min
            self.scale = self.screen_half.y * 1.75 / max(max(0.0001,abs(bound_size.x)), max(abs(bound_size.y), abs(bound_size.z)))
        
        origin = self.transform_vertex(Vector3(0,0,0))
        pygame.draw.circle(self.WINDOW, (0,255,0), origin, 5)

        for vi, vertex in enumerate(va_frame):

            worldpos = get_vertex_pos(vertex, transform)
            if self.bounds_min is None:
                self.bounds_min = Vector3(worldpos)
            if self.bounds_max is None:
                self.bounds_max = Vector3(worldpos)
            self.bounds_min.x = min(self.bounds_min.x, worldpos.x)
            self.bounds_min.y = min(self.bounds_min.y, worldpos.y)
            self.bounds_min.z = min(self.bounds_min.z, worldpos.z)
            self.bounds_max.x = max(self.bounds_max.x, worldpos.x)
            self.bounds_max.y = max(self.bounds_max.y, worldpos.y)
            self.bounds_max.z = max(self.bounds_max.z, worldpos.z)

            curpos = self.transform_vertex(worldpos)
            transformed_vertices.append(curpos)

            size = 5
            pygame.draw.circle(self.WINDOW, (255,(vi*50)%255,(vi*10)%255), curpos, size)

            normscale = 100
            normint = vertex[3]
            normx = convert_signed_5bit(normint & 0x1F)
            normy = convert_signed_5bit((normint>>5) & 0x1F)
            normz = convert_signed_5bit((normint>>10) & 0x1F)
            norm = get_vertex_norm((normx, normy, normz), transform)
            globalnormpos = worldpos+norm*normscale
            normpos = self.transform_vertex(globalnormpos)
            pygame.draw.line(self.WINDOW, (255,0,0), curpos, normpos)
            
        global draw_index
        for face in faces:
            
            vpos = [transformed_vertices[vi] for vi in face.vertex_indices]
            random_color = ((draw_index*50+200)%255, (draw_index*137+200)%255, (draw_index*77+200)%255)
            pygame.draw.lines(self.WINDOW, random_color, True, vpos)
        draw_index += 1
                
                
    def recursive_display(self, node, frame, parent_transform=None):
    
        node_transform = np.array(node.transform).reshape(4,4)

        if parent_transform is not None:
            node_transform = node_transform.dot(parent_transform)
            
        if node.vertex_animation is not None:
            frames = len(node.vertex_animation.keys)
            frame = frame%frames
            key_frame = node.vertex_animation.keys[frame]
            if key_frame < len(node.vertex_animation.body):
                self.display_frame(node.faces, node.vertex_animation.body[key_frame], node_transform)
            
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
            global draw_index
            draw_index = 0
            for node in scene.nodes:
                self.recursive_display(node, self.curframe)

            pygame.display.update()
            

if __name__ == '__main__':
    
    filename = 'Data/3DData1/Buildings/AT_MGT_H0.xbf'    
    scene = load_xbf(filename)
    viewer = Viewer(1280, 720)    
    viewer.view(scene)
