# Import necessary SPADE modules
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.template import Template
from spade.message import Message
import asyncio
import spade
import random
import json
import os
from random import randint
from math import dist
import numpy as np



class Environment:
    def __init__(self):
        self.aircraft_positions = {}
        self.airport_positions = {}
        self.routes = {}

    def generate_airport(self):
        DISTANCE_BET_AIRP = 15
        airport_colors = ["RED","GREEN","YELLOW","MAGENTA","WHITE"] 
        for i in range(5):
            pos = (randint(2,38),randint(2,28))
            if self.airport_positions == {}:
                self.airport_positions[airport_colors[i]]=pos
                continue
            mindist=False
            while not mindist:
                flag=True
                for key,tmp in self.airport_positions.items():
                    x=tmp[0]
                    y=tmp[1]
                    while dist(pos,(x,y))<=DISTANCE_BET_AIRP:
                        flag=False
                        pos = (randint(2,38),randint(2,28))
                if flag:
                    mindist=True
                else:
                    mindist=False
            self.airport_positions[airport_colors[i]]=pos
            #self.grid[pos[0]][pos[1]]=1
            print(self.airport_positions)
        with open("airport_positions.json", "w") as file:
            print("Saving airport positions to JSON")
            json.dump(self.airport_positions, file)
            print("Airport Positions Saved as JSON File")
    
    def generate_final_position(self, initial_position, last_airport):
        tmp = self.airport_positions.copy()
        tmp.pop(last_airport)
        available_airports = list(tmp.items())
        destination = random.choice(available_airports)
        return destination


    def update_position(self,aircraf_id,x,y):
        self.aircraft_positions[aircraf_id]=[x,y]

    
    def save_aircraft_positions(self, aircrafr_id):
        with open("aircraft_positions.json", "w") as file:
            print(f"Saving aircraft {aircrafr_id} position ({self.aircraft_positions[aircrafr_id]}) to JSON")
            json.dump(self.aircraft_positions, file)
            print(f"Aircraft {aircrafr_id} Position Saved to JSON")
            print("-------------------------------")

    def get_aircraft_positions(self):
        return self.aircraft_positions





class gestor_espaco(Agent):
    def __init__(self, jid, password, environment):
        super().__init__(jid, password)
        self.environment = environment
        self.count=0

    async def setup(self):
        self.add_behaviour(self.ReceivePositionUpdates())

    class ReceivePositionUpdates(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=1)  # Esperar por uma mensagem por um tempo limite
            if msg:
                position = position.replace('(', '').replace(')', '').replace(' ', '')
                x_str, y_str = position.split(',')
                x = int(x_str)
                y = int(y_str)
                self.environment.update_position(str(self.jid), x,y) 
                self.agent.count+=1
            if self.agent.count==5:
                self.agent.count=0
                self.environment.save_aircraft_positions()
    