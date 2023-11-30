import random

from mesa import Agent, Model
from mesa.space import MultiGrid
from mesa.time import RandomActivation
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import CanvasGrid
#from mesa_models.boltzmann_wealth_model.model import BoltzmannWealthModel
from mesa.datacollection import DataCollector
import ipywidgets as widgets
from IPython.display import display
from mesa.visualization.UserParam import Slider

# Defina suas variáveis iniciais aqui


class Airplane(Agent):
    def __init__(self, unique_id, model,origin : list ,destination : list):
        super().__init__(unique_id, model)
        self.destination = destination
        self.origin = origin

    def step(self):
        self.move()

    def move(self):
        print('origin: ',self.origin)
        print('dest: ',self.destination)
        x0 = self.origin[0]
        y0 = self.origin[1]
        x1 = self.destination[0]
        y1 = self.destination[1]

        while [x0,y0] != [x1,y1]:
            if x0 < x1:
                x0 = x0 + 1
                self.model.grid.move_agent(self, (x0,y0))
            elif x0 > x1 :
                x0 = x0 - 1
                self.model.grid.move_agent(self, (x0,y0))
                print(x0,y0)
            if y0 < y1:
                y0 = y0 + 1
                self.model.grid.move_agent(self, (x0,y0))
                print(x0,y0)
            elif y0 > y1:
                y0 = y0 - 1
                self.model.grid.move_agent(self, (x0,y0))
                print(x0,y0)
        #self.model.grid.move_agent(self, (x0,y0))
        
        #new_position = random.choice(possible_steps)
        #self.model.grid.move_agent(self, new_position)


class Airport(Agent):
    def __init__(self, unique_id, model, pos):
        super().__init__(unique_id, model)
        self.pos = pos

    def step(self):
        # Aeroportos são agentes fixos, não têm movimento
        pass


def agent_portrayal(agent):
    if isinstance(agent, Airplane):
        return {"Shape": "circle", "Filled": "true", "Layer": 0, "Color": "red", "r": 0.5}
    elif isinstance(agent, Airport):
        return {"Shape": "rect", "Filled": "true", "Layer": 0, "Color": "blue", "w": 0.5, "h": 0.5}


class TraficControler(Model):
    def __init__(self, airplanes, width, height, airports):
        self.airplanes = airplanes
        self.airports = airports
        self.grid = MultiGrid(width, height, True)
        self.schedule = RandomActivation(self)        
        self.airport_coordinates = []
        
        for i in range(self.airports):
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.airport_coordinates.append((x,y))
            airport = Airport(i, self, (x, y))
            self.grid.place_agent(airport, (x, y))
        
        total = len(self.airport_coordinates)
        
        # Criação dos agentes móveis
        for i in range(self.airplanes):
            dest = list(self.airport_coordinates[(i+1)%total])
            origin = list(self.airport_coordinates[i%total])
            a = Airplane(i, self,origin,dest)
            self.schedule.add(a)
            self.grid.place_agent(a, origin)

    def step(self):
        self.schedule.step()

grid = CanvasGrid(agent_portrayal, 20, 20, 500, 500)

model_params = {
    "airplanes": Slider("Airplanes", 10, 1, 100, 1),
    "airports": Slider("Airport", 3, 1, 100, 1),
    "width": 10,
    "height": 10,
}

server = ModularServer(
    TraficControler,
    [grid],
    "Airplane Traffic Controler",
    model_params
)

server.launch()
