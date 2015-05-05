from pandac.PandaModules import NodePath,PandaNode
from pandac.PandaModules import Vec2,Vec3,Vec4,BitMask32
from pandac.PandaModules import OdeBody, OdeMass, Quat, OdeCylinderGeom, OdeSphereGeom, OdeHinge2Joint

from Config import *
from Utils import *

class Wheel:
    def __init__(self, parent, side = LEFT, pos = Vec3(0,0,0), wheelJoint = None):
        self.angle = 0
        self.side = side
        startPos = None
#        for child in parent.getChildren():
#            print child


        if wheelJoint != None:
                self.wheelJoint = loader.loadModel("models/grader/"+wheelJoint)
                self.surfaceId = 2
        else:
            if side == LEFT:
                self.wheelJoint = loader.loadModel("models/grader/wheelsupport-left")
            else:
                self.wheelJoint = loader.loadModel("models/grader/wheelsupport-right")
            self.surfaceId = 1
            
        print `startPos`
        self.wheelJoint.reparentTo(parent)
        self.wheelJoint.setPos(pos)
#        self.wheelJoint.setScale(0.01)
        """
        self.wheel = loader.loadModel("models/grader/wheel")
        self.wheel.flattenLight()
        """
        self.wheel = NodePath(PandaNode("wheel_"+str(side)))
        self.wheel.reparentTo(self.wheelJoint)
        if (self.side == LEFT):
            self.wheel.setHpr(180, 0, 0)
            startPos = Vec3(0.525, 0, -0.192)
        else:
            startPos = Vec3(-0.525, 0, -0.192)
        self.wheel.setPos(startPos)
        
        self.lastPos = None
        self.helper =  NodePath(PandaNode("wheel_helper1_"+str(side)))
        self.helper.reparentTo(self.wheelJoint)
        if side == LEFT:
            self.helper.setPos(0,0,-1.5)
        else:
            self.helper.setPos(-1,0,-1.5)
        
    def move(self):
        self.wheel.setPosQuat(render, self.body.getPosition(), Quat(self.body.getQuaternion()))
        
    def setPos(self, x, y, z):
        self.wheelJoint.setPos(x, y, z)
        
    def turn(self, direction, stopOnZero = 0):
        #print `self.wheelJoint.getH()`
        elapsed = globalClock.getDt()
        last_angle = self.angle
        if(self.side == LEFT and self.getAngle() > 0 ):
            multipler = WHEEL_TURN_SPEED_OUTSIDE
        elif(self.side == RIGHT and self.getAngle() < 0 ):
            multipler = WHEEL_TURN_SPEED_OUTSIDE
        else:
            multipler = WHEEL_TURN_SPEED_INSIDE
        #print self.side, self.getAngle(), multipler
        self.angle = self.angle + direction * elapsed * multipler;
        if (stopOnZero == 1) and ((last_angle > 0 and self.angle < 0) or (last_angle < 0 and self.angle > 0)):
            self.angle = 0
        self.wheelJoint.setH(self.denormalize(self.angle))
        
    def steer(self, angle):
        """
        if(self.side == LEFT and self.getAngle() > 0 ):
            multipler = WHEEL_TURN_SPEED_OUTSIDE
        elif(self.side == RIGHT and self.getAngle() < 0 ):
            multipler = WHEEL_TURN_SPEED_OUTSIDE
        else:
            multipler = WHEEL_TURN_SPEED_INSIDE
        
        self.angle = -axis_value * multipler;
        """
        self.wheelJoint.setH(self.denormalize(angle)*0.8)
        
    def getAngle(self):
        return self.angle

    
    def normalize(self, value):
        if self.side == 9:
            return value - 180
        else:
            return value
    def denormalize(self, value):
        if self.side == 9:
            return value + 180
        else:
            return value
        
    def idle(self):
		if( self.getAngle() > 0 ):
			self.turn(RIGHT, 1)
		if( self.getAngle() < 0 ):
			self.turn(LEFT, 1)
            
    def spin(self, speed):
        elapsed = globalClock.getDt()
        #self.wheel.setP( self.wheel.getP() - speed * elapsed * WHEEL_SPIN_SPEED * self.side)			
        
    def paintGround(self, ground):
        pos = self.helper.getPos(render)
        if (self.lastPos <> None):
            ground.paint(self.lastPos, pos, Vec3(0,0,1))
        self.lastPos = pos
        
    def stopPaint(self):
        self.lastPos = None
    
    
        
        