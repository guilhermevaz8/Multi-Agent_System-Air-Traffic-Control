from mesa import Model
from mesa.space import MultiGrid
from mesa.time import RandomActivation

from agent import *

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

        total = len(self.airport_coordinates) # Obtem a quantidade de aeroportos

        # Criação dos agentes móveis
        for i in range(self.airplanes):
            dest = list(self.airport_coordinates[(i+1)%total])
            origin = list(self.airport_coordinates[i%total])
            a = Airplane(i, self,origin,dest)
            self.schedule.add(a)
            self.grid.place_agent(a, origin)

    def step(self):
        self.schedule.step()
