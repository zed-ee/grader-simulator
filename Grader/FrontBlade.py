import math
from pandac.PandaModules import NodePath,PandaNode
from pandac.PandaModules import Vec2,Vec3,Vec4,BitMask32
from Config import *
from Utils import *
from Damper import Damper

class FrontBlade:
    def __init__(self, parent):
        self.parent = parent
        self.lowArm = loader.loadModel("models/grader/frontblade-lower-arm")
        self.lowArm.reparentTo(parent)
        self.lowArm.setPos(0, -10.74, 1.28)

        self.upArm = loader.loadModel("models/grader/frontblade-upper-arm")
        self.upArm.reparentTo(parent)
        self.upArm.setPos(0, -10.74, 2.5)

        self.bladeAnchor = NodePath(PandaNode("block_pos"))
        self.bladeAnchor.reparentTo(parent)
        self.bladeAnchor.setPos(0, -12.5, 1.5)

        self.block = loader.loadModel("models/grader/frontblade-block")
        self.block.reparentTo(self.bladeAnchor)
        #self.block.setPos(0, -12.5, 2.15)

        self.lowArmLook = NodePath(PandaNode("low_arm_look"))
        self.lowArmLook.reparentTo(self.block)
        self.lowArmLook.setPos(0,-0.06,-0.2)
        self.upArmLook = NodePath(PandaNode("up_arm_look"))
        self.upArmLook.reparentTo(self.block)
        self.upArmLook.setPos(0,-0.28,0.8)
        
        self.blade = loader.loadModel("models/grader/frontblade-blade")
        self.blade.reparentTo(self.block)
        self.blade.setPos(0, -0.74, 0.3)

        self.leftDamper = Damper( (self.block, "frontblade-damper2-top.egg", (0.9, -0.1, 0.5)), (self.blade, "frontblade-damper2-piston.egg", (3.3, 0, 0.1)))
        self.rightDamper = Damper( (self.block, "frontblade-damper2-top.egg", (-0.9, -0.1, 0.5)), (self.blade, "frontblade-damper2-piston.egg", (-3.3, 0, 0.1)))
        self.middleDamper = Damper( (parent, "frontblade-damper1-top.egg", (0, -10.8, 3.45)), (self.block, "frontblade-damper1-piston.egg", (0, -0.03, 0.1)))


        self.upArm.lookAt(self.upArmLook)
        self.lowArm.lookAt(self.lowArmLook)
        self.guides = []
        self.guidesOldPos = []

        for i in range(-1, 2):
            if i != 0:
                np =NodePath(PandaNode("guide-outer"+str(i)))            
                np.reparentTo(self.blade)
                np.setPos(i*6, 0.5, 0)            
                self.guides.append(np)
                self.guidesOldPos.append(None)
            
        for i in range(-4, 5):
            np =NodePath(PandaNode("guide"+str(i)))            
            np.reparentTo(self.blade)
            np.setPos(i, -0.2, 0)            
            self.guides.append(np)
            self.guidesOldPos.append(None)

            
        self.leftGuide2 = NodePath(PandaNode("front-left_guide"))
        self.leftGuide2.reparentTo(self.blade)
        self.leftGuide2.setPos(-4.5, -1, -1)
        self.rightGuide2 = NodePath(PandaNode("front-right_guide"))
        self.rightGuide2.reparentTo(self.blade)
        self.rightGuide2.setPos(4.5, -1, -1)

        self.leftGuide3 = NodePath(PandaNode("front-left_guide2"))
        self.leftGuide3.reparentTo(self.blade)
        self.leftGuide3.setPos(-4, -0, -1.5)
        self.rightGuide3 = NodePath(PandaNode("front-right_guide2"))
        self.rightGuide3.reparentTo(self.blade)
        self.rightGuide3.setPos(4, -0, -1.5)
               
        self.axes = [0, 0]
        
        taskMgr.add(self.animateTask,"frontBladeTask")

    def updateDampers(self):
        self.leftDamper.update()
        self.rightDamper.update()
        self.middleDamper.update()

    def setMove(self, axis, value):
        self.axes[axis] = value
        
    def animateTask(self, task):
        if self.axes[1] < -0.01:
            self.lowerDown()
        elif self.axes[1] > 0.01:
            self.riseUp()
            
        if self.axes[0] < -0.01:
            self.turnLeft()
        elif self.axes[0] > 0.01:
            self.turnRight()
        return task.cont
        
        
    def riseUp(self):
        if (self.block.getZ() < 0.7):
            #print self.block.getZ()
            elapsed = globalClock.getDt()
            newZ = self.block.getZ()+elapsed * FRONTBLADE_UPDOWN_SPEED
            self.block.setZ(min(0.7, newZ))
            self.block.setY((1-math.cos(self.block.getZ()/math.pi))*5)
            self.upArm.lookAt(self.upArmLook)
            self.lowArm.lookAt(self.lowArmLook)
            self.updateDampers()


    def lowerDown(self):
        if (self.block.getZ() > -0.8):
            #print self.block.getZ()
            elapsed = globalClock.getDt()
            newZ = self.block.getZ()-elapsed * FRONTBLADE_UPDOWN_SPEED
            self.block.setZ(max(-0.8, newZ))
            self.block.setY((1-math.cos(self.block.getZ()/math.pi))*5)
            self.upArm.lookAt(self.upArmLook)
            self.lowArm.lookAt(self.lowArmLook)
            self.updateDampers()

    def bladeInGround(self):
        return self.block.getZ() <= -0.8
        
    def bladeTooUp(self):
        return self.block.getZ() > 0.2
        
    def turnLeft(self):
        if (self.blade.getH() < FRONTLADE_MAXROTATION):
            elapsed = globalClock.getDt()
            self.blade.setH(self.blade, elapsed * FRONTLADE_MAXROTATION)
            self.updateDampers()


    def turnRight(self):
        if (self.blade.getH() > -FRONTLADE_MAXROTATION):
            elapsed = globalClock.getDt()
            self.blade.setH(self.blade, - elapsed * FRONTLADE_MAXROTATION)
            self.updateDampers()
            
    def bladeTooStraight(self):
        return -2 < self.blade.getH() < 2

    def reset(self):
        self.blade.setH(0)
        self.block.setZ(0.7)
        self.block.setY((1-math.cos(self.block.getZ()/math.pi))*5)
        self.upArm.lookAt(self.upArmLook)
        self.lowArm.lookAt(self.lowArmLook)
        self.updateDampers()
		
    def reset2(self):
        self.blade.setH(0)
        self.block.setZ(-0.4)
        self.block.setY((1-math.cos(self.block.getZ()/math.pi))*5)
        self.upArm.lookAt(self.upArmLook)
        self.lowArm.lookAt(self.lowArmLook)
        self.updateDampers()
		
    def paintGround(self, ground):
        ground.paint(self.leftGuide2.getPos(render), self.rightGuide2.getPos(render), Vec3(1, 0, 0) )
        a = (self.blade.getH() / FRONTLADE_MAXROTATION) # -1...1
        a1 = abs((a / 2) + 0.5)
        a2 = abs((a / 2) - 0.5)
        ground.paint(self.leftGuide3.getPos(render), self.rightGuide3.getPos(render), Vec3(0, 0, 1) )
        
        """
        b = (self.block.getZ() + 0.5) /1.2  # -0.5...0.7 -> 0...1
        b = b *0.4+0.7
        # 0.3 ... 0.7
        a = (self.blade.getH() /FRONTLADE_MAXROTATION)/2 + 0.5
        #print a
        h = -1 + b
        #print "a, b, h:", a, b, h
        ground.paintFrontBlade(self.leftGuide2.getPos(render), self.rightGuide2.getPos(render), h)
        
        for x in range(len(self.guides)):
            pos = self.guides[x].getPos(render)
            if self.guidesOldPos[x] != None:
                oldpos = self.guidesOldPos[x]
                if x == 0:
                    h = (-1 + b) * (1-a)
                elif x == 1:
                    h = (-1 + b) * (a)
                else:
                    h = 1-b
                ground.paintFrontBlade(oldpos, pos, h)
            self.guidesOldPos[x] = pos
        """

    def stopPaint(self):
        for x in range(len(self.guides)):
            self.guidesOldPos[x] = None
