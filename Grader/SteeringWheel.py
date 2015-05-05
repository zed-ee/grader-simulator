from Config import *

class SteeringWheel:
    def __init__(self, parent):
        self.wheel = loader.loadModel("models/grader/steering-wheel")
        self.wheel.reparentTo(parent)
        self.wheel.setPos(0, 1.35, 6.1)
        self.wheel.setHpr(0, 60, 0)
            
    def setPos(self, x, y, z):
        self.wheel.setPos(x, y, z)
        
    def turn(self, heading):
        self.wheel.setR(heading * STEERING_WHEEL_MULTIPLER)
        