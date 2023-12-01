import random

from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import CanvasGrid
#from mesa_models.boltzmann_wealth_model.model import BoltzmannWealthModel
from mesa.datacollection import DataCollector
import ipywidgets as widgets
from IPython.display import display
from mesa.visualization.UserParam import Slider

from model import *
from agent import *

# Defina suas variáveis iniciais aqui
def agent_portrayal(agent):
    if isinstance(agent, Airplane):
        return {"Shape": "circle", "Filled": "true", "Layer": 0, "Color": "red", "r": 0.5}
    elif isinstance(agent, Airport):
        return {"Shape": "rect", "Filled": "true", "Layer": 0, "Color": "blue", "w": 0.5, "h": 0.5}

grid = CanvasGrid(agent_portrayal, 20, 20, 500, 500)

model_params = {
    "airplanes": Slider("Airplanes", 10, 1, 100, 1),
    "airports": Slider("Airport", 3, 1, 100, 1),
    "width": 20,
    "height": 20,
}

server = ModularServer(
    TraficControler,
    [grid],
    "Airplane Traffic Controler",
    model_params
)

server.launch()
