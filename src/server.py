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
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

    def step(self):
        self.move()

    def move(self):
        possible_steps = self.model.grid.get_neighborhood(
            self.pos,
            moore=True,
            include_center=False
        )
        new_position = random.choice(possible_steps)
        self.model.grid.move_agent(self, new_position)


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
        
        airport_x_coordinates = []
        airport_y_coordinates = []
        
        for i in range(self.airports):
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            airport_x_coordinates.append(x)
            airport_y_coordinates.append(y)
            airport = Airport(i, self, (x, y))
            self.grid.place_agent(airport, (x, y))
        
        total = len(airport_x_coordinates)
        
        # Criação dos agentes móveis
        for i in range(self.airplanes):
            a = Airplane(i, self)
            self.schedule.add(a)
            x = airport_x_coordinates[i%total]
            y = airport_y_coordinates[i%total]
            self.grid.place_agent(a, (x, y))
            
            

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

