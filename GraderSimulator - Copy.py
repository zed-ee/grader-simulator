# -*- coding: utf-8 -*-
from pandac.PandaModules import loadPrcFileData
JOYSTICK_WHEEL = 0
JOYSTICK_STICKS = 1

BUTTON_FORWARD = 1
BUTTON_BACKWARD = 10
BUTTON_START = 3
BUTTON_HORN = 2
BUTTON_WINTER = 10
BUTTON_CAM_LEFT = 0
BUTTON_CAM_RIGHT = 7
BUTTON_RESET = 7
AXIS_STEERINGWHEEL = 0
AXIS_ACCELERATE = 2
AXIS_BRAKE = 1

AXIS_MIDDLE_BLADE_UPDOWN = 0
AXIS_MIDDLE_BLADE_ROTATE = 1
BUTTON_FRONT_BLADE_UP = 3
BUTTON_FRONT_BLADE_DOWN = 2
BUTTON_FRONT_BLADE_LEFT = 1
BUTTON_FRONT_BLADE_RIGHT = 0

TIMEOUT = 45
RESTART_MODE_RESTART = 0
RESTART_MODE_CONTINUE = 1
DEBUG_EVENTS = True
DEBUG_EVENTS = True
MODE = 1
if MODE == 1: 
    if 1 == 0:
        loadPrcFileData("", """win-origin 0 0 
            win-size  1680 785
            show-frame-rate-meter #t 
            client-cpu-affinity #t
            client-cpu-affinity-mask 15
            sync-video  #f
            assert-abort #t
            text-encoding utf8
            cursor-hidden #t
            framebuffer-multisample 1
            multisamples 8
            undecorated 1""")
    else:
        loadPrcFileData("", """win-origin -900 0 
            win-size  3080 1440 
            show-frame-rate-meter #f
            client-cpu-affinity #t
            client-cpu-affinity-mask 15
            assert-abort #t
            text-encoding utf8
            framebuffer-multisample 1
            multisamples 2            
            cursor-hidden #t
            undecorated 1""")
elif MODE == 2:
    loadPrcFileData("", """win-origin -900 0 
win-size 3080 1440 
undecorated 1""")
else:
    loadPrcFileData("", """win-origin 0 300 
win-size 1680 350 
undecorated 1""")
import direct.directbase.DirectStart
from direct.showbase.DirectObject import DirectObject
from direct.task.Task import Task

from pandac.PandaModules import AmbientLight,DirectionalLight
from pandac.PandaModules import TextNode,NodePath,LightAttrib
from pandac.PandaModules import Vec2,Vec3,Vec4,BitMask32, Point3
from pandac.PandaModules import PandaNode,Camera, Plane

from pandac.PandaModules import GraphicsWindow
from pandac.PandaModules import FrameBufferProperties
from pandac.PandaModules import WindowProperties
from pandac.PandaModules import GraphicsPipe

from pandac.PandaModules import CollisionTraverser,CollisionNode, CollisionHandlerEvent
from pandac.PandaModules import CollisionHandlerQueue,CollisionRay, CollisionPlane
from pandac.PandaModules import GeoMipTerrain, PNMImage, Filename 
from pandac.PandaModules import Texture, TextureStage, Shader, Quat

from direct.interval.IntervalGlobal import *
from direct.fsm import FSM

from pandac.PandaModules import OdeWorld, OdeSimpleSpace,OdeJointGroup, AntialiasAttrib
from direct.particles.Particles import Particles
from direct.particles.ParticleEffect import ParticleEffect

import sys
import odebase

from Grader.Grader import *
from Grader.Config import *
from environment.Environment import *
from ObjectMover import *
from SnowMachine.SnowGrid import SnowGrid
from GravelMachine.GravelGrid import GravelGrid
from Screens.Screens import *

from direct.directutil import Mopath
from direct.interval.MopathInterval import *
from direct.interval.IntervalGlobal import *
import CarAnimation

render.setAntialias(AntialiasAttrib.MAuto)
try:
    import pygame
    USE_JOYSTICK = True
except Exception, e:
    print `e`
    USE_JOYSTICK = False

#taskMgr.setupTaskChain('paintChain', numThreads = 1, timeslicePriority=False, frameSync=True) 
taskMgr.setupTaskChain('paintChain', numThreads = 0) 

if USE_JOYSTICK == True:
    pygame.init()
    print "Number of joysticks: "+str(pygame.joystick.get_count())
    if pygame.joystick.get_count() > 0:
        for i in range(0, pygame.joystick.get_count()):
            print "Joystick("+str(i)+") ",
            pygame.joystick.Joystick(i).init()
            print "axes: " + str(pygame.joystick.Joystick(i).get_numaxes()),
            print "buttons: " + str(pygame.joystick.Joystick(i).get_numbuttons())
    else:
        USE_JOYSTICK = False

def debug(text):
    print text

FRONT_BLADE = 1
MIDDLE_BLADE = 2     

MODE_WINTER = 1
MODE_SUMMER = 0
class GraderSimulator(FSM.FSM):
        

    keyboardMapping = { 
        "arrow_left": "left", "arrow_right": "right", "arrow_up": "forward", "arrow_down": "reverse",
        ".": "frontblade-up", ",": "frontblade-down", 
        "page_up": "middleblade-up", "page_down": "middleblade-down", 
        "z": "middleblade-rot-left", "x": "middleblade-rot-right", 
        "home": "middleblade-left", "end": "middleblade-right", 
        "k": "frontblade-left", "l": "frontblade-right", 
        "a": "object-inc", "s": "object-dec", "q": "object-set",
        "enter": "next",
        "escape": "prev",
    }

    keyMap = {}
    
    nextState = {
        ('Off', 'next') : 'Startup',
        ('Startup', 'next') : 'Scenery',
        ('Scenery', 'next') : 'Instructions',
        ('Scenery', 'restart') : 'Startup',
        ('Instructions', 'next') : 'LevelStart',
        ('Instructions', 'restart') : 'Startup',
        ('LevelStart', 'next') : 'Game',
        ('LevelStart', 'restart') : 'Startup',
        ('Game', 'finish') : 'LevelCompleted',
        ('Game', 'restart') : 'Startup',
        ('LevelCompleted', 'next') : 'NextLevelStart',
        ('LevelCompleted', 'restart') : 'Startup',
#        ('LevelCompleted', 'prev') : 'Startup',
        ('NextLevelStart', 'next') : 'LevelStart',
        ('LevelStart', 'gamecompleted') : 'GameCompleted',
        ('GameCompleted', 'next') : 'Startup',
        ('GameCompleted', 'restart') : 'Startup',
        
        }

    def defaultFilter(self, request, args):
        print `(self.state, request)`
        key = (self.state, request)
        next = self.nextState.get(key)
        print next
        return next

    def __init__(self):
    
        self.cam1 = None
        self.cam2 = None
        self.cam3 = None
        self.level = 0
        self.mode = MODE_SUMMER
        self.restartMode = -1
        self.result = 0
        self.resultCount = 0
        self.levelEnd = {}
        self.message = ""
        self.levelStarted = False
        self.firstPaint = True
        self.enableRev = True
        FSM.FSM.__init__(self, 'dummy')
        

        #self.setupScreenSingle(2)
        self.setupScreen()
        #render.setShaderAuto()
        self.odeworld = odebase.ODEWorld_Simple()

        self.LoadModels()
        self.grader.setSyncCamera(False)
        self.grader.brake()

        base.disableMouse()
        self.odeworld.EnableODETask(3)

        ##################
        self.screens = Screens()
        self.selectedBlade = MIDDLE_BLADE
        #base.disableMouse();
        self.lastUpdateTime = 0

        self.cTrav = CollisionTraverser()
        
#        self.grader.bodyBox.setPos(GRADER_START_POS)
#        self.grader.body.setHpr(GRADER_START_HPR)
        #self.grader.moveForward()

        #self.cam1.setPos(self.grader.body, CAMERA_LEFT_POS)
        #self.cam2.setPos(self.grader.body, CAMERA_MIDDLE_POS) 
        #self.cam3.setPos(self.grader.body, CAMERA_RIGHT_POS)
        self.setupLights()
        self.setupKeys(self.keyboardMapping)

        self.accept("l", self.printGraderPos)
        #x = loader.loadModel("models/grader/body-box-full")

        #self.cam1.setPos(self.grader.carbody_view, CAMERA_LEFT_POS)
        #self.objectMover = ObjectMover(self.cam2,3, self.grader.body)
        #self.objectMover = ObjectMover(self.grader.carbody,0.1, render)
        #self.objectMover = ObjectMover(self.env.models['golf']['model'],0.1, render)
        self.snow = SnowGrid(render)
        self.gravel = GravelGrid(render)
        
        
        ## BORDER
        self.maze = loader.loadModel("models/environment/border")
        self.maze.setScale(4)
        self.maze.reparentTo(render)
        self.walls = self.maze.find("**/wall_collide")
        self.walls.node().setIntoCollideMask(BitMask32.bit(0))
        #self.walls.show()
        
        self.maze2 = loader.loadModel("models/environment/levelends")
        self.maze2.setScale(4)
        self.maze2.reparentTo(render)
        self.walls2 = self.maze2.find("**/level2_end")
        self.walls2.node().setIntoCollideMask(BitMask32.bit(0))
        #self.walls2.show()
        
        self.cTrav = CollisionTraverser()
        self.cHandler = CollisionHandlerQueue()
        self.cTrav.addCollider(self.grader.ballSphere, self.cHandler)        
        #self.cTrav.showCollisions(render)
        base.cTrav = self.cTrav
        ## BORDER
        #base.cam.setPos(0,0,500)
        #base.cam.lookAt(0,0,0)
        #taskMgr.add(self.handleGameInputs,"handleGameInputsTask")
        #taskMgr.add(self.updateTerrainTask,"update")
#        base.toggleWireframe( ) 

        self.myMotionPathName = Mopath.Mopath()
        self.myMotionPathName.loadFile("models/line")
        #self.myMotionPathName.ls()

        #self.box = NodePath(PandaNode("box"))
        self.box = loader.loadModel("models/car1/car_box")
        self.box.reparentTo(render)
        car = loader.loadModel('models/vehicles/police')
        car.reparentTo(self.box)
        #box.setScale(1.25)
        car.setHpr(180,0,0)
        car.setZ(2)
        
        self.car1coll = self.box.find("**/ball")
        self.car1coll.node().setIntoCollideMask(BitMask32.bit(0))
        #self.car1coll.show()
#        self.box2 = NodePath(PandaNode("box2"))
        self.box2 = loader.loadModel("models/car1/car_box")
        self.box2.reparentTo(render)
        car2 = loader.loadModel('models/vehicles/vw_golf')
        car2.reparentTo(self.box2)
        #box2.setScale(1.25)
        car2.setHpr(180,0,0)
        car2.setZ(2)
        #self.car2coll = car2.find("**/car_collide")
        self.car2coll = self.box2.find("**/ball")
        self.car2coll.node().setIntoCollideMask(BitMask32.bit(0))
        #self.car2coll.show()
        #self.env.models['police']['model'].place()
        
        self.carAnim1 = CarAnimation.CarAnimation(self.box)
        self.carAnim2 = CarAnimation.CarAnimation(self.box2)
       
        
        if 1==1:
            self.request('next')
        else:
            self.enterStartup()
            self.exitStartup()
            #self.mode=MODE_WINTER
            self.exitScenery()
            self.level = 3
            self.request('LevelStart')
            self.request('next')
            #x = self.env.models['police']['model'].getPos(render)
            #print 'police:', `x`, `self.env.models['bmw']['pos']`
            #self.cam2.setPos(self.env.models['police']['pos'])
            #self.cam2.setPos(CAMERA_MIDDLE_POS*2)
            #self.cam2.setHpr(CAMERA_MIDDLE_HPR)
        #print `box`
#        myInterval = MopathInterval(self.myMotionPathName, box, duration= 10, name = "MotionInterval")
#        myInterval.loop()
        #print `self.myMotionPathName`
        #print `myInterval`
        
        taskMgr.add(self.timerTask, 'timerTask')
        self.timer = -1
        """
        self.rain = render.attachNewNode('parent')
        self.rain.reparentTo(self.grader.carbody_view) # use parent.reparentTo(base.cam) for real apps

        # enable particles
        base.enableParticles()

        rain = ParticleEffect()
        rain.loadConfig(Filename('rain.ptf'))
        #Sets particles to birth relative to the parent
        rain.start(self.rain)
        print "Rain effect " + `rain`
        """
    def timerTask(self, task): 
        if self.state != 'Startup':
            seconds = int(task.time) 
            #print self.timer,self.timer+TIMEOUT, seconds
            if self.timer < 0:
                self.timer = seconds
            elif self.timer+TIMEOUT < seconds:
                #print "Timeout!"
                #self.request('restart')
                sys.exit()
        return Task.cont 

        
    def setupKeyboard(self):
        self.accept("v", self.grader.toggleCameraMode)
        self.accept("arrow_up", self.grader.forward)
        self.accept("arrow_up-up", self.grader.normal)
        self.accept("arrow_down", self.grader.backward)
        self.accept("arrow_down-up", self.grader.normal)
        self.accept("space", self.grader.brake, [200.0])
        self.accept("space-up", self.grader.releasebrake)
        self.accept("shift", self.grader.brake, [70.0])
        self.accept("shift-up", self.grader.releasebrake)
        self.accept("arrow_left", self.grader.Turn, [True,-0.01])
        self.accept("arrow_left-up", self.grader.Turn, [False,-0.01])
        self.accept("arrow_right", self.grader.Turn, [True,0.01])
        self.accept("arrow_right-up", self.grader.Turn, [False,0.01])
        
        self.accept("q", self.grader.frontBladeMove, [1, 1])
        self.accept("q-up", self.grader.frontBladeMove, [1, 0])
        self.accept("w", self.grader.frontBladeMove, [1, -1])
        self.accept("w-up", self.grader.frontBladeMove, [1, 0])
        
        self.accept("e", self.grader.frontBladeMove, [0, 1])
        self.accept("e-up", self.grader.frontBladeMove, [0, 0])
        self.accept("r", self.grader.frontBladeMove, [0, -1])
        self.accept("r-up", self.grader.frontBladeMove, [0, 0])
        
        self.accept("y", self.grader.middleBladeMove, [1, 1])
        self.accept("y-up", self.grader.middleBladeMove, [1, 0])
        self.accept("u", self.grader.middleBladeMove, [1, -1])
        self.accept("u-up", self.grader.middleBladeMove, [1, 0])
        
        self.accept("i", self.grader.middleBladeMove, [0, -1])
        self.accept("i-up", self.grader.middleBladeMove, [0, 0])
        self.accept("o", self.grader.middleBladeMove, [0, 1])
        self.accept("o-up", self.grader.middleBladeMove, [0, 0])
        
        self.accept("v-up", self.printTasks)
        
    def printTasks(self):
        print `taskMgr`
    def printGraderPos(self):
        print 'pos: '+ `self.grader.carbody_ode.geom.getPosition()` + ', ('+ `self.grader.carbody_ode.geom.getQuaternion()`
        for i in range(6):
            print 'pos wheel '+ `i` + ": "+`self.grader.wheels_ode[i].geom.getPosition()` + ', ('+ `self.grader.wheels_ode[i].geom.getQuaternion()`

    def LoadModels(self):
        base.setBackgroundColor(0,0,0)
        world = self.odeworld.world
        space = self.odeworld.space

        world.setGravity(0, 0, -10)

        world.initSurfaceTable(5)
        # surface 1, 2 is the wheels
        # surface 3 is the wall
        # (surfaceId1, surfaceId2, mu, bounce, bounce_vel, soft_erp, soft_cfm, slip, dampen)
        #world.setSurfaceEntry(0, 0, 0.8, 0.0, 0, 188, 0.00001, 0.0, 0.002)
        world.setSurfaceEntry(0, 0, 0.8, 0.0, 10, 0.9, 0.00001, 100, 0.002)
        world.setSurfaceEntry(0, 1, 0.8, 0.1, 10, 0.8, 0.00005, 0, 1)
        world.setSurfaceEntry(0, 2, 0.9, 0.1, 10, 0.8, 0.00005, 0, 1)
        world.setSurfaceEntry(3, 1, 0, 0, 100, 0, 1, 100, 0.002)
        world.setSurfaceEntry(3, 2, 0, 0, 100, 0, 1, 100, 0.002)

        self.env = Environment(self.odeworld, 4)

        notifier = self.odeCollisionEvent
        #notifier = None
        self.grader = Grader(self.odeworld, Vec3(320, 400, 45)*4, Vec3(GRADER_START_HPR), False,
            notifier)
        self.grader.setCams(self.cam1, self.cam2, self.cam3)
        self.enableCollisions = True

    def odeCollisionEvent(self, odeobject, geomcollided, entry):
        if self.enableCollisions:
            if geomcollided != self.env.models['ground']['ode_geom'].geom:
                self.grader.stop()
                self.grader.audio.crash()
                print "collision:", `(odeobject, geomcollided, entry)`
                self.message = "Tegid avarii"
                if self.env.models.has_key('houses') and geomcollided == self.env.models['houses']['ode_geom'].geom:
                    self.message = "Sõitsid vastu maja"
                if self.env.models.has_key('bridge') and geomcollided == self.env.models['bridge']['ode_geom'].geom:
                    self.message = "Sõitsid vastu silda"
                elif self.env.models.has_key('bigtree') and  geomcollided == self.env.models['bigtree']['ode_geom'].geom:
                    self.message = "Sõitsid vastu puud"
                elif self.env.models.has_key('signs1') and  geomcollided == self.env.models['signs1']['ode_geom'].geom:
                    self.message = "Sõitsid liiklusmärgile otsa"
                taskMgr.doMethodLater(0.5, self.handleCollision, "collision",  extraArgs = [self.message])
                #self.grader.setSyncCamera(False)
                self.enableCollisions = False
            
    def handleCollision(self, message):
        self.result = -1
        self.request('finish')
        self.grader.stop()
        
    def handleFinish(self, message):
        self.request('finish')
        self.grader.stop()

    def collisionTask(self, task):
        #return Task.cont       #Continue the task indefinitely        
        for i in range(self.cHandler.getNumEntries()):
          entry = self.cHandler.getEntry(i)
          name = entry.getIntoNode().getName()
          print 'collision:  ' + `(entry, name)`
          if name == "wall_collide":
            self.message = 'Sõitsid teelt välja.'
            taskMgr.doMethodLater(0.5, self.handleCollision, "collision",  extraArgs = [self.message])
            return
#            self.grader.setSyncCamera(False)            
          elif name == "car_collide":
            self.message = 'Tegid avarii.'
            self.carAnim1.seq.clearIntervals()
            self.carAnim2.seq.clearIntervals()
            
            print `self.carAnim1.seq`
            taskMgr.doMethodLater(0.5, self.handleCollision, "collision",  extraArgs = [self.message])
            return
          elif name == "level2_end":
            print "Level Completed"
            self.grader.stop()
            #self.message = 'Tase edukalt läbitud. Väga tubli.'
            taskMgr.doMethodLater(0.5, self.handleFinish, "collision",  extraArgs = [self.message])
            self.request('finish')
            return
          elif name == "loseTrigger":
            pass
          
        return Task.cont       #Continue the task indefinitely        

    #Sets up some default lighting
    def setupLights(self):
        ambientLight = AmbientLight( "ambientLight" )
        ambientLight.setColor( Vec4(.4, .4, .35, 1) )
        #ambientLight.setColor( Vec4(0.1, 0.0, 0.0, 1.0) )

        directionalLight = DirectionalLight( "directionalLight" )
        directionalLight.setDirection( Vec3( 0, 8, -2.5 ) )
        directionalLight.setColor( Vec4( 0.9, 0.8, 0.9, 1 ) )
        ambientLightNP = render.attachNewNode(ambientLight)
        render.setLight(ambientLightNP)
        directionalLightNP = render.attachNewNode(directionalLight)
        # This light is facing backwards, towards the camera.
        directionalLightNP.setHpr(180, -20, 0)
        
        render.setLight(directionalLightNP)
        
    def doNothing(self):
        pass
                
    def disableInputs(self):
        print "disableInputs"
        self.accept("escape", self.doNothing)
        self.accept("enter", self.doNothing)
        self.accept("arrow_left", self.doNothing)
        self.accept("arrow_right", self.doNothing)
        self.setupKeys()
        
    def setupKeys(self, mapping = {} ):
        self.keyMap = {}
        for key in mapping.keys():
            self.accept(key, self.setKey, [mapping[key],1])
            self.accept(key+'-up', self.setKey, [mapping[key],0]) 
            self.keyMap[mapping[key]] = 0
	
    #Records the state of the arrow keys
    def setKey(self, key, value):
        self.keyMap[key] = value
        
    def nextScreen(self):
        self.request('next')
    def prevScreen(self):
        self.request('prev')
                 
    def handleStartupInputs(self, task):
        if USE_JOYSTICK == True:
            for e in pygame.event.get(): 
                self.timer = -1
                if DEBUG_EVENTS: print `e`
                if e.joy ==  JOYSTICK_WHEEL:
                    if e.type == pygame.JOYBUTTONDOWN:
                        if e.button == BUTTON_START:
                            self.request('next')
                                
        if (self.keyMap["next"]!=0):
            self.request('next')
            
        return task.cont

    def handleGameCompletedInputs(self, task):
        if USE_JOYSTICK == True:
            for e in pygame.event.get(): 
                self.timer = -1
                if e.joy == 0:
                    if e.type == pygame.JOYAXISMOTION:
                        if e.axis == AXIS_ACCELERATE:
                            if self.enableRev == True:
                                if e.value > 0.6:
                                    self.request('next')
                                    self.enableRev = False
                            else:
                                if e.value < 0:
                                    self.enableRev = True
#                    if e.type == pygame.JOYBUTTONDOWN:
#                        if e.button == BUTTON_FORWARD:
#                            self.request('next')
                                
        if (self.keyMap["next"]!=0):
            self.request('next')
            
        return task.cont
        
    def handleSceneryInputs(self, task):
        if USE_JOYSTICK == True:
            for e in pygame.event.get(): 
                self.timer = -1
                if DEBUG_EVENTS: print `e`
                if e.joy == 0:
                    if e.type == pygame.JOYAXISMOTION:
                        if e.axis == AXIS_STEERINGWHEEL:
                            if e.value < -0.2:
                                if self.mode != MODE_WINTER:
                                    self.selectSceneryWinter()
                            elif e.value > 0.2:
                                if self.mode != MODE_SUMMER:
                                    self.selectScenerySummer()
                        elif e.axis == AXIS_ACCELERATE:
                            if self.enableRev == True:
                                if e.value > 0.6:
                                    #self.grader.rev()
                                    self.request('next')
                                    self.enableRev = False
                            else:
                                if e.value < 0:
                                    self.enableRev = True
                                
                    elif e.type == pygame.JOYBUTTONDOWN:
                        if e.button == BUTTON_RESET:
                            self.showRestartDialog()
#                        elif e.button == BUTTON_FORWARD:
#                            self.request('next')
                        elif e.button == BUTTON_HORN:
                            self.grader.audio.horn()
                    elif  e.type == pygame.JOYBUTTONUP:
                        if e.button == BUTTON_HORN:
                            self.grader.audio.horn(False)
                                
        if (self.keyMap["next"]!=0):
            self.request('next')
        if (self.keyMap["prev"]!=0):
            self.request('prev')
            
        if (self.keyMap["left"]!=0):
            self.selectScenerySummer()
        if (self.keyMap["right"]!=0):
            self.selectSceneryWinter()

        return task.cont
        
    def handleRestartInputs(self, task):
        if USE_JOYSTICK == True:
            for e in pygame.event.get(): 
                self.timer = -1
                if DEBUG_EVENTS: print `e`
                if e.joy == 0:
                    if e.type == pygame.JOYAXISMOTION:
                        if e.axis == AXIS_STEERINGWHEEL:
                            if e.value < -0.2:
                                if self.restartMode != RESTART_MODE_RESTART:
                                    self.selectRestart()
                            elif e.value > 0.2:
                                if self.restartMode != RESTART_MODE_CONTINUE:
                                    self.selectContinue()
                        elif e.axis == AXIS_ACCELERATE:
                            if self.enableRev == True:
                                if e.value > 0.6:
                                    self.restartGame()
                                    self.enableRev = False
                            else:
                                if e.value < 0:
                                    self.enableRev = True
#                    elif e.type == pygame.JOYBUTTONDOWN:
#                        if e.button == BUTTON_FORWARD:
#                            self.restartGame()
                                
        if (self.keyMap["next"]!=0):
            self.request('next')
        if (self.keyMap["prev"]!=0):
            self.request('prev')
            
        if (self.keyMap["left"]!=0):
            self.selectScenerySummer()
        if (self.keyMap["right"]!=0):
            self.selectSceneryWinter()

        return task.cont

    def handleInstructionsInputs(self, task):
        if USE_JOYSTICK == True:
            for e in pygame.event.get(): 
                self.timer = -1
                if DEBUG_EVENTS: print `e`
                if e.joy == 0:
                    if e.type == pygame.JOYAXISMOTION:
                        if e.axis == 0:
                            self.grader.steer(e.value)
                        elif e.axis == AXIS_ACCELERATE:
                            if self.enableRev == True:
                                if e.value > 0.6:
                                    if self.screens.instructions.step == 3:
                                        self.request('next')
                                    else:
                                        self.grader.rev()
                                    self.enableRev = False
                            else:
                                if e.value < 0:
                                    self.enableRev = True

                    elif  e.type == pygame.JOYBUTTONDOWN:
                        if e.button == BUTTON_RESET:
                            self.showRestartDialog()
                        elif e.button == BUTTON_FORWARD:
                            if self.screens.instructions.step == 3:
                                self.request('next')
                        elif e.button == BUTTON_HORN:
                            self.grader.audio.horn()
                    elif  e.type == pygame.JOYBUTTONUP:
                        if e.button == BUTTON_HORN:
                            self.grader.audio.horn(False)
                elif e.joy == JOYSTICK_STICKS:
                    if  e.type == pygame.JOYBUTTONDOWN:
                        if e.button == BUTTON_FRONT_BLADE_UP:
                            self.grader.frontBladeMove(1, 1)
                            self.grader.audio.blade()
                        elif e.button == BUTTON_FRONT_BLADE_DOWN:
                            self.grader.frontBladeMove(1, -1)
                            self.grader.audio.blade()
                        elif e.button == BUTTON_FRONT_BLADE_LEFT:
                            self.grader.frontBladeMove(0, 1)
                            self.grader.audio.blade()
                        elif e.button == BUTTON_FRONT_BLADE_RIGHT:
                            self.grader.frontBladeMove(0, -1)
                            self.grader.audio.blade()                        
                    elif  e.type == pygame.JOYBUTTONUP:
                        if e.button == BUTTON_FRONT_BLADE_UP:
                            self.grader.frontBladeMove(1, 0)
                            self.grader.audio.blade(False)
                        elif e.button == BUTTON_FRONT_BLADE_DOWN:
                            self.grader.frontBladeMove(1, 0)
                            self.grader.audio.blade(False)
                        elif e.button == BUTTON_FRONT_BLADE_LEFT:
                            self.grader.frontBladeMove(0, 0)
                            self.grader.audio.blade(False)
                        elif e.button == BUTTON_FRONT_BLADE_RIGHT:
                            self.grader.frontBladeMove(0, 0)
                            self.grader.audio.blade(False)
                    elif e.type == pygame.JOYAXISMOTION:
                        if abs(e.value) > 0.05:
                            self.grader.audio.blade()
                        else:
                            self.grader.audio.blade(False)
                        #print `
                        if (e.axis == 0):
                            self.grader.middleBladeMove(1-e.axis, -e.value)
                        else:
                            self.grader.middleBladeMove(1-e.axis, e.value)

        if self.screens.instructions.step == 1:
            if self.grader.frontBlade.bladeInGround() or not self.grader.frontBlade.bladeTooStraight():
                self.screens.instructions.next()
        elif  self.screens.instructions.step == 2:
            if self.grader.middleBlade.bladeInGround() or not self.grader.middleBlade.bladeTooStraight():
                self.screens.instructions.next()
            
        if (self.keyMap["next"]!=0):
            self.request('next')
        if (self.keyMap["prev"]!=0):
            self.request('prev')
        """    
        if (self.keyMap["left"]!=0):
            self.grader.Turn(True,-0.01)
        else:
            self.grader.Turn(False,-0.01)
            
        if (self.keyMap["right"]!=0):
            self.grader.Turn(True,0.01)
        else:
            self.grader.Turn(False,0.01)
        """
        return task.cont
        
    def handleLevelStartInputs(self, task):
        if USE_JOYSTICK == True:
            for e in pygame.event.get(): 
                self.timer = -1
                if e.joy == 0:
                    if e.type == pygame.JOYAXISMOTION:
                        if e.axis == AXIS_ACCELERATE:
                            if self.enableRev == True:
                                if e.value > 0.6:
                                    self.request('next')
                                    self.enableRev = False
                            else:
                                if e.value < 0:
                                    self.enableRev = True
                                
        if (self.keyMap["next"]!=0):
            self.request('next')
        if (self.keyMap["prev"]!=0):
            self.request('prev')
        return task.cont

    def handleLevelCompletedInputs(self, task):
        if USE_JOYSTICK == True:
            for e in pygame.event.get(): 
                self.timer = -1
                if e.joy == 0:
                    if e.type == pygame.JOYAXISMOTION:
                        if e.axis == AXIS_ACCELERATE:
                            if self.enableRev == True:
                                if e.value > 0.6:
                                    self.request('next')
                                    self.enableRev = False
                            else:
                                if e.value < 0:
                                    self.enableRev = True
                    elif  e.type == pygame.JOYBUTTONDOWN:
                        if e.button == BUTTON_RESET:
                            self.showRestartDialog()
                                
        if (self.keyMap["next"]!=0):
            self.request('next')
        return task.cont

    # Accepts arrow keys to move either the player or the menu cursor,
    # Also deals with grid checking and collision detection
    def handleGameInputs(self, task):
        #debug("handleGameInputs")
         
        # Get the time elapsed since last frame. We need this
        # for framerate-independent movement.
        elapsed = globalClock.getDt()
#        startpos = self.grader.body.getPos()
        # Consume PyGame events.
        # This seems superfluous, but it is necessary.
        # Otherwise get_axis and get_button don't work.
        
        if USE_JOYSTICK == True:
            for e in pygame.event.get(): 
                if DEBUG_EVENTS: print "handleGameInputs", `e`
                self.timer = -1
                if e.joy == 0:
                    if e.type == pygame.JOYAXISMOTION:
                        if e.axis == AXIS_STEERINGWHEEL:
                            self.grader.steer(e.value)
                        elif e.axis == AXIS_ACCELERATE:
                            if e.value > -0.8:
                                self.grader.accelerate(1+e.value)
                            else:
                                self.grader.brake2(0.2)
                                
                            if self.enableRev == True:
                                if e.value > 0.6:
                                    self.grader.rev()
                                    self.enableRev = False
                            else:
                                if e.value < 0:
                                    self.enableRev = True
                                    
                        elif e.axis == AXIS_BRAKE:
                            if e.value > 0:
                                self.grader.brake2(e.value + 0.4)
#                            if(e.value < -0.99):
#                                self.grader.rev()
                    elif  e.type == pygame.JOYBUTTONDOWN:
                        if e.button == BUTTON_RESET:
                            self.showRestartDialog()
                        elif e.button == BUTTON_CAM_LEFT:
                            self.dr1.setActive(not self.dr1.isActive())
#                        elif e.button == BUTTON_CAM_RIGHT:
                            self.dr3.setActive(not self.dr3.isActive())
                        elif e.button == BUTTON_FORWARD:
                            self.grader.setGear(GEAR_FORWARD)
                        elif e.button == BUTTON_BACKWARD:
                            self.grader.setGear(GEAR_REVERSE)
                        elif e.button == BUTTON_HORN:
                            self.grader.audio.horn()
                    elif  e.type == pygame.JOYBUTTONUP:
                        if e.button == BUTTON_HORN:
                            self.grader.audio.horn(False)
                elif e.joy == JOYSTICK_STICKS:
                    if e.type == pygame.JOYAXISMOTION:
                        if abs(e.value) > 0.05:
                            self.grader.audio.blade()
                        else:
                            self.grader.audio.blade(False)
                        #print `
                        if (e.axis == 0):
                            self.grader.middleBladeMove(1-e.axis, -e.value)
                        else:
                            self.grader.middleBladeMove(1-e.axis, e.value)
                    elif  e.type == pygame.JOYBUTTONDOWN:
                        if e.button == BUTTON_FRONT_BLADE_UP:
                            self.grader.frontBladeMove(1, 1)
                            self.grader.audio.blade()                        
                        elif e.button == BUTTON_FRONT_BLADE_DOWN:
                            self.grader.frontBladeMove(1, -1)
                            self.grader.audio.blade()                        
                        elif e.button == BUTTON_FRONT_BLADE_LEFT:
                            self.grader.frontBladeMove(0, -1)
                            self.grader.audio.blade()                        
                        elif e.button == BUTTON_FRONT_BLADE_RIGHT:
                            self.grader.frontBladeMove(0, 1)
                            self.grader.audio.blade()                        
                    elif  e.type == pygame.JOYBUTTONUP:
                        if e.button == BUTTON_FRONT_BLADE_UP:
                            self.grader.frontBladeMove(1, 0)
                            self.grader.audio.blade(False)                        
                        elif e.button == BUTTON_FRONT_BLADE_DOWN:
                            self.grader.frontBladeMove(1, 0)
                            self.grader.audio.blade(False)                        
                        elif e.button == BUTTON_FRONT_BLADE_LEFT:
                            self.grader.frontBladeMove(0, 0)
                            self.grader.audio.blade(False)                        
                        elif e.button == BUTTON_FRONT_BLADE_RIGHT:
                            self.grader.frontBladeMove(0, 0)
                            self.grader.audio.blade(False)                        

        return task.cont
                    
    def paintSnowTask(self, task):
        if (self.levelStarted and self.grader.hasMoved()):
            if self.firstPaint:
                self.grader.resetTrack()
                self.firstPaint = False
            else:
                if self.mode == MODE_WINTER:
                    self.grader.paintGround(self.snow)
                    self.snow.redraw()
                else:
                    self.grader.paintGround(self.gravel)
                    self.gravel.redraw()
        return task.cont
                        
    def progressTask(self, task):
        if (self.levelStarted and self.grader.hasMoved()):
            p = 0
            if self.screens.game.items.has_key('progress'):
                if not self.firstPaint:
                    if self.mode == MODE_WINTER:
                        self.grader.calcProgress(self.snow)
                        p = self.snow.getProgress()
                    else:
                        self.grader.calcProgress(self.gravel)
                        p = self.gravel.getProgress()
                    #print `p`
                        
                    self.screens.game.items['progress'].setTexOffset(self.screens.game.stage, 1-p, 0)  

                    cnt =  self.resultCount+1
                    self.result = (self.result * self.resultCount + p) / cnt
                    self.resultCount = cnt
                    #print (cnt, self.result)
#                    self.screens.game.items['progress_mask'].setPos(p*1.8, 0, 0)
                    if self.level == 0:
                        if (self.grader.middleBlade.bladeInGround()):
                            self.screens.tooltip.show("Surusid keskmise saha liiga\nvastu maad!")
                            self.grader.brake2(0.2)
                        elif (self.grader.frontBlade.bladeInGround()):
                            self.screens.tooltip.show("Surusid esimese saha liiga\nvastu maad!")
                            self.grader.brake2(0.2)
                        if self.grader.carbody_ode.body.getLinearVel().length() < 2:
                            self.screens.tooltip.show("Hakka sõitma\nAnna gaasi!")
                        elif not self.dr1.isActive():
                            self.screens.tooltip.show("Lülita sisse külgvaade.")
                        elif self.grader.frontBlade.bladeTooUp():
                            self.screens.tooltip.show("Lase esibuldooser alla.")
                        elif self.grader.middleBlade.bladeTooUp():
                            self.screens.tooltip.show("Lase hõlm alla.")
                        elif self.grader.frontBlade.bladeTooStraight():
                            if self.mode == MODE_WINTER:
                                self.screens.tooltip.show("Hoia esibuldooserit viltuselt,\n et lumi ei koguneks saha ette!")
                        elif self.grader.middleBlade.bladeTooStraight():
                            self.screens.tooltip.show("Suuna hõlm väja,\nnii saad puhastada suuremat ala!")
                        elif p < 0.9:
                            self.screens.tooltip.show("Jälgi sõidutee äärejoont!")

                    else:
                        if (self.grader.bladeInGround()):
                            self.screens.tooltip.show("Ära suru sahku vastu maad\n üks sahkadest on liiga madalal!")
                            self.grader.brake2(0.2)
                        elif (self.grader.bladeTooUp()):
                            self.screens.tooltip.show("Vii sahad tööasendisse!")
                        elif self.grader.carbody_ode.body.getLinearVel().length() > 15:
                            self.screens.tooltip.show("Jälgi kiirust!")
                        elif p < 0.6:
                            self.screens.tooltip.show("Proovi püsida oma sõidusuunas.")
                        elif self.grader.frontBlade.bladeTooStraight():
                            self.screens.tooltip.show("Hoia esibuldooserit viltuselt,\n et lumi ei koguneks sahka ette!")
                            #self.grader.brake2(0.1)
                        elif self.grader.middleBlade.bladeTooStraight():
                            self.screens.tooltip.show("Suuna hõlm väja, \nnii saad puhastada suuremat ala!")
                        elif p < 0.9:
                            if self.level == 3:
                                self.screens.tooltip.show("Püsi sõidutee keskel!\n.")
                            else:
                                self.screens.tooltip.show("Jälgi sõidutee äärejoont!\n")
                                
        return task.cont
    
    def createCamera(self, dispRegion, aspect):
        camera=base.makeCamera(base.win,displayRegion=dispRegion, aspectRatio=aspect)
        #camera.node().getLens().setViewHpr(x, y, z)
        #camera.node().getLens().setFov(120) 
        camera.node().getLens().setNear(0.1)
        #camera.node().getLens().setAspectRatio(aspect)
        
        return camera

    def setupScreenSingle(self, cam):

        dr = base.camNode.getDisplayRegion(0)
        if cam ==1:
            self.cam1 = self.createCamera((0, 1, 0, 1), 45.0, 52.5, 0)
            self.cam2 = NodePath(PandaNode("cam2"))
            self.cam3 = NodePath(PandaNode("cam3"))
            dr.setCamera(self.cam1)
        elif cam == 2:
            self.cam1 = NodePath(PandaNode("cam1"))
            self.cam2 = self.createCamera((0, 1, 0, 1), 2.1389)
            self.cam3 = NodePath(PandaNode("cam3"))
            dr.setCamera(self.cam2)
            self.cam2.node().getLens().setFov(120) 
        elif cam == 3:
            self.cam1 = NodePath(PandaNode("cam1"))
            self.cam2 = NodePath(PandaNode("cam2"))
            self.cam3 = self.createCamera((0, 1, 0, 1), 45.0, 52.5, 0)
            dr.setCamera(self.cam3)
        
    def setupScreen(self):
        # set the default display region to inactive so we can remake it



        dr = base.camNode.getDisplayRegion(0)
        dr.setActive(0)


        #settings for main cam, which we will not really be displaying. Actually, this code might be
        # unnecessary!

        #base.camLens.setViewHpr(45.0, 52.5, 0)
        #base.camLens.setFov(112)


        # set up my dome-friendly display regions to reflect the dome geometry

        window = dr.getWindow()
        self.dr1 = window.makeDisplayRegion(0, 0.292, 0, 1)
        self.dr1.setSort(1)
        self.dr2 = window.makeDisplayRegion(0, 1, 0, 1)
        self.dr2.setSort(0)
        self.dr3 = window.makeDisplayRegion(0.708, 1, 0, 1)
        self.dr3.setSort(1)
        
        self.dr1.setClearColorActive(True)
        self.dr2.setClearColorActive(True)
        self.dr3.setClearColorActive(True)
        self.dr1.setClearDepthActive(True)
        self.dr2.setClearDepthActive(True)
        self.dr3.setClearDepthActive(True)
        self.dr1.setActive(False)
        self.dr3.setActive(False)
        
        camNode1 = Camera('cam1')
        self.cam1 = NodePath(camNode1)
        self.dr1.setCamera(self.cam1)
        self.cam1.node().getLens().setAspectRatio(float(self.dr1.getPixelWidth()) / float(self.dr1.getPixelHeight()))
        self.cam1.node().getLens().setNear(0.1)

        camNode2 = Camera('cam2')
        self.cam2 = NodePath(camNode2)
        self.dr2.setCamera(self.cam2)
        self.cam2.node().getLens().setAspectRatio(float(self.dr2.getPixelWidth()) / float(self.dr2.getPixelHeight()))
        self.cam2.node().getLens().setNear(0.1)
        
        camNode3 = Camera('cam3')
        self.cam3 = NodePath(camNode3)
        self.dr3.setCamera(self.cam3)
        self.cam3.node().getLens().setAspectRatio(float(self.dr3.getPixelWidth()) / float(self.dr3.getPixelHeight()))
        self.cam3.node().getLens().setNear(0.1)

        print self.cam1.node().getLens().getFov() 
        print self.cam2.node().getLens().getFov() 
        print self.cam3.node().getLens().getFov() 
        self.cam1.node().getLens().setFov(55) 
        self.cam2.node().getLens().setFov(123) 
        self.cam3.node().getLens().setFov(55) 
        
        #self.cam1.reparentTo(base.camera)
        # create four cameras, one per region, with the dome geometry. Note that we're not using the 
        # base cam. I tried this at first, pointing the base cam at region 1. It worked, but it threw the 
        # geometry off for some reason. The fix was to create four cameras, parent them to the base 
        # cam, and off we go. 

        #self.cam1 = self.createCamera((0, 0.292, 0, 1), float(dr1.getPixelWidth()) / float(dr1.getPixelHeight()))
        #dr1.setCamera(self.cam1)
        #self.cam2 = self.createCamera((0.292, 0.708, 0.2889, 1), float(dr1.getPixelWidth()) / float(dr1.getPixelHeight()))
        #dr2.setCamera(self.cam2)
        #self.cam3 = self.createCamera((0.708, 1, 0, 1), float(dr1.getPixelWidth()) / float(dr1.getPixelHeight()))
        #dr3.setCamera(self.cam3)


        # loading some baked-in model


        self.cam1.reparentTo(base.cam)
        self.cam2.reparentTo(base.cam)
        self.cam3.reparentTo(base.cam)
        
    def enterStartup(self):
        print "enterStartup"
        self.grader.stopEngine()
        self.dr1.setActive(False)
        self.dr3.setActive(False)
        taskMgr.remove("paintSnowTask")
        taskMgr.remove("progressTask")
        self.env.models['road']['model'].reparentTo(render)
        self.env.models['gravel3']['model'].detachNode()
        self.env.models['gravel']['model'].reparentTo(render)

        if self.mode == MODE_WINTER:
            self.snow.clear()
        else:
            self.gravel.clear()
        self.mode = MODE_SUMMER
        self.env.selectSummer()    
        self.level = 0
        self.grader.setPosQuat( Vec3(1329.5, 1628.75, 178.855), (0.971424, 0.0114102, 0.00194733, 0.237069), [
                                    (Vec3(1320.86, 1637.8, 178.367), (-0.358772, 0.705538, -0.037394, 0.610001)),
                                    (Vec3(1327.31, 1625.38, 178.054), (0.263939, 0.460471, 0.535744, 0.65672)),
                                    (Vec3(1327.08, 1641.03, 178.379), (0.356115, 0.378157, 0.596817, 0.611547)),
                                    (Vec3(1333.52, 1628.6, 178.065), (0.534824, -0.656632, 0.260793, -0.463448)),
                                    (Vec3(1329.06, 1622.01, 177.984), (0.387032, 0.347022, 0.615535, 0.592367)),
                                    (Vec3(1335.27, 1625.23, 177.995), (0.413413, -0.699113, 0.102229, -0.574352))
                                    ])
        self.grader.reset2()
        self.grader.HideSpeedMeter()
        taskMgr.add(self.handleStartupInputs,"handleStartupInputsTask")
        self.screens.startup.show()
        self.grader.setSyncCamera(False)
        self.cam2.setPos(CAMERA_MIDDLE_POS_STARTUP)
        self.cam2.setHpr(CAMERA_MIDDLE_HPR_STARTUP)
        print `base.camera.getQuat(render)`
        ### TEST
#        self.gravel.load('level0_snow', 0.5)
        ### TEST    
        
        
    def exitStartup(self):
        print "exitStartup"
        taskMgr.remove("handleStartupInputsTask")
        self.grader.startEngine()
        Parallel(
            Func(self.screens.startup.toggleButton),
            Sequence(
                Wait(2),
                Func(self.screens.startup.hide)
            )
        ).start()
        
    def enterScenery(self):
        #self.mode = MODE_WINTER
        taskMgr.remove("paintSnowTask")
        taskMgr.remove("progressTask")
        Sequence(
            Wait(2),
            LerpPosHprInterval(self.cam2, pos=CAMERA_MIDDLE_POS_SCENERY, hpr=CAMERA_MIDDLE_HPR_SCENERY, duration=3),
#            Func(self.env.selectWinter),
            Func(taskMgr.add, self.handleSceneryInputs, "handleSceneryInputsTask"),
            Func(self.screens.scenery.show)
            ).start()
        
    def exitScenery(self):
        self.screens.scenery.hide()
        taskMgr.remove("handleSceneryInputsTask")
        taskMgr.add(self.paintSnowTask, "paintSnowTask",  taskChain = 'paintChain')
#        taskMgr.add(self.paintSnowTask, "paintSnowTask")

    def enterInstructions(self):
        self.grader.HideSpeedMeter()
        self.grader.SyncSideCameras()
        Parallel(
            Sequence(
                LerpPosHprInterval(self.cam2, pos=CAMERA_MIDDLE_POS_INSTRUCTIONS, hpr=CAMERA_MIDDLE_HPR_INSTRUCTIONS, duration=4),
                Func(self.screens.instructions.show),
                Wait(7),
                Func(taskMgr.add, self.handleInstructionsInputs, "handleInstructionsInputsTask"),
                ),
            Sequence(
                Wait(2),
                Func(self.grader.reset)
                )
        ).start()

        
    def exitInstructions(self):
        self.screens.instructions.hide()
        taskMgr.remove("handleInstructionsInputsTask")
        
    def showRestartDialog(self):
        self.screens.restart.show()
        taskMgr.remove("handleGameInputsTask")
        taskMgr.remove("handleInstructionsInputsTask")
        taskMgr.remove("handleSceneryInputsTask")
        taskMgr.remove("handleStartupInputsTask")
        taskMgr.remove("handleLevelCompletedInputsTask")
        self.odeworld.EnableODETask(0)
        taskMgr.add(self.handleRestartInputs,"handleRestartInputsTask")
        
    def selectRestart(self):
        self.restartMode = RESTART_MODE_RESTART
        self.screens.restart.selectRestart()

    def selectContinue(self):
        self.restartMode = RESTART_MODE_CONTINUE
        self.screens.restart.selectContinue()
        
    def restartGame(self):
        taskMgr.remove("handleRestartInputsTask")
        self.odeworld.EnableODETask(3)
        self.screens.restart.hide()
        if self.restartMode == RESTART_MODE_RESTART:
            #self.request('restart')
            sys.exit()
        elif self.state == 'Scenery':
            taskMgr.add(self.handleSceneryInputs, "handleSceneryInputsTask")
        elif self.state == 'Instructions':
            taskMgr.add(self.handleInstructionsInputs, "handleInstructionsInputsTask")
        elif self.state == 'Game':
            taskMgr.add(self.handleGameInputs, "handleGameInputsTask")
        elif self.state == 'LevelCompleted':
            taskMgr.add(self.handleLevelCompletedInputs, "handleLevelCompletedInputsTask")
        else:
            print `self.state`
        
    def enterGame(self):
        #self.grader.setSyncCamera(True)
        self.result = 0
        self.resultCount = 0
        self.levelStarted = True
        self.firstPaint = True
        #self.grader.stopEngine()
        self.grader.stop()
        self.grader.steer(0)
        self.grader.brake2(1.0)
        taskMgr.add(self.handleGameInputs,"handleGameInputsTask")
        taskMgr.add(self.collisionTask, "collisionTask")
        taskMgr.add(self.progressTask, "progressTask",  taskChain = 'paintChain')
        
        self.enableCollisions = True
        self.grader.reset()
        self.tasks = Sequence(
                Func(self.grader.setSyncCamera, True),
#                Func(self.grader.brake),
                Func(self.grader.ShowSpeedMeter),
                Func(self.grader.releasebrake),
                Func(self.setupKeyboard),
                )
        self.tasks.start()
        self.screens.game.show()
        self.dr1.setActive(True)
        self.dr3.setActive(True)
        if self.level == 3:
            Sequence(
                Func(self.carAnim1.play),
                Wait(60),
                Func(self.carAnim2.play),
            ).start()        
        
        
    def exitGame(self):
        self.dr1.setActive(False)
        self.dr3.setActive(False)
        self.tasks = Sequence(
            Wait(0.5),
            Func(self.grader.setSyncCamera, False)
            ).start()
        self.screens.game.hide()
        #self.disableInputs()
        taskMgr.remove("handleGameInputsTask")
        taskMgr.remove("collisionTask")
        taskMgr.remove("progressTask")
        if self.level == 3:
            self.carAnim1.seq.clearIntervals()
            self.carAnim2.seq.clearIntervals()
        
        
    def defaultEnter(self):
        print "defaultEnter"
        
    def defaultExit(self):
        print "defaultExit"

    def selectScenerySummer(self):
        self.mode = MODE_SUMMER
        self.screens.scenery.selectSummer()
        self.env.selectSummer()

    def selectSceneryWinter(self):
        self.mode = MODE_WINTER
        self.screens.scenery.selectWinter()
        self.env.selectWinter()
            
    def enterLevelStart(self):
        self.message=""
        self.levelStarted = False
        self.box.detachNode()
        self.box2.detachNode()
        if self.mode == MODE_WINTER:
            self.snow.clear()
        else:
            self.gravel.clear()
            self.env.models['road']['model'].detachNode()
            self.env.models['gravel3']['model'].reparentTo(render)
            self.env.models['gravel']['model'].detachNode()
        if self.level < 4:
            if self.level == 0:
                self.enterLevel0Intro()
            elif self.level == 1:
                self.enterLevel1Intro()
            elif self.level == 2:
                self.enterLevel2Intro()
            elif self.level == 3:
                self.enterLevel3Intro()
            Sequence(
                Wait(1),
                Func(taskMgr.add, self.handleLevelStartInputs, "handleLevelStartInputsTask"),
                ).start()
        else:
            self.level = 0
            self.demand('gamecompleted')
            
    def exitLevelStart(self):
        if self.level == 0:
            self.exitLevel0Intro()
        elif self.level == 1:
            self.exitLevel1Intro()
        elif self.level == 2:
            self.exitLevel2Intro()
        elif self.level == 3:
            self.exitLevel3Intro()
        taskMgr.remove("handleLevelStartInputsTask")
         
    def enterNextLevelStart(self):
#        if self.result > 0.65 or ((self.level == 0 or self.mode == MODE_SUMMER) and self.result >= 0):
        if self.result > 0.65 or ((self.level == 0) and self.result >= 0):
            self.level = self.level + 1
        self.demand('next')

    def exitNextLevelStart(self):
        self.exitLevelStart()
        
    def enterLevelCompleted(self):
        self.screens.game.show()
    
#        if self.result > 0.65 or (self.result >= 0 and self.mode == MODE_SUMMER):
        if self.result > 0.65:
            if self.level != 0:
                if self.result > 0.85:
                    self.message = "Töötulemus on väga hea."
                elif self.result > 0.75:
                    self.message = "Töötulemus on hea."
                elif self.result >  0.5:
                    self.message = "Töötulemus on rahuldav."
                else:
                    self.message = "Töötulemus on kehv."
            result = 0
        elif self.result > 0:
            if self.level != 0:
                self.message = "Kahjuks ei saa töötulemusega raule jääda."
                result = 1
            else:
                result = 0
        else:
            result = 1
        print 'result: ' + `(self.screens.game.items.has_key('progress'), self.result)`
        if self.screens.game.items.has_key('progress'):
            self.screens.game.items['progress'].setTexOffset(self.screens.game.stage, 1-self.result, 0)  
        
        if self.level == 0:
            self.screens.level0end.show(result, self.message)
            if result == 0:
                Sequence(
                    Wait(0.5),
                    LerpPosHprInterval(self.cam2, pos=Vec3(1461.36, 1640.03, 204.903), hpr=Vec3(11.5892, -35.0444, -5.33993), duration=4),
                ).start()
        elif self.level == 1:
            self.screens.level1end.show(result, self.message)
            if result == 0:
                Sequence(
                    Wait(0.5),
                    LerpPosHprInterval(self.cam2, pos=Vec3(1928.22, 918.771, 191.255), hpr=Vec3(16.1904, -35.3418, 2.035), duration=4),
                ).start()
        elif self.level == 2:
            self.screens.level2end.show(result, self.message)
            if result == 0:
                Sequence(
                    Wait(0.5),
                    LerpPosHprInterval(self.cam2, pos=Vec3(3117.02, 736.265, 138.927), hpr=Vec3(61.9806, -34.8236, -6.60664), duration=4),
                ).start()
        elif self.level == 3:
            self.screens.level3end.show(result, self.message)
            if result == 0:
                Sequence(
                    Wait(0.5),
                    LerpPosHprInterval(self.cam2, pos=Vec3(3946.69, 177.991, 155.82), hpr=Vec3(30.5327, -40.8385, 3.76417), duration=4),
                ).start()
        Sequence(
            Wait(2),
            Func(taskMgr.add, self.handleLevelCompletedInputs, "handleLevelCompletedInputsTask"),
            ).start()
        
    def exitLevelCompleted(self):
        if self.level == 0:
            self.screens.level0end.hide()
        elif self.level == 1:
            self.screens.level1end.hide()
        elif self.level == 2:
            self.screens.level2end.hide()
        elif self.level == 3:
            self.screens.level3end.hide()
        taskMgr.remove("handleLevelCompletedInputsTask")
        self.screens.game.hide()
                
                
    def enterGameCompleted(self):
        self.screens.gamecompleted.show(self.mode)
        taskMgr.add(self.handleGameCompletedInputs, "handleGameCompletedInputsTask")

    def exitGameCompleted(self):
        self.screens.gamecompleted.hide()
        taskMgr.remove("handleGameCompletedInputsTask")
     
    def enterLevel0Intro(self):
        self.grader.setPosQuat( Vec3(1237.39, 2098.63, 172.243), (-0.243187, -0.0112304, 0.0216488,  0.969673), [
                                    (Vec3(1246.15, 2089.69, 172.09), (-0.698979, -0.4016, 0.586818,  0.0760983)),
                                    (Vec3(1239.56, 2102.02, 171.447), (0.151114, -0.540025, -0.462597,  0.686688)), 
                                    (Vec3(1239.98, 2086.38, 172.015), (-0.120347, -0.675035, -0.223494,  0.692744)),
                                    (Vec3(1233.39, 2098.71, 171.367), (-0.581909, 0.0740049, 0.707203,  -0.394675)),
                                    (Vec3(1237.77, 2105.37, 171.273), (-0.334631, -0.711114, 0.00308959,  0.618328)),
                                    (Vec3(1231.6, 2102.06, 171.192), (0.559281, -0.112885, -0.702012,  0.426194))
                                    ])

        if self.mode == MODE_WINTER:
            self.snow.load('level0_snow', 0.4)
        else:
            self.gravel.load('level0_snow', 0.5)
            
        """
        self.grader.setPosQuat( Vec3(1157.7, 2245.08, 162.98), (-0.214638, -0.0112082, 0.0249852, 0.97631), [
                                    (Vec3(1165.93, 2235.63, 162.901), (0.657691, 0.507436, -0.49805, -0.248792)),
                                    (Vec3(1160.07, 2248.33, 162.175), (-0.680531, -0.126562, 0.699714, -0.176805)),
                                    (Vec3(1159.57, 2232.7, 162.824), (0.553144, -0.163703, -0.691947, 0.4341)),
                                    (Vec3(1153.71, 2245.39, 162.095), (0.42493, 0.694539, -0.152244, -0.560242)),
                                    (Vec3(1158.48, 2251.77, 161.97), (0.361738, -0.39991, -0.587945, 0.602941)),
                                    (Vec3(1152.12, 2248.83, 161.895), (-0.155291, -0.695343, -0.148518, 0.685802))
                                ])
"""          
        self.grader.setSyncCamera(True)
        self.screens.level0start.show(self.mode, self.message)
 
    def exitLevel0Intro(self):
        self.screens.level0start.hide()
        
    def enterLevel1Intro(self):
        if self.mode == MODE_WINTER:
            self.snow.load('level1_snow',0.7)
        else:
            self.gravel.load('level1_snow', 0.7)
            
        self.grader.setPosQuat( Vec3(1488.8, 1656.08, 176.329), (0.273734, -0.0191399,  0.0101874,  -0.961561), [
                                    (Vec3(1498.06, 1647.73, 175.112), (0.525507, -0.134574,  -0.682844,  0.489343)),
                                    (Vec3(1490.69, 1659.63, 175.538), (0.432702, -0.250937,  -0.649227,  0.572977)),
                                    (Vec3(1492.11, 1644.05, 175.306), (-0.6919, -0.511637,  0.471857,  0.191974)),
                                    (Vec3(1484.75, 1655.95, 175.759), (0.231923, -0.441254,  -0.538183,  0.679607)),
                                    (Vec3(1488.69, 1662.86, 175.649), (0.60394, 0.628471,  -0.299015,  -0.38842)),
                                    (Vec3(1482.75, 1659.17, 175.88), (0.621054, 0.614165,  -0.327753,  -0.360098))
                                ])

        self.grader.setSyncCamera(True)
        self.screens.level1start.show(self.mode)
        
    def exitLevel1Intro(self):
        self.screens.level1start.hide()

    def enterLevel2Intro(self):
        if self.mode == MODE_WINTER:
            self.snow.load('level2_snow', 1)
        else:
            self.gravel.load('level2_snow', 0.7)
            
        self.grader.setPosQuat( Vec3(1911.25, 1011.45, 137.853), (0.328843, -0.0337757, 0.0238795, -0.943478), [
                                    (Vec3(1921.35, 1004.25, 136.098), (-0.6916, -0.569954, 0.388763, 0.213787)),
                                    (Vec3(1912.69, 1015.21, 137.085), (-0.584949, -0.029296, 0.68931, -0.426413)),
                                    (Vec3(1915.88, 999.894, 136.485), (0.0932334, 0.590587, 0.356586, -0.717887)),
                                    (Vec3(1907.22, 1010.85, 137.401), (0.640559, 0.631666, -0.277436, -0.337214)),
                                    (Vec3(1910.34, 1018.18, 137.364), (0.322465, 0.674626, 0.144311, -0.648128)),
                                    (Vec3(1904.86, 1013.82, 137.659), (-0.722169, -0.391482, 0.568087, -0.0499004)),
                                 ])  
        self.grader.setSyncCamera(True)
        self.screens.level2start.show(self.mode)

    def exitLevel2Intro(self):
        self.screens.level2start.hide()
        
    def enterLevel3Intro(self):
        if self.mode == MODE_WINTER:
            self.snow.load('level3_snow', 1.5)
            #self.env.models['ekskavaator']['model'].detachNode()
            self.env.models['ekskavaator']['ode_geom'].geom.setPosition(Vec3(0,0,0))
            self.env.models['golf']['model'].reparentTo(render)
            self.env.models['golf']['ode_geom'].geom.setPosition(Vec3(3698.60, 901.72, 65.26))
            self.env.models['golf']['model'].setPos(Vec3(3698.60, 901.72, 65.26))
        else:
            self.gravel.load('level3_snow', 0.7)
            self.env.models['ekskavaator']['model'].reparentTo(render)
            self.env.models['ekskavaator']['ode_geom'].geom.setPosition(Vec3(3711.89, 826.64, 69.95))
            self.env.models['ekskavaator']['model'].setPos(Vec3(3711.89, 826.64, 69.95))
            self.env.models['golf']['model'].detachNode()
            self.env.models['golf']['ode_geom'].geom.setPosition(Vec3(0,0,0))
            self.box.reparentTo(render)
            self.box2.reparentTo(render)

        self.grader.setPosQuat( Vec3(3037.76, 844.969, 49.4659), (0.845311, -0.0145352,  -0.00145039,  -0.534075), [
                                    (Vec3(3047.09, 853.259, 48.3665), (0.415554, 0.613273,  -0.338986,  0.579913)),
                                    (Vec3(3034.45, 847.252, 48.7086), (-0.242749, 0.067758,  -0.69745,  0.670854)),
                                    (Vec3(3050.09, 846.939, 48.4952), (-0.266277, 0.0431386,  -0.699373,  0.661901)),
                                    (Vec3(3037.45, 840.932, 48.8311), (0.699634, 0.679449,  0.171428,  0.139548)),
                                    (Vec3(3031.01, 845.621, 48.8018), (0.350414, 0.0485753,  0.699058,  -0.621424)),
                                    (Vec3(3034.02, 839.301, 48.9227), (0.563349, 0.314958,  0.625976,  -0.437715))
                                ])

        self.grader.setSyncCamera(True)
        self.screens.level3start.show(self.mode)
        
    def exitLevel3Intro(self):
        self.screens.level3start.hide()

try:        
    w = GraderSimulator()
    run()

    joystick.quit()
    pygame.quit() 
except:
    pass