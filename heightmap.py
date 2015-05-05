from panda3d.core import *
import sys,os
loadPrcFileData("", "prefer-parasite-buffer #f")

import direct.directbase.DirectStart
from direct.interval.IntervalGlobal import *
from direct.gui.DirectGui import OnscreenText
from direct.showbase.DirectObject import DirectObject
from direct.actor import Actor
from random import *
from ObjectMover import *
plane_size = 1000
split_count = 4

class World(DirectObject):
    def __init__(self):
        self.step_x = 0
        self.step_y = 0
        self.suffix =""
#        for x in range (0, split_count):
#            for y in range(0, split_count):
#                cam_pos_x = ((x*2 + 1) - split_count) * (plane_size/(split_count*2))
#                cam_pos_y = ((y*2 + 1) - split_count) * (plane_size/(split_count*2))
#                print `((x, y), (cam_pos_x, cam_pos_y))`
        # creating the offscreen buffer.
        #self.camZ = 690
        #self.camZ = 72000
        #self.far = self.camZ
        #self.near = self.far-60
        winprops = WindowProperties.size(1200,1200)
        props = FrameBufferProperties()
        props.setRgbColor(1)
        props.setAlphaBits(1)
        props.setDepthBits(1)
        LBuffer = base.graphicsEngine.makeOutput(
                 base.pipe, "offscreen buffer", -2,
                 props, winprops,
                 GraphicsPipe.BFRefuseWindow,
                 base.win.getGsg(), base.win)
    
        if (LBuffer == None):
           self.t=addTitle("Shadow Demo: Video driver cannot create an offscreen buffer.")
           return

        self.depthmap = Texture()
        LBuffer.addRenderTexture(self.depthmap, GraphicsOutput.RTMCopyRam, GraphicsOutput.RTPDepthStencil)
        if (base.win.getGsg().getSupportsShadowFilter()):
            Ldepthmap.setMinfilter(Texture.FTShadow)
            Ldepthmap.setMagfilter(Texture.FTShadow) 

        # Adding a color texture is totally unnecessary, but it helps with debugging.
        self.colormap = Texture()
        LBuffer.addRenderTexture(self.colormap, GraphicsOutput.RTMCopyRam, GraphicsOutput.RTPColor)
        
        self.LCam=base.makeCamera(LBuffer)
        self.LCam.node().setScene(render)
        #self.LCam.node().getLens().setFov(0.2)
        #self.LCam.node().getLens().setAspectRatio(1.6)

#        self.LCam.setPos(0, 0, 150)
#        self.LCam.lookAt(0, 0,0)
        #self.LCam.node().getLens().setNearFar(self.near,self.far)        
        
        lens = OrthographicLens()
        lens.setFilmSize(1200, 1200)
        lens.setFilmOffset(0,0)
        lens.setNearFar(-60, 0)        
        self.LCam.node().setLens(lens)
        
        base.setBackgroundColor(0,0,0.2,1)
        base.cam.node().setLens(lens)
        #base.camLens.setNearFar(1.0,10000)
        #base.camLens.setFov(10)
 #       self.LCam.setPos(0, 0, self.camZ)
 #       self.LCam.lookAt(0, 0,0)
        #self.moveCam()
        base.disableMouse()

        self.environ = loader.loadModel("models/environment/road")      
        self.environ.reparentTo(render)
        self.environ.setPos(0,0,0)
        self.environ.setPos(-600,0, -600)
        self.environ.setP(90)
        self.accept("o", base.oobe)
        self.accept('p',self.write)
        """
        self.accept('s',self.decnear)
        self.accept('x',self.incnear)

        self.accept('d',self.decfar)
        self.accept('c',self.incfar)
        self.objectMover = ObjectMover(self.LCam, 100)
        """        

    def moveCam(self):
        if (self.step_y >= split_count):
            sys.exit()
        self.suffix = str(self.step_x)+'_'+str(self.step_y)
        cam_pos_x = ((self.step_x*2 + 1) - split_count) * (plane_size/(split_count*2))
        cam_pos_y = ((self.step_y*2 + 1) - split_count) * (plane_size/(split_count*2))
        print `((self.step_x, self.step_y), (cam_pos_x, cam_pos_y))`
        self.step_x = self.step_x +1;
        if (self.step_x >= split_count):
            self.step_x = 0
            self.step_y = self.step_y +1
        self.LCam.setPos(cam_pos_x, cam_pos_y, self.camZ)
        self.LCam.lookAt(cam_pos_x, cam_pos_y, 0)

    def write(self):
        heightmap = PNMImage()
        self.depthmap.store(heightmap)
        #print `heightmap`
        heightmap.write('heightmap/heightmap'+self.suffix+'.bmp')

        colormap = PNMImage()
        self.colormap.store(colormap)
        #print `colormap`
        colormap.write('heightmap/colormap'+self.suffix+'.bmp')
        #self.moveCam()
        
    def decnear(self):
        self.near = self.near -1
        self.setNearFar()
    def incnear(self):
        self.near = self.near +1
        self.setNearFar()
    def decfar(self):
        self.far = self.far -1
        self.setNearFar()
    def incfar(self):
        self.far = self.far +1
        self.setNearFar()

    def setNearFar(self):
        print `(self.near, self.far)`
        self.LCam.node().getLens().setNearFar(self.near,self.far)        
    
    
    
# end of __init__



World()
run()
