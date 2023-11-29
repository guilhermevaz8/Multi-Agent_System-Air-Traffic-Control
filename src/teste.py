import random

from mesa import Agent, Model
from mesa.experimental import JupyterViz
from mesa.space import MultiGrid
from mesa.time import RandomActivation
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import CanvasGrid
from mesa_models.boltzmann_wealth_model.model import BoltzmannWealthModel


class MyAgent(Agent):
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


class AirportAgent(Agent):
    def __init__(self, unique_id, model, pos):
        super().__init__(unique_id, model)
        self.pos = pos

    def step(self):
        # Aeroportos são agentes fixos, não têm movimento
        pass


def agent_portrayal(agent):
    if isinstance(agent, MyAgent):
        return {"Shape": "circle", "Filled": "true", "Layer": 0, "Color": "red", "r": 0.5}
    elif isinstance(agent, AirportAgent):
        return {"Shape": "rect", "Filled": "true", "Layer": 0, "Color": "blue", "w": 0.5, "h": 0.5}


def add_airports(model, num_airports):
    for i in range(num_airports):
        x = model.random.randrange(model.grid.width)
        y = model.random.randrange(model.grid.height)
        airport = AirportAgent(f'airport_{i}', model, (x, y))
        model.grid.place_agent(airport, (x, y))
        model.schedule.add(airport)


class MyModel(Model):
    def __init__(self, N, width, height, num_airports):
        self.num_agents = N
        self.grid = MultiGrid(width, height, True)
        self.schedule = RandomActivation(self)

        # Criação dos agentes móveis
        for i in range(self.num_agents):
            a = MyAgent(i, self)
            self.schedule.add(a)
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(a, (x, y))

        # Adição dos aeroportos
        add_airports(self, num_airports)

    def step(self):
        self.schedule.step()


grid = CanvasGrid(agent_portrayal, 10, 10, 500, 500)

model_params = {
    "N": 10,
    "width": 10,
    "height": 10,
    "num_airports": 3  # Defina o número de aeroportos desejado
}

server = ModularServer(
    MyModel,
    [grid],
    "Simple Model",
    model_params
)

page = JupyterViz(
    BoltzmannWealthModel,
    model_params,
    measures=["Gini"],
    name="Money Model",
    agent_portrayal=agent_portrayal,
)

page


# server.port = 8521  # Escolha uma porta disponível
# server.launch()
