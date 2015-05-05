from pandac.PandaModules import Texture, TextureStage, Shader, PNMImage
from pandac.PandaModules import Vec2,Vec3,Vec4,BitMask32
from pandac.PandaModules import NodePath,PandaNode,ShaderAttrib, OmniBoundingVolume, Filename
from direct.showbase.DirectObject import DirectObject
from pandac.PandaModules import EggData
from collections import deque
from direct.gui.OnscreenText import OnscreenText, TextNode
from direct.stdpy import threading

import math

MAX_HEIGHT = (60.0 * 4.0)
PLANE_SIZE = 80.0
BITMAP_SIZE = 256
BITMAP_SIZE_CALC = 256
DETAIL_SNOW_PLANES = [(240,640), (260,640), (240, 620), (260, 620),(260, 600),(280, 600),(260, 580),(280, 580),(300, 580),
(280,560), (300, 560), (300, 540), (320, 540), (300, 520), (320, 520), (320, 500),(340, 500), (320, 480),(340, 480)]

def irange(start, finish):
    if start == finish:
        return [start]
    if start < finish:
        return range(start, finish + 1)
    if start > finish:
        return range(start, finish - 1, -1)

class LevelCalculator(DirectObject):
    def __init__(self, parent):
        self.calc = {}
        self.accept('o',self.write)
        
    def clear(self):
        #return
        self.calc = {}
    
    def load(self, level, depth=0.5):
        self.load_init(level, depth)
        
    def load_init(self, level, depth):
        self.clear()
        print "Loading snow planes from "+"levels/"+level+".egg ...",
        egg = EggData()
        egg.read(Filename("models/environment/snow.egg"))
#        egg.read(Filename("levels/"+level+".egg"))
        planeGroup = egg.getFirstChild()
        plane = planeGroup.getFirstChild()
        while plane != None:            
            pos = plane.getFirstChild().getVertex(12).getPos3()
            (x, y, z) = pos * 4
            x = round(x/PLANE_SIZE)*PLANE_SIZE
            y = round(y/PLANE_SIZE)*PLANE_SIZE

            rx = x / PLANE_SIZE
            ry = y / PLANE_SIZE

            if not self.calc.has_key(rx):
               self.calc[rx] = {}
            self.calc[rx][ry] = PNMImage(BITMAP_SIZE_CALC,BITMAP_SIZE_CALC)
            r, g, b = 1, 0, 1
            track = Filename('calc/t'+str(ry)+'_'+str(rx)+'.png')
            if track.exists():
                self.calc[rx][ry].read(track)
            else:
                print "calc missing"
                self.calc[rx][ry].addAlpha()
                self.calc[rx][ry].fill(r, g, b)
                self.calc[rx][ry].alphaFill(1)
            
            plane = planeGroup.getNextChild()
   
    
    def calcPicturePos(self, x, y):
        px = ((x / PLANE_SIZE) + 0.5) * BITMAP_SIZE
        py = ((y / PLANE_SIZE) + 0.5) * BITMAP_SIZE
        return (px, py)
        
        
    def paint(self, fromPos, toPos, color):
        z = (((fromPos[2] + toPos[2]) / 2))# / MAX_HEIGHT)
        (x1, y1) = self.calcPicturePos(fromPos[0], fromPos[1])
        (x2, y2) = self.calcPicturePos(toPos[0], toPos[1])
        c = color
        c[0] = c[0] * z
        c[2] = c[2] * z
        self.drawLine(x1, y1, x2, y2, c)
        
        
    def getProgress(self):
        if len(self.history) > 0:
            return sum(self.history) / len(self.history)
        else:
            return 0
        
                
    
    
    def write(self):        
        print "Writing calc to disc"
        for x in range(len(self.calc)):
            rx = self.calc.keys()[x]
            for y in range(len(self.calc[rx])):
                ry = self.calc[rx].keys()[y]
                self.calc[rx][ry].write('out/c'+str(ry)+'_'+str(rx)+'.png')
                    
     
    def calcProgress(self, guides):
        diffs = []
        for i in range(len(guides)):
            pos = guides[i].getPos(render)
            (x, y) = self.calcPicturePos(pos[0], pos[1])
            p = self.getPixelReal(x, y)
            c = self.getPixelCalc(x, y)
            #print `(p, c)`
            if c == None or p == None:
                diff = 1
            elif (c[2] < 1):
                diff = (p[2]-c[2])
#            elif (c[0] < 1):
#                diff = abs(p[0]-c[0])
            else:
                diff = 1
            print diff
            diffs.append(abs(diff))
        avg = sum(diffs) / len(diffs)
        self.history.append((1-avg))
        
    def drawPixel(self, x, y, color):
        c = [0, 0, 0]
        for a in range(-2, 3):
            for b in range(-2, 3):
                old = self.getPixelReal(x+a, y+b)
                if (old != None):
                    c[0] = color[0]
                    c[1] = color[1]
                    c[2] = color[2]
                    rx = int(math.floor((x+a) / BITMAP_SIZE))
                    ry = int(math.floor((y+b) / BITMAP_SIZE))
                    z = self.height[rx][ry]
                    if c[2] > 0: 
                        diff = c[2] - z
                        omin, omax = self.min, self.max
                        self.min = min(self.min, diff)
                        self.max = max(self.max, diff)
                        if omin != self.min or omax != self.max:
                            print "min-max:", self.min, self.max
                        
#                    print `(c, z, color)`
                    if c[2] > 0: c[2] = (c[2]-z +15) /25    # diff -15 ... 10 -> 0...1
                    if c[0] > 0: c[0] = (c[0]-z +15) /25
                    #print `(c, z)`
                    w = (1-float((abs(a)+abs(b))) / 8) #weight
                    
                    if c[2] == 0: c[2] = 1
                    if c[0] == 0: c[0] = 1
        
                    self.drawPixelReal(x+a, y+b, c[0], max(old[1],w), min(old[2], c[2]), 1)
                    
            
    def getPixelReal(self, x, y):
        rx = int(math.floor(x / BITMAP_SIZE)) 
        ry = int(math.floor(y / BITMAP_SIZE))
        dx = int(x - rx * BITMAP_SIZE)
        dy = int(y - ry * BITMAP_SIZE)
        if self.calc.has_key(rx) and self.calc[rx].has_key(ry):
            return self.calc[rx][ry].getXelA(dx, BITMAP_SIZE - dy -1)
        else:
            #print "getPixelReal",`((rx, ry), (dx, dy))`
            return None
    
    def drawPixelReal(self, x, y, r, g, b, a=0):
        rx = int(math.floor(x / BITMAP_SIZE)) 
        ry = int(math.floor(y / BITMAP_SIZE))
        dx = int(x - rx * BITMAP_SIZE)
        dy = int(y - ry * BITMAP_SIZE)
        #print `((rx, ry), (dx, dy))`
        if self.calc.has_key(rx) and self.calc[rx].has_key(ry):
            #print 'xxx>' + `((rx, ry), (dx, dy), (r,g,b, a))`
            self.calc[rx][ry].setXelA(dx, BITMAP_SIZE - dy -1, r, g, b, a)
    
            
    def drawLine(self, x0, y0, x1, y1, c):
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
                self.drawPixel(y, x, c)
            else:
                self.drawPixel(x, y, c)
            error = error - deltay
            if error < 0:
                y = y + ystep
                error = error + deltax