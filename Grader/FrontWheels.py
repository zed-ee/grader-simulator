from Wheel import *
from Config import *

class FrontWheels: 
    def __init__(self, parent):
        self.leftWheel = Wheel(parent, LEFT, Vec3(2.895, -9.075, 1.873))
        #self.leftWheel.setPos(LEFT_WHEEL_POS)
        self.rightWheel = Wheel(parent, RIGHT,Vec3(-2.895, -9.075, 1.873))
        #self.rightWheel.setPos(RIGHT_WHEEL_POS)
        
    def move(self):
        self.leftWheel.move()
        self.rightWheel.move()
        
    def turn(self, direction):
        #print `self.getHeading()`
        if (self.getHeading() > WHEEL_MAX_TURN and direction == LEFT):
            return
        if (self.getHeading() < -WHEEL_MAX_TURN and direction == RIGHT):
            return

        self.leftWheel.turn(direction)
        self.rightWheel.turn(direction)
        
    def steer(self, axis_value):
        self.leftWheel.steer(axis_value)
        self.rightWheel.steer(axis_value)
        
    def getHeading(self):
        return (self.leftWheel.getAngle() + self.rightWheel.getAngle()) / 2 ;
	
    def idle(self):
        self.leftWheel.idle()
        self.rightWheel.idle()
        
    def spin(self, speed):
        self.leftWheel.spin(speed)
        self.rightWheel.spin(speed)        
        
    def paintGround(self, image):
        self.leftWheel.paintGround(image)
        self.rightWheel.paintGround(image)
        
    def stopPaint(self):
        self.leftWheel.stopPaint()
        self.rightWheel.stopPaint()
