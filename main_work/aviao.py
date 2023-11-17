from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.template import Template
from spade.message import Message
import asyncio
import spade
import random
import json
import os
from a import a_star_search
from random import randint
from math import dist
import numpy as np
from gestor import Environment



class Avião(Agent):
    def __init__(self, jid, password, environment, position, last_airport):
        super().__init__(jid, password)
        self.environment = Environment()
        self.position = position
        self.grif=np.zeros((40,30))
        self.last_airport = last_airport
        self.generate_new_destination()
        self.phase = "levantar"

    def generate_new_destination(self):
        destination = self.environment.generate_final_position(self.position,self.last_airport)  # Pass the initial position
        self.destination_airport = destination[0]
        self.final_position = destination[1]
        self.route = self.environment.routes[self.last_airport][self.destination]
    
    def update_grid(self, position):
        for x in range(position[0] - 1, position[0] + 2):
            for y in range(position[1] - 1, position[1] + 2):
                if 0 <= x < len(self.grid) and 0 <= y < len(self.grid[0]):
                    self.grid[x][y] = 1  # Marcar a célula e as células adjacentes como ocupadas

    def check_route_conflict(self):
        position=self.route[0]
        if self.grid[position[0]][position[1]] == 1:
            return True
        return False
        
    async def setup(self):
        self.add_behaviour(self.MainLoop())
        self.agent.add_behaviour(self.agent.AircraftComs())
    
    class MainLoop(CyclicBehaviour):
        async def run(self):
            if self.agent.phase == "levantar":
                self.agent.add_behaviour(self.agent.AircraftAirportDepart())
            elif self.agent.phase == "moving":
                self.agent.add_behaviour(self.agent.AircraftMoving())
            elif self.agent.phase == "landing":
                self.agent.add_behaviour(self.agent.AircraftAirportArrive())
            
            
    class AircraftComs(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=1)  # Esperar por uma mensagem por um tempo limite
            if msg:
                # Se uma mensagem é recebida, responder com a posição atual
                response = Message()
                response.to = str(msg.sender)
                response.sender = str(self.agent.jid)
                response.body = f"Current position: {self.agent.position}"
                response.set_metadata("response_type", "position")
                await self.send(response)

    class AircraftAirportDepart(CyclicBehaviour):
        async def run(self):
            msg = Message()
            msg.to = self.agent.last_airport
            msg.sender = str(self.agent.jid)
            msg.body = "Permition to takeoff?"
            msg.set_metadata("request_type", "Takeoff")

            await self.send(msg)

            msg_answer = await self.receive()
            answer = msg_answer.metadata["request_answer"]
            if answer == "yes":
                self.agent.phase = "moving"
                await self.agent.stop()

    class AircraftMoving(CyclicBehaviour):
        print("CARALHO MA FODA")  
        async def run(self):
            jids_list = []
            for i in range(5):
                jids_list.append(f"airplane{i}@localhost")

            airplanes_position = []

            for jid in jids_list:
                msg = Message()
                msg.to = jid
                msg.sender = str(self.agent.jid)
                msg.body = "What is your position?"
                msg.set_metadata("request_type", "position")

                await self.send(msg)
                msg_answer = await self.receive()

                position = msg_answer["request_answer"].split(" ")
                airplanes_position.append(position)

            for position in airplanes_position:
                self.agent.environment.update_grid(position)

            conflict = self.agent.check_route_conflict()
            while conflict==False:
                self.agent.route=a_star_search(self.environment.grid,self.agent.position,self.agent.final_position)
                conflict = self.agent.check_route_conflict()
            self.position = self.agent.route[0]


            msg = Message()
            msg.to = "gestor@localhost"
            msg.sender = str(self.agent.jid)
            msg.body = self.position
            msg.set_metadata("request_type", "update_position")
            await self.send(msg)

            self.agent.route=self.agent.route[1:]

            if len(self.agent.route) ==1:
                self.agent.phase = "landing"
                await self.agent.stop()

            await asyncio.sleep(1)


    class AircraftAirportArrive(CyclicBehaviour):
        async def run(self):
            msg = Message()
            msg.to = self.agent.destination_airport
            msg.sender = str(self.agent.jid)
            msg.body = "Permition?"
            msg.set_metadata("request_type", "Landing")

            await self.send(msg)

            msg_answer = await self.receive()
            answer = msg_answer.metadata["request_answer"]
            if answer == "yes":
                self.agent.last_airport = self.agent.destination_airport
                self.agent.generate_new_destination()
                self.agent.phase = "levantar"
                await self.agent.stop()
