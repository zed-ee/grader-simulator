from direct.directbase import DirectStart
from pandac.PandaModules import OdeWorld, OdeSimpleSpace, OdeJointGroup
from pandac.PandaModules import OdeBody, OdeMass, OdeBoxGeom, OdePlaneGeom
from pandac.PandaModules import OdeSphereGeom, OdeBoxGeom, OdeCylinderGeom, OdeCappedCylinderGeom, OdeTriMeshGeom, OdeTriMeshData
from pandac.PandaModules import BitMask32, CardMaker, Vec4, Quat
from random import randint, random

def getOBB(collObj):
    ''' get the Oriented Bounding Box '''
    # save object's parent and transformation
    parent=collObj.getParent()
    trans=collObj.getTransform()
    # ODE need everything in world's coordinate space,
    # so bring the object directly under render, but keep the transformation
    collObj.wrtReparentTo(render)
    # get the tight bounds before any rotation
    collObj.setHpr(0,0,0)
    bounds=collObj.getTightBounds()
    offset=collObj.getBounds().getCenter()-collObj.getPos()
    # bring object to it's parent and restore it's transformation
    collObj.reparentTo(parent)
    collObj.setTransform(trans)
    # (max - min) bounds
    box=bounds[1]-bounds[0]
#        print bounds[0], bounds[1]
    return [box[0],box[1],box[2]], [offset[0],offset[1],offset[2]]
"""    
# Setup our physics world
world = OdeWorld()
world.setGravity(0, 0, -9.81)
 
# The surface table is needed for autoCollide
world.initSurfaceTable(1)
world.setSurfaceEntry(0, 0, 150, 0.0, 9.1, 0.9, 0.00001, 0.0, 0.002)
#world.setSurfaceEntry(0, 0, 0.8, 0.0, 10, 0.9, 0.00001, 100, 0.002)
 
# Create a space and add a contactgroup to it to add the contact joints
space = OdeSimpleSpace()
space.setAutoCollideWorld(world)
contactgroup = OdeJointGroup()
space.setAutoCollideJointGroup(contactgroup)
"""
# Load the box
box = loader.loadModel("box")
# Make sure its center is at 0, 0, 0 like OdeBoxGeom
box.setPos(-.5, -.5, -.5)
box.setScale(10,10,10)
box.flattenLight() # Apply transform
box.setTextureOff()
 
# Add a random amount of boxes
boxes = []

class c:
    def __init__(self,odeWorld, odeSpace):
        self.bodyBox = loader.loadModel("models/grader/body-box")
        self.bodyBox.setScale(0.25)
        self.bodyBox.reparentTo(render)
        self.bodyBox.setPos(400, 400, 100)
        #self.bodyBox.setHpr(GRADER_START_HPR)
        
        boundingBox, offset=getOBB(self.bodyBox)
        print `(boundingBox, offset)`
        boxGeom = OdeBoxGeom(space, *boundingBox)
        self.odeBody = OdeBody(odeWorld)
        M = OdeMass()
        M.setBox(50, *boundingBox)
        self.odeBody.setMass(M)
        self.odeBody.setPosition(self.bodyBox.getPos(render))
        self.odeBody.setQuaternion(self.bodyBox.getQuat(render))
        # Create a BoxGeom
        self.geom = OdeBoxGeom(odeSpace, 1, 1, 1)
        self.geom.setCollideBits(BitMask32(0x00000002))
        self.geom.setCategoryBits(BitMask32(0x00000001))
        self.geom.setBody(self.odeBody)
        boxes.append((self.bodyBox, self.odeBody))

class e:
    def __init__(self,odeWorld, odeSpace):
        obj = loader.loadModel("models/environment/grass")
        obj.reparentTo(render) 
        modelTrimesh = OdeTriMeshData(obj, True)
        self.geom = OdeTriMeshGeom(odeSpace, modelTrimesh)
        # synchronize ODE geom's transformation according to the real object's
        self.geom.setPosition(obj.getPos(render))
        self.geom.setQuaternion(obj.getQuat(render))
        #self.geom.getSpace().setSurfaceType(self.geom, 0)
        self.geom.setCollideBits(BitMask32(0x00000001))
        self.geom.setCategoryBits(BitMask32(0x00000002))            

class w:
    def __init__():
        self.odeWorld = OdeWorld()
        self.odeWorld.setGravity(0, 0, -9.81)
        # The surface table is needed for autoCollide
        self.odeWorld.initSurfaceTable(1)
        self.odeWorld.setSurfaceEntry(0, 0, 150, 0.0, 9.1, 0.9, 0.00001, 0.0, 0.002)
        #self.odeWorld.setSurfaceEntry(0, 0, 0.8, 0.0, 10, 0.9, 0.00001, 100, 0.002)
         
        # Create a space and add a contactgroup to it to add the contact joints
        self.odeSpace = OdeSimpleSpace()
        self.odeSpace.setAutoCollideWorld(self.odeWorld)
        self.contactgroup = OdeJointGroup()
        self.odeSpace.setAutoCollideJointGroup(self.contactgroup)
        self.x = c(world, space)
        self.y = e(world, space)
# Setup the geometry
"""
boxNP = box.copyTo(render)
boxNP.setPos(400+randint(-10, 10), 400+randint(-10, 10), 100 + random())
boxNP.setColor(random(), random(), random(), 1)
boxNP.setHpr(randint(-45, 45), randint(-45, 45), randint(-45, 45))
boundingBox, offset=getOBB(box)
print `(boundingBox, offset)`
boxGeom = OdeBoxGeom(space, *boundingBox)
boxBody = OdeBody(world)
M = OdeMass()
M.setBox(50, *boundingBox)
boxBody.setMass(M)
boxBody.setPosition(boxNP.getPos(render))
boxBody.setQuaternion(boxNP.getQuat(render))
boxGeom.setBody(boxBody)

# Create the body and set the mass
boxBody = OdeBody(world)
M = OdeMass()
M.setBox(50, 1, 1, 1)
boxBody.setMass(M)
boxBody.setPosition(boxNP.getPos(render))
boxBody.setQuaternion(boxNP.getQuat(render))
# Create a BoxGeom
boxGeom = OdeBoxGeom(space, 1, 1, 1)

boxGeom.setCollideBits(BitMask32(0x00000002))
boxGeom.setCategoryBits(BitMask32(0x00000001))
boxGeom.setBody(boxBody)
boxes.append((boxNP, boxBody))

ground = loader.loadModel("models/environment/grass")
ground.reparentTo(render) 

# Add a plane to collide with
#cm = CardMaker("ground")
#cm.setFrame(-20, 20, -20, 20)
#ground = render.attachNewNode(cm.generate())
#ground.setPos(400, 400, 60); ground.lookAt(0, 0, -1)
#groundGeom = OdePlaneGeom(space, Vec4(0, 0, 1, 0))
modelTrimesh = OdeTriMeshData(ground, True)
groundGeom = OdeTriMeshGeom(space, modelTrimesh)
# synchronize ODE geom's transformation according to the real object's
groundGeom.setPosition(ground.getPos(render))
groundGeom.setQuaternion(ground.getQuat(render)) 

groundGeom.setCollideBits(BitMask32(0x00000001))
groundGeom.setCategoryBits(BitMask32(0x00000002))

obj=ground
modelTrimesh = OdeTriMeshData(obj, True)
geom = OdeTriMeshGeom(space, modelTrimesh)
# synchronize ODE geom's transformation according to the real object's
geom.setPosition(obj.getPos(render))
geom.setQuaternion(obj.getQuat(render))
#self.geom.getSpace().setSurfaceType(self.geom, 0)
geom.setCollideBits(BitMask32(0x00000001))
geom.setCategoryBits(BitMask32(0x00000002))
"""
# Set the camera position
base.disableMouse()
base.camera.setPos(350, 350, 200)
base.camera.lookAt(400, 400, 0)
 
# The task for our simulation
def simulationTask(task):
  space.autoCollide() # Setup the contact joints
  # Step the simulation and set the new positions
  world.quickStep(globalClock.getDt())
  for np, body in boxes:
    np.setPosQuat(render, body.getPosition(), Quat(body.getQuaternion()))
  contactgroup.empty() # Clear the contact joints
  return task.cont
 
# Wait a split second, then start the simulation  
taskMgr.doMethodLater(0.5, simulationTask, "Physics Simulation")
 
run()