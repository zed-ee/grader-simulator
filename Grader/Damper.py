class Damper:
    def __init__(self, (parent_up, model_up, pos_up), (parent_down, model_down, pos_down)):

        self.up = loader.loadModel("models/grader/"+model_up)
        self.up.reparentTo(parent_up)
        self.up.setPos(pos_up)

        self.down = loader.loadModel("models/grader/"+model_down)
        self.down.reparentTo(parent_down)
        self.down.setPos(pos_down)
        self.update()
        
    def update(self):
        self.up.lookAt(self.down)
        self.down.lookAt(self.up)
