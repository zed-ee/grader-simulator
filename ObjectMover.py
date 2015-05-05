from direct.showbase.DirectObject import DirectObject
from direct.task.Task import Task

class ObjectMover(DirectObject):
    keyboardMapping = { 
        "a": "object-inc", "s": "object-dec"
    }
    keyMap = {}
    mode = 0;
    def __init__(self, object, step, parent=render, ode_geom = None):
        self.object = object
        self.step = step
        self.setupKeys()
        self.parent = parent
        self.ode_geom = ode_geom
        taskMgr.add(self.handleKeys,"ObjectMover.handleKeys")       
        
    def increaseX(self):
        elapsed = globalClock.getDt()
        self.object.setX(self.object.getX() + self.step)
    def decreaseX(self):
        elapsed = globalClock.getDt()
        self.object.setX(self.object.getX() - self.step)
    def increaseY(self):
        elapsed = globalClock.getDt()
        self.object.setY(self.object.getY() + self.step)
    def decreaseY(self):
        elapsed = globalClock.getDt()
        self.object.setY(self.object.getY() - self.step)
    def increaseZ(self):
        elapsed = globalClock.getDt()
        self.object.setZ(self.object.getZ() + self.step)
    def decreaseZ(self):
        elapsed = globalClock.getDt()
        self.object.setZ(self.object.getZ() - self.step)
        
    def increaseH(self):
        elapsed = globalClock.getDt()
        self.object.setH(self.object.getH() + 1)
    def decreaseH(self):
        elapsed = globalClock.getDt()
        self.object.setH(self.object.getH() - 1)
    def increaseP(self):
        elapsed = globalClock.getDt()
        self.object.setP(self.object.getP() + 1)
    def decreaseP(self):
        elapsed = globalClock.getDt()
        self.object.setP(self.object.getP() - 1)
    def increaseR(self):
        elapsed = globalClock.getDt()
        self.object.setR(self.object.getR() + 1)
    def decreaseR(self):
        elapsed = globalClock.getDt()
        self.object.setR(self.object.getR() - 1)

    def toggleMode(self):
        self.mode = self.mode +1;
        if self.mode == 6: self.mode = 0;
        print "new mode: ",
        if self.mode == 0:
            print 'X'
        elif self.mode == 1:
            print 'Y'
        elif self.mode == 2:
            print 'Z'
        elif self.mode == 3:
            print 'H'
        elif self.mode == 4:
            print 'P'
        elif self.mode == 5:
            print 'R'
        
    def increase(self):
        if self.mode == 0:
            self.increaseX()
        elif self.mode == 1:
            self.increaseY()
        elif self.mode == 2:
            self.increaseZ()
        elif self.mode == 3:
            self.increaseH()
        elif self.mode == 4:
            self.increaseP()
        elif self.mode == 5:
            self.increaseR()
        if self.ode_geom <> None:
            self.ode_geom.setQuaternion(self.object.getQuat(render))
            self.ode_geom.setPosition(self.object.getPos(render))
        print `self.object.getPos(self.parent)`, `self.object.getHpr(self.parent)`, `self.object.getQuat(self.parent)`

    def decrease(self):
        if self.mode == 0:
            self.decreaseX()
        elif self.mode == 1:
            self.decreaseY()
        elif self.mode == 2:
            self.decreaseZ()
        elif self.mode == 3:
            self.decreaseH()
        elif self.mode == 4:
            self.decreaseP()
        elif self.mode == 5:
            self.decreaseR()
        if self.ode_geom <> None:
            self.ode_geom.setQuaternion(self.object.getQuat(render))
            self.ode_geom.setPosition(self.object.getPos(render))
        print `self.object.getPos(self.parent)`, `self.object.getHpr(self.parent)`, `self.object.getQuat(self.parent)`

    def printPos(self):
        print `self.object.getPos(self.parent)`, `self.object.getHpr(self.parent)`, `self.object.getQuat(self.parent)`, `globalClock.getFrameTime()`
        
    def setupKeys(self):
        self.accept('w-up', self.toggleMode)
        self.accept('x-up', self.printPos)
        for key in self.keyboardMapping.keys():
            self.accept(key, self.setKey, [self.keyboardMapping[key],1])
            self.accept(key+'-up', self.setKey, [self.keyboardMapping[key],0]) 
            self.keyMap[self.keyboardMapping[key]] = 0
	
    #Records the state of the arrow keys
    def setKey(self, key, value):
        self.keyMap[key] = value
        
    def handleKeys(self, task):
        if (self.keyMap["object-inc"]!=0):     self.increase()
        if (self.keyMap["object-dec"]!=0):     self.decrease()
        return Task.cont        
    
     