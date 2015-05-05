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

class GravelGrid(DirectObject):
    def __init__(self, parent):
        self.snow = NodePath(PandaNode("snow_planes"))
        self.snow.reparentTo(render)
        self.tracks = {}
        self.calc = {}
        self.planes = {}
        self.updates = {}
        self.height = {}
        self.history = deque([], 20)
        self.min = 999
        self.max = 0
        self.textObject = OnscreenText(text = "", pos = (0.75,0.95), scale = 0.07,fg=(1,0.5,0.5,1),align=TextNode.ACenter,mayChange=1)        
        #return
        self.shader = Shader.load(Shader.SLGLSL, "GravelMachine/gravel_vrtx.sha", "GravelMachine/gravel_frag.sha","") 
        #self.shader = Shader.load(Shader.SLGLSL, "SnowMachine/snow_vrtx.sha", "SnowMachine/snow_frag.sha","") 
        
        self.heightmap = loader.loadTexture('heightmap/medium/heightmap_road-RGB.png')
        self.heightmap2 = loader.loadTexture('heightmap/medium/heightmap-RGB-gravelroad.bmp')
        self.normalmap = loader.loadTexture('heightmap/medium/normalmap.png')
        #snow = loader.loadTexture('plane_copy.png')
        #tracks = loader.loadTexture('tracks.png')
        #tex2.setMinfilter( Texture.FTNearest )
        #tex2.setFormat(Texture.FRgba32)

        #self.load_init('level0_snow')
        #tex3 = loader.loadTexture('models/SnowTexture.png')
        tex3 = loader.loadTexture('models/environment/summer/mudel/3093.jpg')
        #self.snow.setTexture(tex3)
        self.snow.setShaderInput("colorMap", tex3)
        self.snow.setShaderInput("heightmap", self.heightmap)
        self.snow.setShaderInput("heightmap2", self.heightmap2)
        self.snow.setShaderInput("normalmap", self.normalmap)
        #self.snow.setShaderInput("pos", 0, 0, 0, 0)
        tex3 = loader.loadTexture('empty.png')
        self.snow.setTexture(tex3)
        parent.setShaderInput("tracks", tex3)
        tex3 = loader.loadTexture('empty2.png')
        parent.setShaderInput("bumpMap", tex3)
        #cube.setShaderInput("snow", snow)
        #cube.setShaderInput("snowHeight", Vec4(100, 100, 100, 100))

        #self.snow.node().setBounds(OmniBoundingVolume()) 
        #self.snow.node().setFinal(True) 
#        self.snow.setShader(self.shader)      
        #taskMgr.add(self.paintSnow,"paintSnow")
        self.accept('p',self.write)
        
    def clear(self):
        #return
        for x in range(len(self.planes)):
            rx = self.tracks.keys()[x]
            for y in range(len(self.planes[rx])):
                ry = self.tracks[rx].keys()[y]
                self.planes[rx][ry].removeNode()
                #del self.tracks[rx][ry]
        self.tracks = {}
        self.planes = {}
        self.history.clear()
    
    def load(self, level, depth=0.5):
        #pass
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
            #print 'ddd:', `pos`,
            (x, y, z) = pos * 4
            print `(x, y, z)`
            x = round(x/PLANE_SIZE)*PLANE_SIZE
            y = round(y/PLANE_SIZE)*PLANE_SIZE
#            print `(x, y, z)`
            node = loader.loadModel("models/helpers/plane_med_new")
            node.reparentTo(self.snow)
            #node.setScale(2.5)
            node.setPos(x, y, z)
            node.setShaderInput("pos", x, y, z, depth)
            #node.setShaderInput("heightmap", self.heightmap)
            #node.setShaderInput("normalmap", self.normalmap)
            #node.setDepthWrite(False)
            #node.setDepthTest(False)
            rx = x / PLANE_SIZE
            ry = y / PLANE_SIZE
            if not self.planes.has_key(rx):
               self.planes[rx] = {}
            self.planes[rx][ry] = node
#            self.planes[rx][ry].setShaderInput("pos", x, y, z, 0)
            if not self.tracks.has_key(rx):
               self.tracks[rx] = {}
               self.height[rx] = {}
            self.tracks[rx][ry] = PNMImage(BITMAP_SIZE,BITMAP_SIZE)
            self.height[rx][ry] = z
            r, g, b = 1, 0, 1
            track = Filename('GravelMachine/tracks/t'+str(ry)+'_'+str(rx)+'.png')
#            d = int((60-ry)*60 + rx);
#            print `d`
#            track = Filename('tracks/tile'+str(d)+'.png')
            if track.exists():
                self.tracks[rx][ry].read(track)
            else:
                print "track missing"
                self.tracks[rx][ry].addAlpha()
                self.tracks[rx][ry].fill(r, g, b)
                self.tracks[rx][ry].alphaFill(1)
                #self.tracks[rx][ry].read("empty.png")

            if not self.calc.has_key(rx):
               self.calc[rx] = {}
            self.calc[rx][ry] = PNMImage(BITMAP_SIZE_CALC,BITMAP_SIZE_CALC)
            r, g, b = 1, 0, 1
            track = Filename('GravelMachine/tracks/c'+str(ry)+'_'+str(rx)+'.png')
            if track.exists():
                self.calc[rx][ry].read(track)
            else:
                print "calc missing"
                self.calc[rx][ry].addAlpha()
                self.calc[rx][ry].fill(r, g, b)
                self.calc[rx][ry].alphaFill(1)
            self.updateShader(rx, ry)
            
            plane = planeGroup.getNextChild()
#        print "done", `self.tracks`
        self.snow.setShader(self.shader)      
   
    def paintSnow(self, task):        
        if base.mouseWatcherNode.hasMouse():
            #get the mouse position as a Vec2. The values for each axis are from -1 to
            #1. The top-left is (-1,-1), the bottom right is (1,1)
            mpos = base.mouseWatcherNode.getMouse()    
            x = (mpos.getX()*200) + 300
            y = (mpos.getY()*200) + 300 
            
            rx = int(math.floor(x / 20)*20)+10
            ry = int(math.floor(y / 20)*20)+10
            dx = int((((x - rx) / 20)-0.5) * BITMAP_SIZE)
            dy = (BITMAP_SIZE-1) - int((((y - ry)  / 20)+0.5) *BITMAP_SIZE)
            rx = rx 
            ry = ry
            if self.tracks.has_key(rx) and self.tracks[rx].has_key(ry):
                print "mouse: ", `(x,y)`, `(rx,ry)`, `(dx,dy)`, 
                self.tracks[rx][ry].setXelVal(dx, dy, 255, 255, 255)
                val = self.tracks[rx][ry].getXelVal(dx, dy)
                print `(val[0],val[1],val[2])`
                #self.tracks[rx][ry].write('out/a'+str(rx)+'_'+str(ry)+'.png')
                myTexture=Texture()
                myTexture.load(self.tracks[rx][ry])
                #self.planes[rx][ry].setShaderInput("pos", rx, ry, 0, 0)
                self.planes[rx][ry].setShaderInput("tracks", myTexture)
                #self.planes[rx][ry].setShaderInput("ground", self.ground)
                
        return task.cont
    
    def calcPicturePos(self, x, y):
        """
        rx = int(math.floor(x / PLANE_SIZE)*PLANE_SIZE)+PLANE_SIZE/2 
        ry = int(math.floor(y / PLANE_SIZE)*PLANE_SIZE)+PLANE_SIZE/2
        dx = int((((x - rx) / PLANE_SIZE)+0.5) * BITMAP_SIZE)
        dy = (BITMAP_SIZE-1) - int((((y - ry)  / PLANE_SIZE)+0.5) *BITMAP_SIZE)
        px = ((rx / PLANE_SIZE) * BITMAP_SIZE)  + dx
        py = ((ry / PLANE_SIZE) * BITMAP_SIZE)  + dy
        """
        px = ((x / PLANE_SIZE) + 0.5) * BITMAP_SIZE
        py = ((y / PLANE_SIZE) + 0.5) * BITMAP_SIZE
        return (px, py)
        
    def paintWheel(self, fromPos, toPos):
        #print `(fromPos, toPos)`
        (x1, y1) = self.calcPicturePos(fromPos[0], fromPos[1])
        (x2, y2) = self.calcPicturePos(toPos[0], toPos[1])
        #print `((x1, y1), (x2, y2))`
        self.drawLine(x1, y1, x2, y2, Vec3(0, 0, 0.3))
        
    def paintFrontBlade(self, fromPos, toPos, height):
        #print `(fromPos, toPos)`
        (x1, y1) = self.calcPicturePos(fromPos[0], fromPos[1])
        (x2, y2) = self.calcPicturePos(toPos[0], toPos[1])
        #print `((x1, y1), (x2, y2))`
        self.drawLine(x1, y1, x2, y2, Vec3(0, 0, height))
        
    def paint(self, fromPos, toPos, color):
        z = (((fromPos[2] + toPos[2]) / 2))# / MAX_HEIGHT)
        (x1, y1) = self.calcPicturePos(fromPos[0], fromPos[1])
        (x2, y2) = self.calcPicturePos(toPos[0], toPos[1])
        #print `((x1, y1), (x2, y2), z)`
        #print (((fromPos[2] + toPos[2]) / 2))
        c = color
        c[0] = c[0] * z
        c[2] = c[2] * z
        self.drawLine(x1, y1, x2, y2, c)
        
        
    def redraw(self):
#        x = threading.Lock()
        upd = self.updates
        self.updates = {}
#        del x
        for i in range(len(upd)):
            (x, y) = upd.keys()[i]
            self.updateShader(x, y)
            
    def getProgress(self):
        if len(self.history) > 0:
            return sum(self.history) / len(self.history)
        else:
            return 0
        
                
    
    def updateShader(self, rx, ry):
        myTexture=Texture()
        myTexture.load(self.tracks[rx][ry])
#        self.planes[rx][ry].setShaderInput("pos", rx, ry, 0, 0)
        self.planes[rx][ry].setShaderInput("tracks", myTexture)
#        self.planes[rx][ry].setShaderInput("ground", self.ground)
    
    def write(self):        
        print "Writing tracks to disc"
        for x in range(len(self.calc)):
            rx = self.calc.keys()[x]
            for y in range(len(self.calc[rx])):
                ry = self.calc[rx].keys()[y]
                self.calc[rx][ry].write('out/c'+str(ry)+'_'+str(rx)+'.png')
                
        for x in range(len(self.tracks)):
            rx = self.tracks.keys()[x]
            for y in range(len(self.tracks[rx])):
                ry = self.tracks[rx].keys()[y]
                self.tracks[rx][ry].write('out/t'+str(ry)+'_'+str(rx)+'.png')
     
     
    def calcProgress(self, guides):
        diffs = []
        for i in range(len(guides)):
            pos = guides[i].getPos(render)
            (x, y) = self.calcPicturePos(pos[0], pos[1])
            p = self.getPixelReal(x, y)
            c = self.getPixelCalc(x, y)
            #print `(p, c)`
            diff = 1
            if c == None or p == None:
                diff = 1
            elif (c[2] < 1):
                diff = ((p[2]-c[2])*20)
            elif (c[0] < 1):
                diff = ((p[0]-c[0])*20)
            elif p[2] == 1:
                diff = 0
            else:
                diff = 1
            diff = (1 - min(1, abs(diff)))
            diff = min(1, diff*1.2+0.1)
            diffs.append(diff)
        avg = sum(diffs) / len(diffs)
        self.history.append(avg)
        
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
#                        if omin != self.min or omax != self.max:
#                            print "min-max:", self.min, self.max
                        
#                    print `(c, z, color)`
                    if c[2] > 0: c[2] = (c[2]-z +15) /25    # diff -15 ... 10 -> 0...1
                    if c[0] > 0: c[0] = (c[0]-z +15) /25
                    #print `(c, z)`
                    w = (1-float((abs(a)+abs(b))) / 8) #weight
#                    print w
#                    if (old[2] > 0 and old[3] > w):
#                        c[0] = 0
#                        if (old[2] < c[2]):
#                            c[2] = old[2]
                    
                    #print (c[0], c[1], c[2], w)
#                    if(old[2] < c[2]):
#                        print `(old, c, w, (a,b))`
                    
                    if c[2] == 0: c[2] = 1
                    if c[0] == 0: c[0] = 1
        
                    self.drawPixelReal(x+a, y+b, c[0], max(old[1],w), min(old[2], c[2]), 1)
                    
    def drawPixelOld(self, x, y, c):
        cr = Vec3(0, 0, c[2])
        if c[2] < 0:
            cr[2] = -c[2]
        for a in range(-2, 3):
            for b in range(-2, 3):
                old = self.getPixelReal(x+a, y+b)
                if (old != None):
                    
                    m = (1-(abs(a)+abs(b)) / 8)
                    if c[2] < 0:
                        r = 1+m*cr[2]
                    else:
                        r = (1-m*cr[2])
                    #print ((x,y), (a, b), `c`, m)
                    self.drawPixelReal(x+a, y+b, min(old[0], cr[0]), 0, (old[2] * r))    
            
    def getPixelReal(self, x, y):
        rx = int(math.floor(x / BITMAP_SIZE)) 
        ry = int(math.floor(y / BITMAP_SIZE))
        dx = int(x - rx * BITMAP_SIZE)
        dy = int(y - ry * BITMAP_SIZE)
        if self.tracks.has_key(rx) and self.tracks[rx].has_key(ry):
            return self.tracks[rx][ry].getXelA(dx, BITMAP_SIZE - dy -1)
        else:
            #print "getPixelReal",`((rx, ry), (dx, dy))`
            return None
    
    def getPixelCalc(self, x, y):
        rx = int(math.floor(x / BITMAP_SIZE)) 
        ry = int(math.floor(y / BITMAP_SIZE))
        dx = int((x - rx * BITMAP_SIZE))
        dy = int((y - ry * BITMAP_SIZE))
        cx = int((float(dx) / BITMAP_SIZE) * BITMAP_SIZE_CALC)
        cy = int((float(dy) / BITMAP_SIZE) * BITMAP_SIZE_CALC)
        if self.calc.has_key(rx) and self.calc[rx].has_key(ry):
            return self.calc[rx][ry].getXel(cx, BITMAP_SIZE_CALC - cy -1)
        else:
            #print "getPixelCalc", `((rx, ry), (cx, cy))`
            return None

    def drawPixelReal(self, x, y, r, g, b, a=0):
        rx = int(math.floor(x / BITMAP_SIZE)) 
        ry = int(math.floor(y / BITMAP_SIZE))
        dx = int(x - rx * BITMAP_SIZE)
        dy = int(y - ry * BITMAP_SIZE)
        #print `((rx, ry), (dx, dy))`
        if self.tracks.has_key(rx) and self.tracks[rx].has_key(ry):
            #print 'xxx>' + `((rx, ry), (dx, dy), (r,g,b, a))`
            #self.calc[rx][ry].setXelA(dx, BITMAP_SIZE - dy -1, r, g, b, a)
            self.tracks[rx][ry].setXelA(dx, BITMAP_SIZE - dy -1, r, g, b, a)
#            x = threading.Lock()
            self.updates[(rx, ry)] = True
#            del x
            #self.drawPixelRealCalc( x, y, r, g, b)
    
    def drawPixelRealCalc(self, x, y, r, g, b):
        DIFF =  1
        
        rx = int(math.floor(x / BITMAP_SIZE)) 
        ry = int(math.floor(y / BITMAP_SIZE))
        dx = int((x - rx * BITMAP_SIZE)*DIFF)
        dy = int((y - ry * BITMAP_SIZE)*DIFF)
        cx = int((float(dx) / BITMAP_SIZE) * BITMAP_SIZE_CALC)
        cy = int((float(dy) / BITMAP_SIZE) * BITMAP_SIZE_CALC)
        #print `((rx, ry), (dx, dy), (cx, cy))`
        if self.calc.has_key(rx) and self.calc[rx].has_key(ry):
            self.calc[rx][ry].setXel(cx, BITMAP_SIZE_CALC - cy -1, r, g, b)
            (cr, cg, cb) = self.calc[rx][ry].getXel(cx, BITMAP_SIZE_CALC - cy -1)

            
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