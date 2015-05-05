from direct.actor.Actor import Actor
from pandac.PandaModules import CollisionTraverser,CollisionNode
from pandac.PandaModules import CollisionHandlerQueue,CollisionRay
from pandac.PandaModules import CollisionHandlerFloor
from pandac.PandaModules import Vec3,Vec4,BitMask32

import math

from Config import *
from FrontWheels import *
from BackWheels import *
from SteeringWheel import *
from MiddleBlade import *
from FrontBlade import *
from pandac.PandaModules import OdeBody, OdeMass, Quat, OdeBoxGeom

class Grader:
    speed = 0
    
    def __init__(self, parent, collisionTraverser, odeWorld, odeSpace):
        self.lastZPos = ()
        self.speed = 0;
        self.acceleration = 0
        self.direction = FORWARD
        self.moved = False
        self.bodyBox = loader.loadModel("models/grader/body-box")
        self.bodyBox.setScale(self.getScale())
        self.bodyBox.reparentTo(parent)
        self.bodyBox.setPos(GRADER_START_POS)
        self.bodyBox.setHpr(GRADER_START_HPR)
        
        self.odeBody = OdeBody(odeWorld)
        M = OdeMass()
        M.setBox(50, 1, 1, 1)
        self.odeBody.setMass(M)
        self.odeBody.setPosition(self.bodyBox.getPos(render))
        self.odeBody.setQuaternion(self.bodyBox.getQuat(render))
        # Create a BoxGeom
        self.geom = OdeBoxGeom(odeSpace, 1, 1, 1)
        self.geom.setCollideBits(BitMask32(3))
        self.geom.setCategoryBits(BitMask32(4))
        self.geom.setBody(self.odeBody)
        """
        boundingBox, offset=getOBB(self.bodyBox)
        self.geom = OdeBoxGeom(odeSpace, *boundingBox)
        print `self.geom`
        self.odeBody = OdeBody(odeWorld)
        M = OdeMass()
        M.setBox(4, *boundingBox)
        self.odeBody.setMass(M)
        self.geom.setBody(self.odeBody)
        mass = M.getMagnitude()
        # synchronize ODE geom's transformation according to the real object's
        self.geom.setPosition(self.bodyBox.getPos(render))
        self.geom.setQuaternion(self.bodyBox.getQuat(render))

        #self.geom.getSpace().setSurfaceType(self.geom, 0)
        self.geom.setCollideBits(BitMask32(0x00000002))
        self.geom.setCategoryBits(BitMask32(0x00000001))
        """
        
        self.body =  loader.loadModel("models/grader/body")
        #self.body.setScale(self.getScale())
        self.body.reparentTo(self.bodyBox)
        self.body.setPos(0, -6, -2.5)

        self.controlPanel= loader.loadModel("models/grader/control-panel")
        self.controlPanel.reparentTo(self.body)
        self.controlPanel.flattenLight()

        self.steeringWheel= SteeringWheel(self.body)

        self.frontWheels = FrontWheels(self.body, self.odeBody, odeWorld, odeSpace)
        self.backWheels = BackWheels(self.body, self.odeBody, odeWorld, odeSpace)
        self.frontBlade = FrontBlade(self.body)
        self.middleBlade = MiddleBlade(self.body)
        self.lastZPos = ((self.body.getZ(render), self.frontWheels.leftWheel.wheel.getZ(render), self.frontWheels.rightWheel.wheel.getZ(render)))

        
        """
        self.backWheels = loader.loadModel("models/grader/backwheels")
        self.backWheels.reparentTo(self.body)

        
        """
        """
        fromObject = self.body.attachNewNode(CollisionNode('colNode'))
        fromObject.node().addSolid(CollisionRay(0, 0, 0, 0, 0, -1))

        lifter = CollisionHandlerFloor()
        lifter.addCollider(fromObject, self.body)
        """
        self.cTrav =  CollisionTraverser()

        self.bodyGroundRay = CollisionRay()
        self.bodyGroundRay.setOrigin(0, 0,1000)
        self.bodyGroundRay.setDirection(0,0,-1)
        self.bodyGroundCol = CollisionNode('bodyRay')
        self.bodyGroundCol.addSolid(self.bodyGroundRay)
        self.bodyGroundCol.setFromCollideMask(BitMask32.bit(0))
        self.bodyGroundCol.setIntoCollideMask(BitMask32.allOff())
        self.bodyGroundColNp = self.body.attachNewNode(self.bodyGroundCol)
        self.bodyGroundHandler = CollisionHandlerQueue()
        self.cTrav.addCollider(self.bodyGroundColNp, self.bodyGroundHandler)

        self.leftWheelGroundRay = CollisionRay()
        self.leftWheelGroundRay.setOrigin(2.895, -9.075, 1000)
        self.leftWheelGroundRay.setDirection(0,0,-1)
        self.leftWheelGroundCol = CollisionNode('leftWheelRay')
        self.leftWheelGroundCol.addSolid(self.leftWheelGroundRay)
        self.leftWheelGroundCol.setFromCollideMask(BitMask32.bit(0))
        self.leftWheelGroundCol.setIntoCollideMask(BitMask32.allOff())
        self.leftWheelGroundColNp = self.body.attachNewNode(self.leftWheelGroundCol)
        self.leftWheelGroundHandler = CollisionHandlerQueue()
        self.cTrav.addCollider(self.leftWheelGroundColNp, self.leftWheelGroundHandler)
        
        self.rightWheelGroundRay = CollisionRay()
        self.rightWheelGroundRay.setOrigin(-2.895, -9.075, 1000)
        self.rightWheelGroundRay.setDirection(0,0,-1)
        self.rightWheelGroundCol = CollisionNode('rightWheelRay')
        self.rightWheelGroundCol.addSolid(self.rightWheelGroundRay)
        self.rightWheelGroundCol.setFromCollideMask(BitMask32.bit(0))
        self.rightWheelGroundCol.setIntoCollideMask(BitMask32.allOff())
        self.rightWheelGroundColNp = self.body.attachNewNode(self.rightWheelGroundCol)
        self.rightWheelGroundHandler = CollisionHandlerQueue()
        self.cTrav.addCollider(self.rightWheelGroundColNp, self.rightWheelGroundHandler)
        
        #self.bodyGroundColNp.show()
        #self.cTrav.showCollisions(render)
        
#        self.frontBlade = loader.loadModel("models/esisahk")
#        self.frontBlade.reparentTo(self.body)
              
    def getScale(self):
        return GRINDER_SCALE * GLOBAL_SCALE
        
    def idleTurn(self):
        self.frontWheels.idle()
        self.steeringWheel.turn(self.frontWheels.getHeading())
        
    def idleSpeed(self):
        if (self.speed > 0):
            self.acceleration = self.acceleration - GRINDER_DEACCELARATION * 0.1
        
    def turnLeft(self):
        self.turn(LEFT)

    def turnRight(self):
        self.turn(RIGHT)
        
    def turn(self, direction):
        #elapsed = globalClock.getDt()
        self.frontWheels.turn(direction)
        self.steeringWheel.turn(self.frontWheels.getHeading())
        
    def steer(self, axis_value):
        self.frontWheels.steer(axis_value)
        self.steeringWheel.turn(self.frontWheels.getHeading())
        

    def moveForward(self):
        #print "moveForward"
        self.odeBody.addRelForce(0, -500, 0)
        return
        if (self.speed == 0): 
            self.acceleration = 0
        if (self.speed < GRINDER_MAX_SPEED):
            self.speed = self.speed  + 1
            self.acceleration = 0

    def moveBackward(self):
        #print "moveBackward"
        self.odeBody.setForce(0, 0, 0)
        self.acceleration = self.acceleration - GRINDER_DEACCELARATION * 0.5

    def move(self):
        self.bodyBox.setPosQuat(render, self.odeBody.getPosition(), Quat(self.odeBody.getQuaternion()))
        self.frontWheels.move()
        #self.backWheels.move()
        
    def moveOld(self):#, direction, acceleration, stopOnZero=0):
        #print `(direction, acceleration, stopOnZero)`
        #print `(self.speed, self.acceleration, self.direction)`
        if self.speed == 0 and self.acceleration <= 0: return
        stopOnZero = False;
        elapsed = globalClock.getDt()
        last_speed = self.speed
        #print 'bf:', `self.speed`, direction, elapsed, acceleration
#        if ((self.direction == FORWARD and self.speed < GRINDER_MAX_SPEED) 
#          or (self.direction == BACKWARD and self.speed < GRINDER_MAX_SPEED)):
        self.speed = self.speed + self.direction * elapsed * self.acceleration
        if (self.speed < 0):
            self.speed = 0
        #print 'af', `self.speed`
        if (stopOnZero == 1) and ((last_speed > 0 and self.speed < 0) or (last_speed < 0 and self.speed > 0)):
            self.speed = 0
         
#        if 1==1 or (self.speed > 0):
        oldHpr= self.body.getHpr()
        oldPos = self.body.getPos()
        heading = self.frontWheels.getHeading() / WHEEL_MAX_TURN
        if (self.speed > 0):
            self.body.setH(self.body.getH() + heading * elapsed  * GRINDER_TURN_MULTIPLER )
        else:
            self.body.setH(self.body.getH() - heading * elapsed  * GRINDER_TURN_MULTIPLER )
            
        self.body.setY(self.body, - elapsed * self.speed)
        """
        if self.checkGroundLevel() == 0: 
            #pass
            self.body.setHpr(oldHpr)
            self.body.setPos(oldPos)
        """
        #else:
            #print `self.body.getPos()`
        #print 'spin:'+str(self.speed)
        self.lastZPos = ((self.body.getZ(render), self.frontWheels.leftWheel.wheel.getZ(render), self.frontWheels.rightWheel.wheel.getZ(render)))
        #print "lastZPos: "+ `self.lastZPos`
        self.frontWheels.spin(self.speed)        
        self.moved = True
 
    def accelerate(self, axis_value): 
        axis_value = -axis_value - 0.1
        print `axis_value`
        if axis_value > 0:
            self.acceleration = (axis_value)*GRINDER_ACCELARATION
        else:
            self.acceleration = axis_value*GRINDER_DEACCELARATION
        
    def middleBladeDown(self):
        self.middleBlade.lowerDown()

    def middleBladeUp(self):
        self.middleBlade.riseUp()
        
    def middleBladeLeft(self):
        self.middleBlade.moveLeft()

    def middleBladeRight(self):
        self.middleBlade.moveRight()

    def middleBladeRotateLeft(self):
        self.middleBlade.rotateLeft()

    def middleBladeRotateRight(self):
        self.middleBlade.rotateRight()

    def frontBladeDown(self):
        self.frontBlade.lowerDown()

    def frontBladeUp(self):
        self.frontBlade.riseUp()

    def frontBladeLeft(self):
        self.frontBlade.turnLeft()

    def frontBladeRight(self):
        self.frontBlade.turnRight()
        
    def paintGround(self, ground):
        #pass
        self.frontWheels.paintGround(ground)
        #self.middleBlade.paintGround(image)
        self.frontBlade.paintGround(ground, self.speed)
        """
        def paint(image, x, y):
            #print `(x,y)`
            c1 = Vec3(0, 0, 0)
            c2 = Vec3(0.3, 0.3, 0.3)
            c3 = Vec3(0.6, 0.6, 0.6)
            image.setXelVal(int(x)-1, int(y), 0)
            image.setXelVal(int(x)-1, int(y)-1, 0)
            image.setXelVal(int(x), int(y)-1, 0)
            image.setXelVal(int(x), int(y), 0)
            image.setXelVal(int(x), int(y)+1, 0)
            image.setXelVal(int(x)+1, int(y)+1, 0)
            image.setXelVal(int(x)+1, int(y), 0)
        x1 = self.frontWheels.leftWheel.wheel.getX(render) / SNOW_SCALE + 128
        y1 = -self.frontWheels.leftWheel.wheel.getY(render) / SNOW_SCALE + 128
        x2 = self.frontWheels.rightWheel.wheel.getX(render) / SNOW_SCALE + 128
        y2 = -self.frontWheels.rightWheel.wheel.getY(render) / SNOW_SCALE + 128
        #print `(x1, y1)`
        paint(image, x1, y1);
        paint(image, x2, y2);
        #image.fillVal(0, 0, 0)
        """
        
    def checkGroundLevel(self):
        #print `self.body.getPos()`
        #return 0
        def getTerrianZ(groundHandler):
            entries = []
            for i in range(groundHandler.getNumEntries()):
                entry = groundHandler.getEntry(i)
                entries.append(entry)
            entries.sort(lambda x,y: cmp(y.getSurfacePoint(render).getZ(),
                                         x.getSurfacePoint(render).getZ()))
            #print `entries`
            if (len(entries)>0) and (entries[0].getIntoNode().getName() == "terrain"):
                #disp = entries[0].getSurfacePoint(render) - entries[0].getInteriorPoint(render)
                return entries[0].getSurfacePoint(render).getZ() #+ disp[2]
            return 30000
            
        self.cTrav.traverse(render)
        bodyZ = getTerrianZ(self.bodyGroundHandler)
        #print `bodyZ`
        leftWheelZ = max(0, getTerrianZ(self.leftWheelGroundHandler))
        rightWheelZ = max(0, getTerrianZ(self.rightWheelGroundHandler))
        #print (bodyZ, leftWheelZ, rightWheelZ), " -> ",
        if bodyZ == 30000: bodyZ = self.lastZPos[0]
        if leftWheelZ == 30000: leftWheelZ = self.lastZPos[1]
        if rightWheelZ == 30000: rightWheelZ = self.lastZPos[2]
        #print (bodyZ, leftWheelZ, rightWheelZ)

        self.body.setZ(bodyZ)
        tilt = 0
        _min = min(leftWheelZ, rightWheelZ)
        if ( abs(leftWheelZ - rightWheelZ) > 10): return 0
        if _min == leftWheelZ:
            tilt = math.degrees(math.atan((rightWheelZ - leftWheelZ) / (2)));
        else:
            tilt = - math.degrees(math.atan((leftWheelZ - rightWheelZ) / (2)));
#        print `(_min, rightWheelZ,leftWheelZ, tilt)`
        self.body.setR(tilt)
        wheelZ = (leftWheelZ + rightWheelZ) /2
        _min = min(bodyZ, wheelZ)
        if _min == bodyZ:
            head = math.degrees(math.atan((bodyZ - wheelZ) / (1)));
        else:
            head = - math.degrees(math.atan((wheelZ - bodyZ) / (1)));
        self.body.setP(head)
        return 1
        
    def hasMoved(self):
        ret = self.moved
        self.moved = False
        return ret
            
