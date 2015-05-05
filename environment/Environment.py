from pandac.PandaModules import Texture, DecalEffect, NodePath, PandaNode, Shader
from pandac.PandaModules import OdeBody, OdeMass, OdeSphereGeom, OdeBoxGeom, OdePlaneGeom, OdeCylinderGeom, OdeCappedCylinderGeom, OdeTriMeshGeom, OdeTriMeshData
from pandac.PandaModules import BitMask32, Quat, Mat4, EggData, Filename,DecalEffect
import odebase

class Environment:
    modes = ['summer', 'winter']
    selectedMode = -1
    models = {'ground':  {'model': "models/environment/ground", 'texture': None, 'z':0, 'ode':2}, 
              'grass':  {'model': "models/environment/grass", 'texture': ['models/environment/summer/mudel/4739.jpg', 'models/SnowTexture.jpg'], 'z':0, 'ode':0}, 
              'gravel': {'model': "models/environment/gravel_sideroads", 'texture': ['models/environment/summer/mudel/3093.jpg', 'models/environment/winter/mudel/3093_2.jpg'], 'z':0.05, 'ode':0}, 
              'gravel3': {'model': "models/environment/gravel_sideroads", 'texture': ['models/environment/summer/mudel/sand.jpg', None], 'z':0.05, 'ode':0, 'dontshow': 1}, 
              'road':   {'model': "models/environment/road", 'texture': ['models/environment/winter/mudel/road.jpg', 'models/environment/winter/mudel/road2.jpg'], 'z':0.1, 'ode':0}, 
              'skybox': {'model': "models/environment/skybox", 'texture': ['models/environment/summer/suvine_taevas.jpg', 'models/environment/winter/talvine_taevas.jpg'], 'z':0, 'ode':0}, #              'houses': {'model': "models/environment/houses", 'texture': None, 'z':0, 'ode':1},
              'river': {'model': "models/environment/river", 'texture': None, 'z':0.1, 'ode':0},
              'houses': {'model': "models/environment/houses", 'texture': None, 'z':0.1, 'ode':1},
              'bridge': {'model': "models/environment/bridge", 'texture': None, 'z':0.1, 'ode':1},
              'bridge_road': {'model': "models/environment/bridge_road", 'texture': None, 'z':0.1, 'ode':0},
              'trees':  {'model': "models/environment/trees", 'texture': ['models/environment/summer/kuusk_color.png','models/environment/winter/kuusk_talv_color.png'], 'z':0, 'ode':0},
              'signs1': {'model': "models/environment/signs01", 'texture': None, 'z':0, 'ode':1},
              'signs2': {'model': "models/environment/signs02", 'texture': None, 'z':0, 'ode':1},
              'signs3': {'model': "models/environment/signs03", 'texture': None, 'z':0, 'ode':1},
              'bigtree': {'model': "models/environment/bigtree", 'texture': None, 'z':0, 'ode':1},
              'posts': {'model': "models/environment/level_posts", 'texture': None, 'z':0, 'ode':0},
              'bus':  {'model': "models/vehicles/bus", 'texture': None, 'z':0, 'ode':1, 'pos':(1399.12, 1843.18, 180.95), 'hpr':(207.14, 0.00, 0.00), 'scale':1}, 
              'bmw':  {'model': "models/vehicles/bmw", 'texture': None, 'z':0, 'ode':1, 'pos':(1484.62, 1548.36, 174.21), 'hpr':(142.59, 0.00, 0.00), 'scale':1}, 
              'toyota':  {'model': "models/vehicles/toyota", 'texture': None, 'z':0, 'ode':1, 'pos':(1499.04, 1526.91, 173.21), 'hpr':(142.59, 0.00, 0.00), 'scale':1.25}, 
              'ekskavaator':  {'model': "models/vehicles/ekskavaator", 'texture': None, 'z':0, 'ode':1, 'pos':(0, 0, 0), 'hpr':(341.57, 0.00, 350.54), 'scale':1.50, 'dontshowx':1}, 
              'golf':  {'model': "models/vehicles/vw_golf", 'texture': None, 'z':0, 'ode':1, 'pos':(0, 0, 0), 'hpr':(222.51, 6.00, 0.00), 'scale':1.25, 'dontshow':1}, 
              #'police':  {'model': "models/vehicles/police", 'texture': None, 'z':0, 'ode':1, 'pos':(3899.20, 404.39, 111.97), 'hpr':(320.71, 0.00, 0.00), 'scale':1.25}, 
             }
             #pos':(3737.69, 763.991, 91.82)
    def __init__(self, odeworld, scale):
#        self.node = NodePath(PandaNode("cube"))
#        self.node.reparentTo(render)    
        world = odeworld.world
        space = odeworld.space
        shader = Shader.load(Shader.SLGLSL, "dummy_vrtx.sha", "dummy_frag.sha","") 
        print `shader`
        for i in range(len(self.models)):
            x = self.models.keys()[i]
            model = loader.loadModel(self.models[x]['model'])
            model.setZ(self.models[x]['z'])

            if self.models[x].has_key('pos'):
                model.setPos(self.models[x]['pos'])
            if self.models[x].has_key('hpr'):
                model.setHpr(self.models[x]['hpr'])
            if self.models[x].has_key('scale'):
                print 'setscale: '+x +', '+`self.models[x]['scale']`
                model.setScale(self.models[x]['scale'])
            else:
                print 'setscale: '+x +', '+`scale`
                model.setScale(scale)
            
            model.flattenStrong()
            self.models[x]['model'] = model
            if self.models[x]['ode'] == 2:
                self.models[x]['ode_geom'] = odebase.ODEtrimesh(world, space, realObj=None, collObj= model,
                               mass=0, surfaceId=0, collideBits=6, categoryBits=1)
                odeworld.AddObject(self.models[x]['ode_geom'])
                #model.reparentTo(render)
            elif self.models[x]['ode'] == 1:
                if self.models[x].has_key('mass'):
                    m = self.models[x]['mass']
                    coll = 255
                    cat = 2
                else:
                    m = 0
                    coll = 6
                    cat = 1
                self.models[x]['ode_geom'] = odebase.ODEtrimesh(world, space, realObj= model, collObj=None,
                               mass=m, surfaceId=0, collideBits=coll, categoryBits=cat)
                odeworld.AddObject(self.models[x]['ode_geom'])
                if not self.models[x].has_key('dontshow'):
                    model.reparentTo(render)
            elif not self.models[x].has_key('dontshow'):
                model.reparentTo(render)
                
                
            if self.models[x]['texture'] != None:
                for y in range(len(self.models[x]['texture'])):                
                    if self.models[x]['texture'][y] != None:
                        texture= loader.loadTexture(self.models[x]['texture'][y])
                        texture.setWrapU(Texture.WMRepeat)
                        texture.setWrapV(Texture.WMRepeat)
                        texture.setMagfilter(Texture.FTLinear)
                        texture.setMinfilter(Texture.FTLinearMipmapLinear)                    
                        self.models[x]['texture'][y] = texture
                        #self.base.setTexture(tex1,1)
                #self.models[x]['model'].setTexture(self.models[x]['texture'][self.selectedMode], 1)        
                
            if self.models[x].has_key('shader'):
                model.setShaderInput("colorMap",  self.models[x]['texture'][self.selectedMode])
                model.setShader(shader)
            
            
        #self.models['gravel3']['model'].detachNode()
        #load trees
        egg = EggData()
        egg.read(Filename("models/environment/noor_puu_locations.egg"))
        planeGroup = egg.getFirstChild()
        plane = planeGroup.getFirstChild()
        i = 0
        while plane != None:            
            pos = plane.getFirstChild().getVertex(1).getPos3()
            #print 'ddd:', `pos`,
            (x, y, z) = pos * 4
            print `(x, y, z)`
            tree = loader.loadModel("models/environment/noor_puu")
            tree.setScale(4)
            tree.reparentTo(render)
            tree.setPos(x,y,z+4)
            #tree.setH(180)
            #tree.node().setEffect(DecalEffect.make())
            tree.setBillboardAxis();
            key = 'tree'+str(i)
            textures = []
            for x in ['summer', 'winter']:
                texture= loader.loadTexture('models/environment/'+x+'/puud/noor_puu.png')
                texture.setWrapU(Texture.WMRepeat)
                texture.setWrapV(Texture.WMRepeat)
                texture.setMagfilter(Texture.FTLinear)
                texture.setMinfilter(Texture.FTLinearMipmapLinear)                    
                textures.append(texture)
            
            self.models[key] = {'model': tree, 'texture': textures, 'z':0.0, 'ode':0}
            plane = planeGroup.getNextChild()
            i = i + 1
        
    def selectSummer(self):
        if self.selectedMode == 0: return
        self.selectedMode = 0
        self.changeMode()
        
    def selectWinter(self):
        if self.selectedMode == 1: return
        self.selectedMode = 1
        self.changeMode()

    def changeMode(self):
        print "Environment.changeMode" + self.modes[self.selectedMode]
        for i in range(len(self.models)):
            x = self.models.keys()[i]
            if self.models[x]['texture'] != None:
                if (self.models[x]['texture'][self.selectedMode] != None):
                    self.models[x]['model'].setTexture(self.models[x]['texture'][self.selectedMode], 1)        
                    self.models[x]['model'].reparentTo(render)
                else:
                    self.models[x]['model'].detachNode()
            if self.models[x].has_key('shader'):
                self.models[x]['model'].setShaderInput("colorMap",  self.models[x]['texture'][self.selectedMode])
        
        