from Wheel import *
from Config import *

class BackWheels: 
    def __init__(self, parent, odeBody, odeWorld, odeSpace):
        self.leftWheel = Wheel(parent, odeBody, odeWorld, odeSpace, LEFT, Vec3(2.895, 4.99, 1.873), "wheelsupport-back")
        self.leftWheel2 = Wheel(parent, odeBody, odeWorld, odeSpace, LEFT, Vec3(2.895, 8.87, 1.873), "wheelsupport-back")
        self.rightWheel = Wheel(parent, odeBody, odeWorld, odeSpace, RIGHT, Vec3(-2.895, 4.99, 1.873), "wheelsupport-back")
        self.rightWheel2 = Wheel(parent, odeBody, odeWorld, odeSpace, RIGHT, Vec3(-2.895, 8.87, 1.873), "wheelsupport-back")
        
	
    def idle(self):
        self.leftWheel.idle()
        self.rightWheel.idle()
        self.leftWheel2.idle()
        self.rightWheel2.idle()
        
    def spin(self, speed):
        self.leftWheel.spin(speed)
        self.rightWheel.spin(speed)        
        self.leftWheel2.spin(speed)
        self.rightWheel2.spin(speed)        
        
