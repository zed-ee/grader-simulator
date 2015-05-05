import math
from pandac.PandaModules import NodePath,PandaNode
from pandac.PandaModules import Vec2,Vec3,Vec4,BitMask32
from Config import *
from Damper import Damper

class MiddleBlade:
    def __init__(self, parent):

        self.bladeBeam = loader.loadModel("models/grader/middleblade-arm")
        self.bladeBeam.reparentTo(parent)
        self.bladeBeam.setPos(0, -8.5, 2.9)
        
        self.bladeRing = loader.loadModel("models/grader/middleblade-ring")
        self.bladeRing.reparentTo(self.bladeBeam)
        self.bladeRing.setPos(0, 4.8, -0.02)
        self.blade = loader.loadModel("models/grader/middleblade-blade")
        self.blade.reparentTo(self.bladeRing)
        self.blade.setPos(0, 0.25, -1.8)

        self.leftDamper = Damper( (parent, "middleblade-damper3-top.egg", (1.7, -3.8, 5.8)), (self.bladeBeam, "middleblade-damper-piston.egg", (2.3, 4.9, -0.1)))
        self.rightDamper = Damper( (parent, "middleblade-damper3-top.egg", (-1.7, -3.8, 5.8)), (self.bladeBeam, "middleblade-damper-piston.egg", (-2.3, 4.9, -0.1)))
        self.middleDamper = Damper( (parent, "middleblade-damper3-top.egg", (0, -2.6, 4.5)), (self.bladeBeam, "middleblade-damper-piston.egg", (2.3, 5.1, -0.1)))
        #self.rightDamper.up.setR(180)
        #self.bladeBeam.lookAt(self.bladeDampers)
        self.axes = [0, 0]
        taskMgr.add(self.animateTask,"middleBladeTask")

        self.guides = []
        self.guidesOldPos = []
        """
        for i in range(-1, 2):
            if i != 0:
                np =loader.loadModel("box")#NodePath(PandaNode("middle-guide-outer"+str(i)))            
                np.reparentTo(self.blade)
                np.setPos(i*6, 0, -2)
                self.guides.append(np)
                self.guidesOldPos.append(None)
            
        for i in range(-4, 5):
            np =loader.loadModel("box")#NodePath(PandaNode("middle-guide"+str(i)))            
            np.reparentTo(self.blade)
            np.setPos(i, -0.2, -2)
            self.guides.append(np)
            self.guidesOldPos.append(None)
        """
        self.leftGuide2 = NodePath(PandaNode("left_guide"))
        self.leftGuide2.reparentTo(self.blade)
        self.leftGuide2.setPos(-5, -3, -1)
        self.rightGuide2 = NodePath(PandaNode("right_guide"))
        self.rightGuide2.reparentTo(self.blade)
        self.rightGuide2.setPos(5, -3, -1)

        self.leftGuide3 = NodePath(PandaNode("left_guide2"))
        self.leftGuide3.reparentTo(self.blade)
        self.leftGuide3.setPos(-4, -1, -1.5)
        self.rightGuide3 = NodePath(PandaNode("right_guide2"))
        self.rightGuide3.reparentTo(self.blade)
        self.rightGuide3.setPos(4, -1, -1.5)

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
            self.moveLeft()
        elif self.axes[0] > 0.01:
            self.moveRight()
        return task.cont
            
    def riseUp(self):
        if (self.bladeBeam.getP() < MIDDLEBLADE_UPPER_POS):
            elapsed = globalClock.getDt()
            #print self.bladeBeam.getP()
            self.bladeBeam.setP(self.bladeBeam, elapsed * 10)
            print `(-self.bladeBeam.getP()*2, self.bladeBeam.getP())`
            self.blade.setP(-self.bladeBeam.getP()*2 +22)
            self.updateDampers()

    def lowerDown(self):
        if (self.bladeBeam.getP() > MIDDLEBLADE_LOWER_POS):
            #print self.bladeBeam.getP()
            elapsed = globalClock.getDt()
            self.bladeBeam.setP(self.bladeBeam, -elapsed *  10)
            print `(-self.bladeBeam.getP()*2, self.bladeBeam.getP())`
            self.blade.setP(-self.bladeBeam.getP()*2  +22)
            self.updateDampers()
            
    def bladeInGround(self):
        return self.bladeBeam.getP() <= MIDDLEBLADE_LOWER_POS
        
    def bladeTooUp(self):
        return self.bladeBeam.getP() > 12
        
    def moveLeft(self):
        elapsed = globalClock.getDt()
        if self.blade.getX() > 0:
            self.blade.setX(self.blade, -elapsed)
        elif (self.bladeBeam.getH() < MIDDLEBLADE_MAX_TILT):
            #print self.bladeBeam.getH()
            self.bladeBeam.setH(self.bladeBeam, elapsed * MIDDLEBLADE_UPPER_POS)
            self.bladeRing.setH(-self.bladeBeam.getH()*2)
            self.updateDampers()
        elif self.blade.getX() > -2:
            self.blade.setX(self.blade, -elapsed)            

    def moveRight(self):
        elapsed = globalClock.getDt()
        if self.blade.getX() < 0:
            self.blade.setX(self.blade, elapsed)
        elif (self.bladeBeam.getH() > -MIDDLEBLADE_MAX_TILT):
            #print self.bladeBeam.getH()
            self.bladeBeam.setH(self.bladeBeam, -elapsed * MIDDLEBLADE_UPPER_POS)
            self.bladeRing.setH(-self.bladeBeam.getH()*2)
            self.updateDampers()
        elif self.blade.getX() < 2:
            self.blade.setX(self.blade, elapsed)            

    def bladeTooStraight(self):
        return -2 < self.bladeBeam.getH() < 2
        
    def rotateLeft(self):
        if (self.bladeRing.getH() < MIDDLEBLADE_MAXROTATION):
            #print self.bladeRing.getH()
            elapsed = globalClock.getDt()
            self.bladeRing.setH(self.bladeRing, elapsed * MIDDLEBLADE_ROTATION_SPEED)


    def rotateRight(self):
        if (self.bladeRing.getH() > -MIDDLEBLADE_MAXROTATION):
            #print self.bladeRing.getH()
            elapsed = globalClock.getDt()
            self.bladeRing.setH(self.bladeRing, - elapsed * MIDDLEBLADE_ROTATION_SPEED)
            
    def reset(self):
        self.blade.setX(0)
        self.bladeBeam.setH(0)
        self.bladeRing.setH(0)
        self.bladeBeam.setP(MIDDLEBLADE_UPPER_POS)
        self.blade.setP(-self.bladeBeam.getP()*2  +22)
        self.updateDampers()
        
    def reset2(self):
        self.blade.setX(0)
        self.bladeBeam.setH(MIDDLEBLADE_MAX_TILT)
        self.bladeRing.setH(-MIDDLEBLADE_MAX_TILT*2)
        self.bladeBeam.setP(6)
        self.blade.setP(-self.bladeBeam.getP()*2  +22)
        self.updateDampers()
        
    def paintGround(self, ground):
        #ground.paint(self.leftGuide2.getPos(render), self.leftGuide2.getPos(render), Vec3(1, 0, 0) )
        #return
        ground.paint(self.leftGuide2.getPos(render), self.rightGuide2.getPos(render), Vec3(1, 0, 0) )
        a = (self.bladeRing.getH() / MIDDLEBLADE_MAX_TILT) # -1...1
        a1 = abs((a / 2) + 0.5)
        a2 = abs((a / 2) - 0.5)
        ground.paint(self.leftGuide3.getPos(render), self.rightGuide3.getPos(render), Vec3(0, 0, 1) )
        """
        for x in range(len(self.guides)):
            pos = self.guides[x].getPos(render)
            if self.guidesOldPos[x] != None:
                oldpos = self.guidesOldPos[x]
                if x == 0:
                    c = Vec3(1, a1, 1)
                elif  x == 1:
                    c = Vec3(1, a2, 1)
                else:
                    c = Vec3(0, 1, 1)
                ground.paint(self.leftGuide2.getPos(render), self.rightGuide2.getPos(render), c)
            self.guidesOldPos[x] = pos
        """        
                
        
    def paintGroundOld(self, ground):
        b = (self.bladeBeam.getP() - MIDDLEBLADE_LOWER_POS) / (MIDDLEBLADE_UPPER_POS - MIDDLEBLADE_LOWER_POS) # 0...1
        #b = b *0.4+0.55 # 0.3 ... 0.7
        a = (self.bladeRing.getH() / MIDDLEBLADE_MAX_TILT) / 4 + 0.5
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
                    h = 1 - b
                ground.paintFrontBlade(oldpos, pos, h)
            self.guidesOldPos[x] = pos
            
    def stopPaint(self):
        for x in range(len(self.guides)):
            self.guidesOldPos[x] = None
