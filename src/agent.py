from mesa import Agent

class Airplane(Agent):
    def __init__(self, unique_id, model,origin : list ,destination : list):
        super().__init__(unique_id, model)
        self.destination = destination
        self.origin = origin

    def step(self):
        self.move()

    def move(self):
        x0 = self.origin[0]
        y0 = self.origin[1]
        x1 = self.destination[0]
        y1 = self.destination[1]

        if [x0,y0] != [x1,y1]:
            if x0 < x1:
                x0 = x0 + 1
            elif x0 > x1 :
                x0 = x0 - 1
            if y0 < y1:
                y0 = y0 + 1
            elif y0 > y1:
                y0 = y0 - 1
        self.model.grid.move_agent(self, (x0,y0))

        self.origin[0] = x0
        self.origin[1] = y0
        self.destination[0] = x1
        self.destination[1] = y1

class Airport(Agent):
    def __init__(self, unique_id, model, pos):
        super().__init__(unique_id, model)
        self.pos = pos

    def step(self):
        # Aeroportos são agentes fixos, não têm movimento
        pass
