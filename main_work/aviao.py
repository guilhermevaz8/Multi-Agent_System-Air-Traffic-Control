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




class Avião(Agent):
    def __init__(self, jid, password, environment, position, last_airport):
        super().__init__(jid, password)
        self.environment = environment
        self.position = position
        self.last_airport = last_airport
        self.environment=[]
        destination = self.environment.generate_final_position(self.position,self.last_airport)  # Pass the initial position
        self.destination_airport = destination[0]
        self.final_position = destination[1]



    async def setup(self):
        self.add_behaviour(self.AircraftInteraction())

    class AircraftInteraction(CyclicBehaviour):
        
        async def run(self):
            await self.send_instruction_to_atc(self.agent.position)

            await self.receive_pos()            # Aguardar instruções de rota do ATC
            #await self.receive_route_instructions()

            self.agent.update_position()

            if self.agent.position == self.agent.final_position:
                self.agent.get_new_destination()

            await asyncio.sleep(1)

        async def send_instruction_to_atc(self, position):
            # Enviar posição atual para o ATC
            msg = Message(to="atc_agent@localhost")
            msg.set_metadata("performative", "inform")
            msg.body = f"{self.id}+{self.agent.position}"
            await self.send(msg)

        async def receive_pos(self):    
             #Receber instruções de rota do ATC
             msg = await self.receive(timeout=1)  # Esperar por uma mensagem por um tempo limite
             if msg:
                count=0
                self.environment.grid= msg.body
                for i in range(len(self.environment.grid)):
                    for j in range(len(self.environment.grid[0])):
                        if self.environment.grid[i][j]==1:
                            count+=1
                print(count)
                # Atualizar a rota da aeronave conforme necessário

    def update_position(self):
        # Atualizar a posição da aeronave no ambiente
        self.grid=self.environment.grid
        self.route=a_star_search(self.environment.grid,self.position,self.final_position)
        self.position = (self.route[0][0],self.route[0][1])
        print(f"Aircraft {self.id} moving to {self.position}")
        self.environment.update_aircraft_position(self.id, self.position, self.destination_airport)

    def get_new_destination(self):
        self.last_airport = self.destination_airport
        destination = self.environment.generate_final_position(self.position,self.last_airport)  # Pass the initial position
        self.destination_airport = destination[0]
        self.final_position = destination[1]