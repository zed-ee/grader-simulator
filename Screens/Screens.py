from pandac.PandaModules import TextNode, PNMImageHeader,Filename 
from pandac.PandaModules import TransparencyAttrib, Texture, TextureStage
from direct.gui.OnscreenImage import OnscreenImage
from direct.gui.OnscreenText import OnscreenText

from pandac.PandaModules import Vec2,Vec3,Vec4,BitMask32, VBase4
from direct.interval.IntervalGlobal import *
import time
SCALE_2D = Vec3(1.6, 1.0, 1.0)

class Screens:
    def __init__(self):
        self.startup = StartupScreen()
        self.scenery = SceneryScreen()
        self.instructions = InstructionsScreen()
        self.game = GameScreen()
        self.startup = StartupScreen()
        self.level0start = MultiImageScreen(['levels/level0', 'levels/level0'])
        self.level1start = MultiImageScreen(['levels/level1_summer','levels/level1_winter'])
        self.level2start = MultiImageScreen(['levels/level2_summer','levels/level2_winter'])
        self.level3start = MultiImageScreen(['levels/level3_summer','levels/level3_winter'])
        self.level0end = MultiImageScreen(['levels/level0_ok', 'levels/level0_failed'])
        self.level1end = MultiImageScreen(['levels/level1_ok','levels/level1_failed'])
        self.level2end = MultiImageScreen(['levels/level2_ok','levels/level2_failed'])
        self.level3end = MultiImageScreen(['levels/level3_ok','levels/level3_failed'])
        self.gamecompleted = MultiImageScreen(['gamecompleted_summer','gamecompleted_winter'])
        self.tooltip = Tootltip()
        self.restart = RestartGameScreen()


class DefaultScreen:
    items = {}
    def __init__(self, name=None):
        self.name = name
        self.choise_sound = loader.loadSfx("audio/choise.mp3")

    def show(self, extra=""):
        if self.name:
            print self.name+".show()"
            self.addText(name = "dummy", text = self.name, pos = (-0.5, 0.02), scale = 0.07, fg = (1, 1, 1, 1))
           
    def hide(self):
        self.clear()
        
    def clear(self):
        print "DefaultScreen("+`self.name`+").clear()"
        print `self.items`
        for x in range(len(self.items)):
            k = self.items.keys()[x]
            self.items[k].destroy()
        self.items = {}
            
    def removeItem(self, k):
        if self.items.has_key(k):
            self.items[k].destroy()
            del self.items[k]
        
    def addImage(self, name, image, pos, scale = 1):
        np= OnscreenImage(image = image, pos = pos)
        np.setTransparency(TransparencyAttrib.MAlpha)
        iH=PNMImageHeader() 
        iH.readHeader(Filename(image)) 
        self.items[name] = np
        
    def addText(self, name, text, pos, scale, fg):
        text = OnscreenText(text = text, pos = pos, scale=scale, fg = fg)
        self.items[name] = text

class MultiImageScreen(DefaultScreen):
    items = {}
    
    def __init__(self, images):
        DefaultScreen.__init__(self)
        self.images = images
        
    def show(self, index = 0, message=""):
        self.addImage(name = "bg", image = 'Screens/images/'+self.images[index]+'.png', pos = (0, 0, 0.0))
        self.addText(name = "message", text = message, pos = (0, 0.3), scale = 0.045, fg = (0.99, 0.75, 0, 1))
        #self.items['message'].place()
        
class Tootltip(DefaultScreen):
    items = {}
    visible = False
    pause = False
    def __init__(self):
        DefaultScreen.__init__(self)
        
    def show(self, message=""):
        if self.pause: return
        self.pause = True
        if self.visible:
            self.removeItem("txt")
            self.addText(name = "txt", text = message, pos = (-1.5, 0.75), scale = 0.06, fg = (1, 1, 1, 1))
        else:
            self.visible = True
            self.addImage(name = "message", image = 'Screens/images/message.png', pos = (-1.5, 0, 0.0))
            self.addText(name = "txt", text = message, pos = (-1.5, 0.75), scale = 0.06, fg = (1, 1, 1, 1))
            Sequence(
                Wait(5),
                Func(self.clear)
            ).start()
            
    def clear(self):
        self.pause = True
        DefaultScreen.clear(self)
        Sequence(
            Wait(3),
            Func(self.unpause)
        ).start()
        self.visible = False
        
        
    def unpause(self):
        self.pause = False
        

class StartupScreen(DefaultScreen):
    exit = False
    items = {}
    def __init__(self):
        DefaultScreen.__init__(self)
        
    def show(self, name=""):
        if self.exit: return
        DefaultScreen.show(self)
        print ">StartupScreen.show"
        self.exit = False
        self.addImage(name = "bg", image = 'Screens/images/startup_bg.png', pos = (0, 0, 0.0))
        self.addImage(name = "bg_bot", image = 'Screens/images/startup_bg_bottom.png', pos = (0, 0, 0.0))
        self.addImage(name = "frame", image = 'Screens/images/startup.png', pos = (0, 0, 0.0))
        self.addImage(name = "button_up", image = 'Screens/images/startup_button_up.png', pos = (0, 0, 0.0))
        
        self.addImage(name = "left", image = 'Screens/images/corbex-tutvustus.png', pos = (-1.5, 0, 0.0))
        self.addImage(name = "right", image = 'Screens/images/tehn-andmed.png', pos = (1.5, 0, 0.0))
        """
        self.addImage(name = "frame", image = 'Screens/images/frame.png', pos = (0, 0, 0.07), scale=0.5)
        self.addImage(name = "logo", image = 'Screens/images/logo.png', pos = (0, 0, 0.7), scale=0.5)
        self.addImage(name = "pedal", image = 'Screens/images/pedal_small.png', pos = (1, 0, -0.3), scale=0.5)
        
        self.addText(name = "mnt", text = "Eesti Maanteemuuseum", pos = (-0.9, 0.55), scale = 0.045, fg = (1, 1, 1, 1))
        self.addText(name = "copy", text = "© 2010 Eesti Maantemuuseum. Kõik õigused reserveeritud.", pos = (0.5, -0.55), scale = 0.02, fg = (1, 1, 1, 1))
"""        
        
    def hide(self):
        print ">StartupScreen.hide"
        if self.exit: return
        self.exit = True
        self.i = LerpFunc(self.animateBackground,
             fromData=1,
             toData=4,
             duration=3,
             blendType='noBlend',
             extraArgs=[],
             name=None)
        self.i.start()
        self.removeItem('left')
        self.removeItem('right')
        return 3

    def pressButton(self):
        print "pressButton"
        self.removeItem('button_up')
        self.addImage(name = "button_down", image = 'Screens/images/startup_button_down.png', pos = (0, 0, 0.0))
        
    def releaseButton(self):
        print "releaseButton"
        self.removeItem('button_down')
        self.addImage(name = "button_up", image = 'Screens/images/startup_button_up.png', pos = (0, 0, 0.0))
        
    def toggleButton(self):
        Sequence(
            Func(self.pressButton),
            Wait(1),
            Func(self.releaseButton)
        ).start()
            
    def animateBackground(self, t):
        #print t
        if ('bg' in self.items):
            self.items['bg'].setPos(0, 0, 0.15 * t)
            self.items['bg_bot'].setPos(0, 0, -0.15 * t)
            if t == 4:
                self.clear()
                self.exit = False

            
class SceneryScreen(DefaultScreen):
    items = {}
 
    def __init__(self):
        DefaultScreen.__init__(self)
        
    def show(self, name=""):
        DefaultScreen.show(self)
        print ">SceneryScreen.show"
        self.addImage(name='bg', image = 'Screens/images/scenery_bg.png', pos = (0, 0, 0))
        self.addImage(name='choise', image = 'Screens/images/scenery_summer.png', pos = (0, 0, 0))
        
    def hide(self):
        #DefaultScreen.hide(self)
        self.choise_sound.play()
        print ">SceneryScreen.hide"
        self.clear()
        
    def selectSummer(self):
        self.choise_sound.play()
        self.removeItem('choise')
        self.addImage(name='choise', image = 'Screens/images/scenery_summer.png', pos = (0, 0, 0))

    def selectWinter(self):
        self.choise_sound.play()
        self.removeItem('choise')
        self.addImage(name='choise', image = 'Screens/images/scenery_winter.png', pos = (0, 0, 0))

class RestartGameScreen(DefaultScreen):
    items = {}
 
    def __init__(self):
        DefaultScreen.__init__(self)
        
    def show(self, name=""):
        self.choise_sound.play()
        DefaultScreen.show(self)
        print ">RestartGameScreen.show"
        self.addImage(name='choise', image = 'Screens/images/abort_game.png', pos = (0, 0, 0))
        
    def hide(self):
        #DefaultScreen.hide(self)
        print ">RestartGameScreen.hide"
        self.choise_sound.play()
        self.clear()
        
    def selectContinue(self):
        self.choise_sound.play()
        self.removeItem('choise')
        self.addImage(name='choise', image = 'Screens/images/abort_game_continue.png', pos = (0, 0, 0))

    def selectRestart(self):
        self.choise_sound.play()
        self.removeItem('choise')
        self.addImage(name='choise', image = 'Screens/images/abort_game_restart.png', pos = (0, 0, 0))
        
class InstructionsScreen(DefaultScreen):
    items = {}
    inMotion = False
    step = 0
    def __init__(self):
        DefaultScreen.__init__(self)
        
    def show(self, name=""):
        DefaultScreen.show(self)
        self.addImage(name='bg', image = 'Screens/images/instructions_step0.png', pos = (0, 0, 0))
        #self.addImage(name='text', image = 'Screens/images/instructions_text.png', pos = (0, 0, 0))
        self.step = 0
        self.inMotion = True
        Sequence(
            Wait(5),
            Func(self.showNext)
        ).start()

    def next(self):
        #print "next,", self.inMotion
        if self.inMotion == True: return
        self.inMotion = True
        self.motion = Sequence(
            Wait(1),
            Func(self.showOk),
            Wait(3),
            Func(self.showNext)
        )
        self.motion.start()
        
    def showNext(self):
        #print "showNext,", self.inMotion, self.step
        self.step = self.step + 1
        self.removeItem('bg')
        self.addImage(name='bg', image = 'Screens/images/instructions_step'+str(self.step)+'.png', pos = (0, 0, 0))
        self.inMotion = False
        
    def showOk(self):
        #print "showOk,", self.inMotion, self.step
        self.removeItem('bg')
        self.addImage(name='bg', image = 'Screens/images/instructions_step_ok.png', pos = (0, 0, 0))
        self.choise_sound.play()
        
        
    
    def hide(self):
        #DefaultScreen.hide(self)
        self.choise_sound.play()
        if hasattr(self, "motion"):
            self.motion.finish()
        print ">InstructionsScreen.hide"
        self.clear()
        

class GameScreen(DefaultScreen):
    items = {}

    def __init__(self):
        DefaultScreen.__init__(self, "")
        
    def show(self, name=""):
        DefaultScreen.show(self)
        print ">GameScreen.show"
        self.addImage(name = "progress_bg", image = 'Screens/images/progress_bg.png', pos = (0, 0, 0))
        self.addImage(name = "progress", image = 'Screens/images/progress.png', pos = (0, 0, 0))
#        self.addImage(name = "progress_mask", image = 'Screens/images/progress_mask.png', pos = (0, 0, 0))
         #load the mask, or generate one with PNMImage 
        maskTex = loader.loadTexture('Screens/images/progress_mask.png') 
        maskTex.setWrapU(Texture.WMBorderColor) 
        maskTex.setWrapV(Texture.WMBorderColor) 
        maskTex.setBorderColor(VBase4(1, 1, 1, 0.0)) 
            
        #apply the mask 
        self.stage = TextureStage('ts') 
        self.stage.setMode(TextureStage.MModulate) 
        self.items['progress'].setTexture(self.stage, maskTex) 
       
    def hide(self):
        DefaultScreen.hide(self)
        print ">GameScreen.hide"
        del self.stage
        

        