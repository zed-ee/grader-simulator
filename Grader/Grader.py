from direct.actor.Actor import Actor
from pandac.PandaModules import CollisionTraverser,CollisionNode
from pandac.PandaModules import CollisionHandlerQueue,CollisionRay, CollisionSphere
from pandac.PandaModules import CollisionHandlerFloor
from pandac.PandaModules import Vec3,Vec4,BitMask32, Quat, TransparencyAttrib, Material, Filename
from direct.gui.OnscreenImage import OnscreenImage, DirectObject, TextureStage
from direct.interval.IntervalGlobal import *
from direct.task.Task import Task
from collections import deque
from direct.particles.Particles import Particles
from direct.particles.ParticleEffect import ParticleEffect
from random import randint, random

import math
import odebase
from Config import *
from FrontWheels import *
from BackWheels import *
from SteeringWheel import *
from MiddleBlade import *
from FrontBlade import *
from pandac.PandaModules import OdeBody, OdeMass, Quat, OdeBoxGeom
GEAR_FORWARD = 1
GEAR_REVERSE = -1
#from wiregeom import wireGeom
class Grader():
    CAMERA_DEFAULT_MODE = 0
    CAMERA_STICKY_MODE = 1
    CAMERA_DRIVER_MODE = 2
    modelpath = "models/car1"
    def __init__(self,odeworld,pos,hpr,syncCamera=True, odeEventHandler=None):
        self.odeworld = odeworld
        self.syncCamera=syncCamera
        world = odeworld.world
        space = odeworld.space
        #variables
        world.setContactSurfaceLayer(0.01)
        self.cameramode = self.CAMERA_DRIVER_MODE
        self.turn=False
        self.turnspeed=0.0
        self.turnangle=0.0
        self.carOrientation=1
        self.acceleration=False
        self.maxSpeed=0
        self.accForce=0
        self.stoppingforce = 0
        self.objects = []
        self.turnangle_fixed = False
        self.pointer = None
        self.lastPos = pos
        self.moved = False
        self.speedHistory = deque([0], 10)
        self.gear = GEAR_FORWARD
        base.enableParticles()
        
        #Body of the our car - similar the boxes

        self.carbody = loader.loadModel("%s/car_box" % self.modelpath)
        bodyHeight=-0.8
        bodyShift = 0
        self.carbody.setPos(pos)
        self.carbody.reparentTo(render)
        density = 6
        collidebit = 3
        catbit = 4
        #self.carbody.setHpr(hpr)
        self.carbody_ode = odebase.ODEbox(world,space,
            self.carbody,
            None, density, 0, collidebit, catbit)

        odeworld.AddObject(self.carbody_ode)
        self.objects.append(self.carbody_ode)
        
        self.ballSphere = self.carbody.find("**/ball")
        self.ballSphere.node().setFromCollideMask(BitMask32.bit(0))
        self.ballSphere.node().setIntoCollideMask(BitMask32.allOff())
        #self.ballSphere.show()
        
        # car appearance specific
        self.carbody_view = NodePath(PandaNode("carbody_view"))
        self.body = loader.loadModel("models/grader/body_uus.egg")
        #self.carbody_view.setScale(0.8,0.8,0.8)
        self.carbody_view.setZ(1.2)
        self.carbody_view.setH(180)
        self.carbody_view.setY(3)
        self.carbody_view.setZ(-2.4)
        #self.carbody_view.setTwoSided(True)
        self.carbody_view.reparentTo(self.carbody)
        self.body.setH(-180)
        self.body.setY(2.2)
        self.body.setZ(3.2)
        self.body.reparentTo(self.carbody_view)
        #self.carbody_view.hide()
        #self.carbody_view.setRenderModeWireframe()
        nodes = [ "head.L", "head.R", "rear.L", "rear.R"]
        self.lights = []
        """    
        for node in nodes:
            np = self.carbody_view.find("**/%s" % node)
            np.setLightOff()
            self.lights.append(np)
        self.npTubes = [ self.carbody_view.find("**/tube.L"), self.carbody_view.find("**/tube.R") ]
        self.npBody = self.carbody_view.find("**/body")
        self.lightsTexture1 = loader.loadTexture("%s/car1.png" % self.modelpath)
        self.lightsTexture2 = loader.loadTexture("%s/car2.png" % self.modelpath)
        """
        self.npTubes = [NodePath(PandaNode("left_guide"))]
        self.controlPanel= loader.loadModel("models/grader/control-panel")
        self.controlPanel.reparentTo(self.carbody_view)
        self.controlPanel.flattenLight()

        self.frontWheels = FrontWheels(self.carbody_view)
        self.frontBlade = FrontBlade(self.carbody_view)
        self.middleBlade = MiddleBlade(self.carbody_view)
        self.steeringWheel= SteeringWheel(self.carbody_view)
        

        self.allowTurnover = False
        # car appearance specific ended


        self.joints=[] #suspensions
        self.wheels=[]     #wheels visualisation
        self.wheels_ode = []

        wheelDistance = 3.5 #1.8
        #bodyDistance = 2.2 # 1.1
        bodyDistance = 12 # 1.1
        
        bodyDistance2 = 2 # 1.1
        bodyDistance3 = 5.8 # 1.1
        for i in range(6):
            w = loader.loadModel("models/grader/wheel.egg")
            if i == 2 or i == 3  or i == 5:
                w.setHpr(90, 0, 90)
            else:
                w.setHpr(90, 180, 90)
            w.flattenLight()
            #w.setR(90)
            self.wheels.append(w)
            #self.wheels[i].setColor(1,0.5,0.5)
            #self.wheels[i].setScale(0.8)
            self.wheels[i].setQuat(Quat(0.7,0,0.7,0))
            self.wheels[i].reparentTo(render)
        self.wheels[0].setPos(self.carbody, -wheelDistance,+bodyDistance,+bodyHeight)
        self.wheels[2].setPos(self.carbody, +wheelDistance,+bodyDistance,+bodyHeight)

        self.wheels[1].setPos(self.carbody, -wheelDistance,-bodyDistance2,+bodyHeight)
        self.wheels[3].setPos(self.carbody, +wheelDistance,-bodyDistance2,+bodyHeight)

        self.wheels[4].setPos(self.carbody, -wheelDistance,-bodyDistance3,+bodyHeight)
        self.wheels[5].setPos(self.carbody, +wheelDistance,-bodyDistance3,+bodyHeight)
#        for i in range(len(self.wheels)):
#            self.wheels[i].setHpr(self.carbody.getHpr())

        for i in range(6):
            if i == 0 or i == 2:
                surfacetype = 2
            else:
                surfacetype = 1
            wheels_ode = odebase.ODEcylinder2(world, space, self.wheels[i], None, 2, 2, 1.7, 0.4, surfacetype, collidebit, catbit)
            odeworld.AddObject(wheels_ode)
            self.objects.append(wheels_ode)
            self.wheels_ode.append(wheels_ode)

            joint = OdeHinge2Joint(world)
            self.joints.append(joint)
            joint.attachBodies(self.carbody_ode.body, wheels_ode.body)
            #min/max angle for the wheel. Set min=max for stable turn
            joint.setParamHiStop(0, 0.0)
            joint.setParamLoStop(0, 0.0)

            #Error reduction parameter of suspension
            joint.setParamSuspensionERP(0, 0.6)

            #Blending of forces - in this case influences rigidity of a suspension
            joint.setParamSuspensionCFM(0, 0.02)

            #axis of joint: set one - vertical, and one - horisontal
            joint.setAxis1(0,0,1)
            joint.setAxis2(1,0,0)

        self.joints[0].setAnchor(Vec3(pos.getX()-(wheelDistance-0.2),pos.getY()+bodyDistance,pos.getZ()+bodyHeight))
        self.joints[2].setAnchor(Vec3(pos.getX()+(wheelDistance-0.2),pos.getY()+bodyDistance,pos.getZ()+bodyHeight))

        self.joints[1].setAnchor(Vec3(pos.getX()-(wheelDistance-0.2),pos.getY()-bodyDistance2,pos.getZ()+bodyHeight))
        self.joints[3].setAnchor(Vec3(pos.getX()+(wheelDistance-0.2),pos.getY()-bodyDistance2,pos.getZ()+bodyHeight))
        
        self.joints[4].setAnchor(Vec3(pos.getX()-(wheelDistance-0.2),pos.getY()-bodyDistance3,pos.getZ()+bodyHeight))
        self.joints[5].setAnchor(Vec3(pos.getX()+(wheelDistance-0.2),pos.getY()-bodyDistance3,pos.getZ()+bodyHeight))

        self.maxVelocity = 55
        self.maxSpeed=15
        self.accForce=600
        self.axis=[1,3, 4,5]
        self.axis2=[1,3,0,2, 4,5]

        self.calcGuides = []
        for i in range ( -3, 4):
            guide = NodePath(PandaNode("grader_left_guide"+str(i)))
            guide.reparentTo(self.carbody_view)
            guide.setPos(-i*2, -1, 0)
            self.calcGuides.append(guide)
        

        #self.ShowSpeedMeter()
        self.setupCamera()
        self.SetupParticle()
        self.confirmdead = False

        if odeEventHandler != None and self.odeworld.supportEvent:
            self.odeworld.setCollisionNotifier(self.carbody_ode, odeEventHandler)
            for b_ode in self.wheels_ode:
                self.odeworld.setCollisionNotifier(b_ode, odeEventHandler)

        self.audio = CarAudio1(self.carbody)

#        taskMgr.add(self.myTasks, "ode car task",  taskChain = 'paintChain')
#        taskMgr.add(self.myTasks, "ode car task")
#        taskMgr.doMethodLater(0.5,self.checkRotation, "checkRotation")

    def startEngine(self):
        taskMgr.add(self.myTasks, "ode car task")
        #taskMgr.doMethodLater(0.5,self.checkRotation, "checkRotation")
        self.audio.start()
        self.startenginetasks = Sequence(
                Wait(4.5),
                Func(self.smoke, True, True),
                Wait(4),
                Func(self.smoke, True, False))
        self.startenginetasks.start()
        
    def stopEngine(self):
        taskMgr.remove("ode car task")
        taskMgr.remove("checkRotation")
        self.audio.stopAll()

    def rev(self):
        self.audio.rev()
        
    def changeCameraMode(self, mode):
        self.cameramode = mode

    def toggleCameraMode(self):
        self.cameramode = (self.cameramode + 1) % 3


    def changeCarColor(self, color):
        return
        material = self.npBody.findMaterial("*")
        #material = Material(material)
        material.setDiffuse(color)
        material.setAmbient(color)
        self.npBody.setMaterial(material, 1)

    def changeHeadLights(self, on):
        return
        if on:
            tex = self.lightsTexture2
        else:
            tex = self.lightsTexture1
        self.lights[0].setTexture(tex,1)
        self.lights[1].setTexture(tex,1)

    def changeRearLights(self, on):
        return
        if on:
            tex = self.lightsTexture2
        else:
            tex = self.lightsTexture1
        self.lights[2].setTexture(tex,1)
        self.lights[3].setTexture(tex,1)

    def setSyncCamera(self, syncCamera):
        self.syncCamera = syncCamera

    def setCams(self, cam1, cam2, cam3):
        self.cam1 = cam1
        self.cam2 = cam2
        self.cam3 = cam3

        self.mirror1 = loader.loadModel("models/grader/mirror1.egg")
        self.mirror2 = loader.loadModel("models/grader/mirror2.egg")
        self.mirror1.reparentTo(self.body)
        self.mirror2.reparentTo(self.body)
        
        altBuffer=base.win.makeTextureBuffer("hello", 256, 256)
        self.altCam=base.makeCamera(altBuffer)
        self.altCam.reparentTo(self.body)        
        self.altCam.setPos(-2.1, 2.1, 4.7)
        self.altCam.setHpr(172, 3, 0)
        self.mirror1.setTexture(altBuffer.getTexture(),1)

        altBuffer2=base.win.makeTextureBuffer("hello2", 256, 256)
        self.altCam2=base.makeCamera(altBuffer2)
        self.altCam2.reparentTo(self.body)        
        self.altCam2.setPos(2.6, 2.1, 4.7)
        self.altCam2.setHpr(180, 0, 0)
        self.mirror2.setTexture(altBuffer2.getTexture(),1)
        
    def setupCamera(self):
        #Setup the camera basis
        self.camPosNode = self.carbody_view.attachNewNode('camPosNode')
        self.camPosNode.setPos(0,5,-2)
        self.camLookatNode = self.carbody.attachNewNode('camLookatNode')
        self.camLookatNode.setPos(0,0,2)
        self.camLookatNode2 = self.carbody.attachNewNode('camLookatNode2')
        self.camLookatNode2.setPos(0,8,3.5)
        self.camDriverNode = self.carbody_view.attachNewNode('camDriverNode')
        self.camDriverNode.setPos(CAMERA_MIDDLE_POS)
        self.camPosNode.show()
        self.camLookatNode.show()
        self.camLookatNode2.show()
        self.camDriverNode.show()
        #base.camLens.setFar(10000)


    def ShowSpeedMeter(self):
        #spedometer
        if self.pointer == None:
            self.spdm = OnscreenImage(image = '%s/spdm.png' % self.modelpath, scale=0.26, pos = (1.7, 0, -0.8))
            self.spdm.setTransparency(TransparencyAttrib.MAlpha)
            self.pointer = OnscreenImage(image = '%s/spdm_pointer.png' % self.modelpath, scale=0.26, pos = (1.7, 0, -0.8))
            self.pointer.setTransparency(TransparencyAttrib.MAlpha)
        self.lastPos = Vec3(0,0,0)
        
    def HideSpeedMeter(self):
        if self.pointer != None:
            self.spdm.destroy()
            self.pointer.destroy()
            self.pointer = None


    def forward(self):
        self.Accel(self.maxVelocity, 40.0, self.axis)

    def normal(self):
        self.Accel(0, 15.0, self.axis2)

    def releasebrake(self):
        self.normal()
        self.changeRearLights(False)


    def backward(self):
        self.Accel(-25.0, 40.0, self.axis)

    def brake(self, force=200.0):
        self.Accel(0, force, self.axis2)
        self.changeRearLights(True)

    def Destroy(self):
        if hasattr(self, "startenginetasks"):
            self.startenginetasks.finish()
        self.audio.Destroy()
        for particle in self.particles:
            particle.disable()
            particle.cleanup()
        taskMgr.remove("ode car task")
        #taskMgr.remove("checkRotation")
        for joint in self.joints:
            joint.detach()
            joint.destroy()
        for b_ode in self.objects:
            self.odeworld.RemoveObject(b_ode)
            b_ode.destroy()
        self.objects = []
        self.HideSpeedMeter()
        
    def myTasks(self, task):
        self.TurnTask(task)
        if not self.confirmdead:
            self.JetTask(task)
            self.checkRotation(task)
            if self.IsDead():
                self.brake()
                self.confirmdead = True
                #self.releasebrake()
                self.cameramode = self.CAMERA_DEFAULT_MODE
                #self.smoke(False, True)
        else:
            self.audio.setState(True, 0, False, 0)
        self.Sync()
        return task.cont

    #def addCamdist(self, v):
    #  self.camDistance += v

    def steer(self, axis_value):
        self.turnangle = axis_value * 0.5
        self.turnangle_fixed = True
         
    def setGear(self, gear):
        if (self.gear <> gear): 
            self.brake2(1.0)
        self.gear = gear
		
    def accelerate(self, axis_value):
        #print "accelerate", `axis_value`
        for i in [1,3,0,2, 4,5]:
            self.joints[i].setParamFMax(1, 0)
            
        if self.gear == GEAR_FORWARD:
            self.acceleration=True
            self.stoppingforce = 0
            self.accForce = axis_value * 300;
        else:
            self.acceleration=False
            self.stoppingforce = axis_value * 40
            aspect = -25
            for i in self.axis:
                #set angular engine speed
                self.joints[i].setParamVel(1,aspect*self.carOrientation)
                #and force to it
                self.joints[i].setParamFMax(1, self.stoppingforce)
        
    def brake2(self, axis_value):
        for i in [1,3,0,2, 4,5]:
            self.joints[i].setParamFMax(1, 0)
        aspect = 0
        force = 200*axis_value+10
        axis = self.axis2
        
        self.acceleration=False
        self.stoppingforce = force
        for i in axis:
            #set angular engine speed
            self.joints[i].setParamVel(1,aspect*self.carOrientation)
            #and force to it
            self.joints[i].setParamFMax(1, force)
        
    def Accel(self, aspect, force, axis):
        if not self.allowTurnover and self.carOrientation < 0:
            self.acceleration = False
            return
        dt = globalClock.getDt()
        #force = force * dt ** 2
        for i in [1,3,0,2, 4,5]:
            self.joints[i].setParamFMax(1, 0)
        #We use two different methods for move forward and backward
        #Forward - "jet engine" - add force to the body of the car
        #Backward - angular engine - add angular speed to the wheels
        if aspect>0:
            self.acceleration=True
            self.stoppingforce = 0
        else:
            self.acceleration=False
            self.stoppingforce = force
            for i in axis:
                #set angular engine speed
                self.joints[i].setParamVel(1,aspect*self.carOrientation)
                #and force to it
                self.joints[i].setParamFMax(1, force)

    #check car orientation, and change control according to it
    def checkRotation(self,task):
        oldO=self.carOrientation
        if abs(int(self.carbody.getR()))<90:
            self.carOrientation=1
        else:
            self.carOrientation=-1
        if oldO != self.carOrientation:
            self.camPosNode.setZ(-self.camPosNode.getZ())
            if self.allowTurnover:
                for i in [1,3,0,2, 4,5]:
                    self.joints[i].setParamVel(1,-self.joints[i].getParamVel(1))

        return task.again

    #turn wheels - set variables
    def Turn(self,enabled,aspect):
        self.turn=enabled
        self.turnspeed=aspect
        self.turnangle_fixed = False
        
    #immediately, turn wheels here
    def TurnTask(self,task):
        #calculate angle
        #print `(self.acceleration, self.turnspeed)`
        if not self.turnangle_fixed:
            if not self.turn:
                if self.turnangle>0.01:
                    self.turnspeed=-0.01*self.carOrientation
                elif self.turnangle<-0.01:
                    self.turnspeed=0.01*self.carOrientation
                else:
                    self.turnspeed=0
                    self.turnangle=0;
            self.turnangle=self.turnangle+self.turnspeed*self.carOrientation
        if self.turnangle>0.5:
            self.turnangle=0.5
        if self.turnangle<-0.5:
            self.turnangle=-0.5
        # and set angle to the front wheels
        self.joints[0].setParamHiStop(0, self.turnangle)
        self.joints[0].setParamLoStop(0, self.turnangle)
        self.joints[2].setParamHiStop(0, self.turnangle)
        self.joints[2].setParamLoStop(0, self.turnangle)
        #print `self.turnangle`
        
        self.frontWheels.steer(-self.turnangle*90)
        self.steeringWheel.turn(-self.turnangle*90)
        
        # will fix wheel position a bit better
        for i in xrange(6):
          self.wheels_ode[i].body.setFiniteRotationAxis(self.joints[i].getAxis2())
        return task.cont

    #task for jet engeene
    def JetTask(self,task):
        dir = self.carbody.getMat().getRow3(1)
        body = self.carbody_ode.body
        v = body.getLinearVel()
        fSameDirection = (dir.dot(v) >= 0)
        vl = v.length()
        self.audio.setState(self.confirmdead, vl, self.acceleration, self.stoppingforce)
        if self.acceleration:
            #print "JetTask:", self.acceleration, vl, self.maxSpeed, self.accForce, self.stoppingforce
            if self.maxSpeed > vl:
                body.addRelForce(0,self.accForce,0)
                if vl < 20 and fSameDirection:
                #if vl < 20:
                    self.smoke(True, True)
                    return task.cont
            elif self.maxSpeed*1.5 < vl:
                print "JetTask:", self.acceleration, vl, self.maxSpeed, self.accForce, self.stoppingforce
                diff = vl - self.maxSpeed 
                body.addRelForce(0,-200*diff,0)
#        else:
#            self.normal()
        self.smoke(True, False)
        return task.cont

    def IsDead(self):
        if not self.allowTurnover and self.carOrientation < 0:
            body = self.carbody_ode.body
            v = body.getLinearVel().length()
            if v < 0.1:
                return True
        return False

    def middleBladeMove(self, axis, value):
        self.middleBlade.setMove(axis, value)
        
    def frontBladeMove(self, axis, value):
        self.frontBlade.setMove(axis, value)
        
        
    def Sync(self):
        #self.odeworld.simulationTask3(Task)
        # update the camera
        if self.syncCamera:
            """
            body = self.carbody_ode.body
            camVec = self.camPosNode.getPos(render) - body.getPosition()

            if self.cameramode == self.CAMERA_DRIVER_MODE:
                camLookat = self.camLookatNode2.getPos(render)
                targetCamPos = self.camDriverNode.getPos(render)
            else:
                if self.cameramode == self.CAMERA_DEFAULT_MODE:
                    camDistance = Vec2(-5, 0)
                else:
                    camDistance = Vec2(-5, -2)
                targetCamPos = body.getPosition() + camVec * camDistance.getX() + Vec3(0,0,camDistance.getY())
                camLookat = self.camLookatNode.getPos(render)

                if self.cameramode == self.CAMERA_DEFAULT_MODE:
                    dPos = targetCamPos - self.cam2.getPos(render)
                    dt = globalClock.getDt()
                    #print targetCamPos, dPos, dt
                    delta = dPos * dt * 2
                    if delta.length() > 10:
                        delta *= delta.length() / 10
                    targetCamPos = (self.cam2.getPos(render) + delta)
            if targetCamPos.getZ() < 1:
                targetCamPos.setZ(1)
            self.cam2.setPos(targetCamPos)
            self.cam2.lookAt(camLookat)
            """
            self.cam1.setPos(self.carbody_view, CAMERA_LEFT_POS)
            self.cam3.setPos(self.carbody_view, CAMERA_RIGHT_POS)
            self.cam1.setHpr(self.carbody_view, (CAMERA_LEFT_HPR))
            self.cam3.setHpr(self.carbody_view, (CAMERA_RIGHT_HPR))
            self.cam2.setPos(self.carbody_view, (CAMERA_MIDDLE_POS))
            self.cam2.setHpr(self.carbody_view, (CAMERA_MIDDLE_HPR))

        # the speedometer pointer
        curPos = self.carbody.getPos(render)
        vel = (self.lastPos - curPos).length() /globalClock.getDt()*2
        self.speedHistory.append(vel)
        avgVel = sum(self.speedHistory) / len(self.speedHistory)
        #print 'vel:', vel
        self.moved = ((self.lastPos - curPos).length()  > 0.01)
        #print 'moved', (self.lastPos - curPos).length()
        #if self.moved:
        self.lastPos = curPos
        if self.pointer != None:
            self.pointer.setR(avgVel*4-20)

    def SyncSideCameras(self):
        self.cam1.setPos(self.carbody_view, CAMERA_LEFT_POS)
        self.cam3.setPos(self.carbody_view, CAMERA_RIGHT_POS)
        self.cam1.setHpr(self.carbody_view, (CAMERA_LEFT_HPR))
        self.cam3.setHpr(self.carbody_view, (CAMERA_RIGHT_HPR))
            
    def SetupParticle(self):
        particleRenderNode = render.attachNewNode("smokeNode")
        self.particles = []
        for i in range(1):
            particle = ParticleEffect()
            self.particles.append(particle)
            if i == 2:
                particle.loadConfig(Filename("particles/steam.ptf"))
            else:
                particle.loadConfig(Filename("particles/smoke2.ptf"))
            p0 = particle.getParticlesNamed('particles-1')
            p0.setBirthRate(100000)
            if i < 2:
                particle.start(self.npTubes[i], particleRenderNode)
            else:
                particle.start(self.carbody, particleRenderNode)
        particleRenderNode.setBin('fixed', 0)
        particleRenderNode.setDepthWrite(False)

    def smoke(self, tube, on):
        if tube:
            l  = [0]
        else:
            l = [2]
        if on:
            #h = (self.actor.neck.getR()) / 180 * math.pi
            h = 0
            for i in l:
                particle = self.particles[i]
                p0 = particle.getParticlesNamed('particles-1')
                p0.setBirthRate(0.3 + 0.2 * random.random())
                emitter = p0.getEmitter()
                v = 1
                emitter.setExplicitLaunchVector(Vec3(v * math.sin(h), -v * math.cos(h), 12.0000))
        else:
            for i in l:
                particle = self.particles[i]
                p0 = particle.getParticlesNamed('particles-1')
                p0.setBirthRate(100000.0)

    def stop(self):
        self.brake()
        
    def resetTrack(self):
        self.frontBlade.stopPaint()
        self.middleBlade.stopPaint()
        self.frontWheels.stopPaint()
        
    def reset(self):
        self.frontBlade.reset()
        self.middleBlade.reset()
        
    def reset2(self):
        self.frontBlade.reset2()
        self.middleBlade.reset2()
	
    
    def setPosQuat(self, pos, quat, wheels):
        self.carbody_ode.geom.setPosition(pos)
        self.carbody_ode.geom.setQuaternion(quat)
        self.carbody_ode.body.setLinearVel(0)
        self.carbody_ode.body.setAngularVel(0)
        print "setPosQuat: "+`self.carbody_ode.geom`
        for i in range(6):
            self.wheels_ode[i].geom.setPosition(wheels[i][0])
            self.wheels_ode[i].geom.setQuaternion(wheels[i][1])
            self.wheels_ode[i].body.setLinearVel(0)
            self.wheels_ode[i].body.setAngularVel(0)
        
        self.joints[0].setParamHiStop(0, self.turnangle)
        self.joints[0].setParamLoStop(0, self.turnangle)
        self.joints[2].setParamHiStop(0, self.turnangle)
        self.joints[2].setParamLoStop(0, self.turnangle)
        self.stop()
        pass
        
    def hasMoved(self):
        return True
        ret = self.moved
#        self.moved = False
        return ret
        
    def paintGround(self, ground):
        self.frontWheels.paintGround(ground)
        self.frontBlade.paintGround(ground)
        self.middleBlade.paintGround(ground)
        
    def calcProgress(self, ground):
        ground.calcProgress(self.calcGuides)
        
    def bladeInGround(self):
        return self.frontBlade.bladeInGround() or self.middleBlade.bladeInGround()
        
    def bladeTooUp(self):
        return self.frontBlade.bladeTooUp() or self.middleBlade.bladeTooUp()

from direct.showbase.Audio3DManager import Audio3DManager
from pandac.PandaModules import AudioManager
class CarAudio1():
    STATE_START = 1
    STATE_READY = 2
    STATE_RUN = 3
    STATE_DEAD = 4
    def __init__(self, car, f3D=False):
        self.f3D = f3D
        self.car = car
        self.start0_sound = loader.loadSfx("audio/startengine0_11025.wav")
        self.start1_sound = loader.loadSfx("audio/startengine1_11025.wav")
        self.start1_sound.setLoop(1)
        self.run_sound = loader.loadSfx("audio/enginerun_11025.wav")
        self.run_sound.setLoop(1)
        self.normal_sound = loader.loadSfx("audio/enginenormal_11025.wav")
        self.normal_sound.setLoop(1)
        self.brake_sound = loader.loadSfx("audio/brake_11025.wav")
        self.brake_sound.setLoop(1)
        self.horn_sound = loader.loadSfx("audio/bushorn.wav")
        self.horn_sound.setLoop(1)
        
        self.blade_sound = loader.loadSfx("audio/sahad.wav")
        self.blade_sound.setLoop(1)
        
        self.crash_sound = loader.loadSfx("audio/crash.mp3")
        
        self.rev_sound = loader.loadSfx("audio/rev_11025.wav")
        self.audioMgr = base.sfxManagerList[0]
        #self.audioMgr.audio3dSetDropOffFactor(5)
        if self.f3D:
            self.audio3d = Audio3DManager(self.audioMgr, camera)
            #self.audio3d.setDropOffFactor( 10 )
            #self.audio3d.attachSoundToObject(self.start0_sound, self.car)
            self.audio3d.attachSoundToObject(self.start1_sound, self.car)
            self.audio3d.attachSoundToObject(self.normal_sound, self.car)
            self.audio3d.attachSoundToObject(self.run_sound, self.car)
            self.audio3d.attachSoundToObject(self.brake_sound, self.car)
        self.state = self.STATE_START
        self.tasks = Sequence(
            Func(self.start0_sound.play),
            Wait(self.start0_sound.length()),
            Func(self.ready))

    def stopAll(self):
        print "CarAudio1.stopAll"
        self.start0_sound.stop()
        self.start1_sound.stop()
        self.run_sound.stop()
        self.normal_sound.stop()
        self.brake_sound.stop()
        self.brake_sound_playing = False
        self.rev_sound.stop()
        self.horn_sound.stop()

    def crash(self):
        self.crash_sound.play()
        
    def start(self):
        self.stopAll()
        self.tasks.start()

    def rev(self):
        self.rev_sound.play()
        
    def horn(self, play=True):
        if play:
            self.horn_sound.play()
        else:
            self.horn_sound.stop()
        
    def blade(self, play=True):
        if play:
            self.blade_sound.play()
        else:
            self.blade_sound.stop()

    def ready(self):
 #       print "CarAudio1.ready"
        if self.state != self.STATE_READY:
            self.stopAll()
            self.state = self.STATE_READY
            self.start1_sound.setVolume(0.8)
            self.start1_sound.play()

    def dead(self):
        if self.state != self.STATE_DEAD:
            self.stopAll()
            self.state = self.STATE_DEAD

    def run(self, speed, acceleration, stoppingforce):
        r = min(speed/100,1)

        minrate = 0.5
        pr = minrate + r * (1.5-minrate)
        self.normal_sound.setPlayRate(pr)

        minv = 0.1
        v = minv + r * (1-minv)
        self.normal_sound.setVolume(v)

        if self.state != self.STATE_RUN:
            self.acceleration = False
            self.start1_sound.stop()
            self.normal_sound.play()
            self.state = self.STATE_RUN

        if False:
            if self.acceleration != acceleration:
                if acceleration:
                    self.acceleration = acceleration
                    self.run_sound.play()
                    self.run_sound.setVolume(v)
                else:
                    vold = self.run_sound.getVolume()
                    if vold < 0.1:
                        self.acceleration = acceleration
                        self.run_sound.stop()
                    else:
                        self.run_sound.setVolume(vold - 0.05)

        if not acceleration and speed > 1 and stoppingforce > 20:
            v = r * (stoppingforce-20) / 100
            if v < 0.1:
                if self.brake_sound_playing:
                    self.brake_sound.stop()
                    self.brake_sound_playing = False
            else:
                if not self.brake_sound_playing:
                    #self.brake_sound.play()
                    self.brake_sound_playing = True
                v = min(v*2,1)
                self.brake_sound.setVolume(v)
        elif self.brake_sound_playing:
            self.brake_sound.stop()
            self.brake_sound_playing = False


    def setState(self, isdead, speed, acceleration, stoppingforce):
#        print "CarAudio1.setState"
        if self.state != self.STATE_START:
            if isdead:
                self.dead()
            elif speed > 0.5:
                self.run(speed, acceleration, stoppingforce)
            else:
                self.ready()
        self.update()

    def Destroy(self):
        self.tasks.finish()
        if self.f3D:
            #self.audio3d.detachSound(self.start0_sound)
            self.audio3d.detachSound(self.start1_sound)
            self.audio3d.detachSound(self.normal_sound)
            self.audio3d.detachSound(self.run_sound)
            self.audio3d.detachSound(self.brake_sound)
        self.stopAll()
        #self.audioMgr.stopAllSounds()

    def update(self):
        if self.f3D:
            self.audio3d.update()

            
