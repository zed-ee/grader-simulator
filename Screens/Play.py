from pandac.PandaModules import TextNode
from pandac.PandaModules import TransparencyAttrib
from direct.gui.OnscreenImage import OnscreenImage
from pandac.PandaModules import Vec2,Vec3,Vec4,BitMask32
from direct.interval.IntervalGlobal import *

SCALE_2D = Vec3(1.6, 1.0, 1.0)

class GameScreen:
    def __init__(self):
        pass
        
    def show(self):
        self.visible = True
        self.exit = False
        text = TextNode('node name')
        text.setText("Game.")
        textNodePath = aspect2d.attachNewNode(text)
        textNodePath.setScale(0.07)
        self.bg = OnscreenImage(image = 'Dialogs/images/startup_bg.png', pos = (0, 0, 0))
        self.bg.setTransparency(TransparencyAttrib.MAlpha)
        self.bg.setScale(SCALE_2D)

        self.texts = OnscreenImage(image = 'Dialogs/images/startup_texts.png', pos = (0, 0, 0))
        self.texts.setTransparency(TransparencyAttrib.MAlpha)
        self.texts.setScale(SCALE_2D)
        
    def hide(self):
        if self.exit: return
        self.exit = True
        self.texts.destroy()
        self.i = LerpFunc(self.animateBackground,
             fromData=1,
             toData=4,
             duration=4.0,
             blendType='noBlend',
             extraArgs=[],
             name=None)
        self.i.start()
             
    def animateBackground(self, t):
        #print t
        self.bg.setScale(SCALE_2D * t)
