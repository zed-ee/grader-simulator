from Config import *
from pandac.PandaModules import Point3, Vec3 

from pandac.PandaModules import GeomVertexFormat, GeomVertexData, GeomVertexWriter 
from pandac.PandaModules import Geom, GeomNode, GeomPoints, NodePath, GeomLinestrips 

import math, random

def swap(a, b):
    c = a
    a = b
    b = c

def plot(image, x, y, c):
    #old = image.getXel(x,y)
    #print 'p:'+`(x, y, c)` 
    for a in range(-2, 3):
        for b in range(-1, 2):
            if x+a < 0 or y+b < 0: continue
            if x+a >= SNOW_BITMAP_SIZE or y+b >= SNOW_BITMAP_SIZE: continue
            old = image.getXel(x+a, y+b)
            m = (abs(a)+abs(b))
            image.setXel(x+a, y+b, min(old[0], c[0]), 0, min(old[2], c[2]*m))
                    
            
        
def irange(start, finish):
    if start == finish:
        return [start]
    if start < finish:
        return range(start, finish + 1)
    if start > finish:
        return range(start, finish - 1, -1)
 
 
def drawLine(image, x0, y0, x1, y1, c):
    orig_x0 = x0
    orig_y0 = y0
 
    if abs(y1 - y0) > abs(x1 - x0):
        steep = True
    else:
        steep = False
 
    if steep:
        x0, y0 = y0, x0
        x1, y1 = y1, x1
    if x0 > x1:
        x0, x1 = x1, x0
        y0, y1 = y1, y0
 
    deltax = x1 - x0
    deltay = abs(y1 - y0)
    error = deltax / 2
    y = y0
    if y0 < y1:
        ystep = 1 
    else:
         ystep = -1
    for x in irange(x0,x1):
        if steep:
            plot(image, y, x, c)
        else:
            plot(image, x, y, c)
        error = error - deltay
        if error < 0:
            y = y + ystep
            error = error + deltax
  
 
def scale(val, inscale, outscale, offset):
    return int(max(0, min(outscale-1, (val / inscale * outscale) + offset)))
        
    
def paintPath(image, pos1, pos2, color, board_size, board_scale, texture_size):
        
    x1 =  scale(pos1[0], board_size*board_scale, texture_size, texture_size/2)
    y1 =  scale(pos1[1], board_size*board_scale, texture_size, texture_size/2)
    x2 =  scale(pos2[0], board_size*board_scale, texture_size, texture_size/2)
    y2 =  scale(pos2[1], board_size*board_scale, texture_size, texture_size/2)
    #print `(x1, x2, y1, y2)`
    if (x1 <> x2) or (y1 <> y2):
        #print "L:"+`(x1, x2, y1, y2)`
        drawLine(image, x1, y1, x2, y2, color) 

def getOBB(collObj):
    ''' get the Oriented Bounding Box '''
    # save object's parent and transformation
    parent=collObj.getParent()
    trans=collObj.getTransform()
    # ODE need everything in world's coordinate space,
    # so bring the object directly under render, but keep the transformation
    collObj.wrtReparentTo(render)
    # get the tight bounds before any rotation
    collObj.setHpr(0,0,0)
    bounds=collObj.getTightBounds()
    offset=collObj.getBounds().getCenter()-collObj.getPos()
    # bring object to it's parent and restore it's transformation
    collObj.reparentTo(parent)
    collObj.setTransform(trans)
    # (max - min) bounds
    box=bounds[1]-bounds[0]
#        print bounds[0], bounds[1]
    return [box[0],box[1],box[2]], [offset[0],offset[1],offset[2]]
    
    
class wireGeom: 
  
  def __init__ (self):    
    # GeomNode to hold our individual geoms 
    self.gnode = GeomNode ('wirePrim') 
    
    # How many times to subdivide our spheres/cylinders resulting vertices.  Keep low 
    # because this is supposed to be an approximate representation 
    self.subdiv = 12 

  def line (self, start, end):  
    
    # since we're doing line segments, just vertices in our geom 
    format = GeomVertexFormat.getV3() 
    
    # build our data structure and get a handle to the vertex column 
    vdata = GeomVertexData ('', format, Geom.UHStatic) 
    vertices = GeomVertexWriter (vdata, 'vertex') 
        
    # build a linestrip vertex buffer 
    lines = GeomLinestrips (Geom.UHStatic) 
    
    vertices.addData3f (start[0], start[1], start[2]) 
    vertices.addData3f (end[0], end[1], end[2]) 
    
    lines.addVertices (0, 1) 
      
    lines.closePrimitive() 
    
    geom = Geom (vdata) 
    geom.addPrimitive (lines) 
    # Add our primitive to the geomnode 
    self.gnode.addGeom (geom) 

  def circle (self, radius, axis, offset):  
    
    # since we're doing line segments, just vertices in our geom 
    format = GeomVertexFormat.getV3() 
    
    # build our data structure and get a handle to the vertex column 
    vdata = GeomVertexData ('', format, Geom.UHStatic) 
    vertices = GeomVertexWriter (vdata, 'vertex') 
        
    # build a linestrip vertex buffer 
    lines = GeomLinestrips (Geom.UHStatic) 
    
    for i in range (0, self.subdiv): 
      angle = i / float(self.subdiv) * 2.0 * math.pi 
      ca = math.cos (angle) 
      sa = math.sin (angle) 
      if axis == "x": 
        vertices.addData3f (0, radius * ca, radius * sa + offset) 
      if axis == "y": 
        vertices.addData3f (radius * ca, 0, radius * sa + offset) 
      if axis == "z": 
        vertices.addData3f (radius * ca, radius * sa, offset) 
    
    for i in range (1, self.subdiv): 
      lines.addVertices(i - 1, i) 
    lines.addVertices (self.subdiv - 1, 0) 
      
    lines.closePrimitive() 
    
    geom = Geom (vdata) 
    geom.addPrimitive (lines) 
    # Add our primitive to the geomnode 
    self.gnode.addGeom (geom) 

  def capsule (self, radius, length, axis): 
    
    # since we're doing line segments, just vertices in our geom 
    format = GeomVertexFormat.getV3() 
    
    # build our data structure and get a handle to the vertex column 
    vdata = GeomVertexData ('', format, Geom.UHStatic) 
    vertices = GeomVertexWriter (vdata, 'vertex') 
        
    # build a linestrip vertex buffer 
    lines = GeomLinestrips (Geom.UHStatic) 
    
    # draw upper dome 
    for i in range (0, self.subdiv / 2 + 1): 
      angle = i / float(self.subdiv) * 2.0 * math.pi 
      ca = math.cos (angle) 
      sa = math.sin (angle) 
      if axis == "x": 
        vertices.addData3f (0, radius * ca, radius * sa + (length / 2)) 
      if axis == "y": 
        vertices.addData3f (radius * ca, 0, radius * sa + (length / 2)) 

    # draw lower dome 
    for i in range (0, self.subdiv / 2 + 1): 
      angle = -math.pi + i / float(self.subdiv) * 2.0 * math.pi 
      ca = math.cos (angle) 
      sa = math.sin (angle) 
      if axis == "x": 
        vertices.addData3f (0, radius * ca, radius * sa - (length / 2)) 
      if axis == "y": 
        vertices.addData3f (radius * ca, 0, radius * sa - (length / 2)) 
    
    for i in range (1, self.subdiv + 1): 
      lines.addVertices(i - 1, i) 
    lines.addVertices (self.subdiv + 1, 0) 
      
    lines.closePrimitive() 
    
    geom = Geom (vdata) 
    geom.addPrimitive (lines) 
    # Add our primitive to the geomnode 
    self.gnode.addGeom (geom) 

  def rect (self, width, height, axis): 
    
    # since we're doing line segments, just vertices in our geom 
    format = GeomVertexFormat.getV3() 
    
    # build our data structure and get a handle to the vertex column 
    vdata = GeomVertexData ('', format, Geom.UHStatic) 
    vertices = GeomVertexWriter (vdata, 'vertex') 
        
    # build a linestrip vertex buffer 
    lines = GeomLinestrips (Geom.UHStatic) 
    
    # draw a box 
    if axis == "x": 
      vertices.addData3f (0, -width, -height) 
      vertices.addData3f (0, width, -height) 
      vertices.addData3f (0, width, height) 
      vertices.addData3f (0, -width, height) 
    if axis == "y": 
      vertices.addData3f (-width, 0, -height) 
      vertices.addData3f (width, 0, -height) 
      vertices.addData3f (width, 0, height) 
      vertices.addData3f (-width, 0, height) 
    if axis == "z": 
      vertices.addData3f (-width, -height, 0) 
      vertices.addData3f (width, -height, 0) 
      vertices.addData3f (width, height, 0) 
      vertices.addData3f (-width, height, 0) 

    for i in range (1, 3): 
      lines.addVertices(i - 1, i) 
    lines.addVertices (3, 0) 
      
    lines.closePrimitive() 
    
    geom = Geom (vdata) 
    geom.addPrimitive (lines) 
    # Add our primitive to the geomnode 
    self.gnode.addGeom (geom) 

  def generate (self, type, radius=1.0, length=1.0, extents=Point3(1, 1, 1), R=-1, G=-1, B=-1): 
    if R==-1: 
        R=random.uniform(0,1) 
    if G==-1: 
        G=random.uniform(0,1) 
    if B==-1: 
        B=random.uniform(0,1) 

    if type == 'sphere': 
      # generate a simple sphere 
      self.circle (radius, "x", 0) 
      self.circle (radius, "y", 0) 
      self.circle (radius, "z", 0) 

    if type == 'capsule': 
      # generate a simple capsule 
      self.capsule (radius, length, "x") 
      self.capsule (radius, length, "y") 
      self.circle (radius, "z", -length / 2) 
      self.circle (radius, "z", length / 2) 

    if type == 'box': 
      # generate a simple box 
      self.rect (extents[1]/2, extents[2]/2, "x") 
      self.rect (extents[0]/2, extents[2]/2, "y") 
      self.rect (extents[0]/2, extents[1]/2, "z") 

    if type == 'cylinder': 
      # generate a simple cylinder 
      self.line ((0, -radius, -length / 2), (0, -radius, length/2)) 
      self.line ((0, radius, -length / 2), (0, radius, length/2)) 
      self.line ((-radius, 0, -length / 2), (-radius, 0, length/2)) 
      self.line ((radius, 0, -length / 2), (radius, 0, length/2)) 
      self.circle (radius, "z", -length / 2) 
      self.circle (radius, "z", length / 2) 

    if type == 'ray': 
      # generate a ray 
      self.circle (length / 10, "x", 0) 
      self.circle (length / 10, "z", 0) 
      self.line ((0, 0, 0), (0, 0, length)) 
      self.line ((0, 0, length), (0, -length/10, length*0.9)) 
      self.line ((0, 0, length), (0, length/10, length*0.9)) 

    if type == 'plane': 
      # generate a plane 
      length = 3.0 
      self.rect (1.0, 1.0, "z") 
      self.line ((0, 0, 0), (0, 0, length)) 
      self.line ((0, 0, length), (0, -length/10, length*0.9)) 
      self.line ((0, 0, length), (0, length/10, length*0.9)) 

    # rename ourselves to wirePrimBox, etc. 
    name = self.gnode.getName() 
    self.gnode.setName(name + type.capitalize()) 

    NP = NodePath (self.gnode)  # Finally, make a nodepath to our geom 
    NP.setColor(R, G, B)   # Set default color 

    return NP      