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
from a import a_star_search
from random import randint
from math import dist
import numpy as np



class Environment:
    def __init__(self):
        self.grid=np.zeros((40,30))
        self.aircraft_positions = {}
        self.weather_conditions = {}
        self.runway_status = {}
        self.airport_positions = {}
        self.conflict_zones = []  # Zonas onde podem ocorrer conflitos

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
        with open("airport_positions.json", "w") as file:
            print("Saving airport positions to JSON")
            json.dump(self.airport_positions, file)
            print("Airport Positions Saved as JSON File")
    
    def generate_final_position(self, initial_position):
        available_airports = list(self.airport_positions.values())
        available_airports.remove(initial_position)  # Remove the initial position from the available options
        final_position = random.choice(available_airports)
        return final_position

    def update_aircraft_position(self, aircraft_id, position):
        self.aircraft_positions[aircraft_id] = position
        self.save_aircraf_positions()
        self.detect_conflicts()

    def move_aircraft(self):
        for aircraft_id, position in self.aircraft_positions.items():
            if isinstance(position, tuple) and len(position) == 2:
                new_x = position[0]
                new_y = position[1] 
                self.aircraft_positions[aircraft_id] = (new_x, new_y)
            #print(f"Moved aircraft {aircraft_id} to position {self.aircraft_positions[aircraft_id]}")
    
    def save_aircraf_positions(self):
        with open("aircraft_positions.json", "w") as file:
            print("Saving aircraft postions to JSON")
            json.dump(self.aircraft_positions, file)
            print("Aircraft Postions Saved to JSON")

    def detect_conflicts(self):
        self.conflict_zones = []
        for id1, pos1 in self.aircraft_positions.items():
            for id2, pos2 in self.aircraft_positions.items():
                if id1 != id2 and self.is_close(pos1, pos2):
                    self.conflict_zones.append((id1, id2))

    def is_close(self, pos1, pos2, min_distance=10):
        # Determinar se duas aeronaves estão perigosamente próximas
        return abs(pos1[0] - pos2[0]) < min_distance and abs(pos1[1] - pos2[1]) < min_distance

    def suggest_routes(self, aircraft_id):
        # Verificar se a aeronave está em uma zona de conflito
        for conflict in self.conflict_zones:
            if aircraft_id in conflict:
                # Gerar uma rota alternativa
                return self.generate_alternative_route(aircraft_id)
        return []

    def generate_alternative_route(self, aircraft_id):
        pos=self.aircraft_positions[aircraft_id]
        goal=self.airport_positions["MAGENTA"]
        path = a_star_search(self.grid,pos,goal)
        return (path)

    def update_weather(self, weather_data):
        self.weather_conditions = weather_data

    def update_runway_status(self, runway_id, status):
        self.runway_status[runway_id] = status

    def get_aircraft_positions(self):
        return self.aircraft_positions

    def get_weather_data(self):
        return {"wind": random.choice(["N", "S", "E", "W"]), "visibility": random.choice(["good", "moderate", "poor"])}

    def get_runway_status(self):
        return {"runway1": random.choice(["free", "occupied", "maintenance"])}


class AirTrafficControlAgent(Agent):
    def __init__(self, jid, password, environment):
        super().__init__(jid, password)
        self.environment = environment
    
    async def setup(self):
        self.add_behaviour(self.EnvironmentInteraction())

    class EnvironmentInteraction(CyclicBehaviour):
        first=False

        async def run(self):
            print("EnvironmentInteraction behavior is running")
            if (self.first != True):
                # Atualizar a posição das aeronaves
                self.agent.environment.move_aircraft()
                first=True
            # Perceber os dados do ambiente
            aircraft_positions = self.agent.environment.get_aircraft_positions()
            weather_data = self.agent.environment.get_weather_data()
            runway_status = self.agent.environment.get_runway_status()

            # Detectar conflitos
            self.agent.environment.detect_conflicts()

            # Resolver conflitos e comunicar com as aeronaves
            for conflict_zone in self.agent.environment.conflict_zones:
                for aircraft_id in conflict_zone:
                    new_route = self.agent.environment.suggest_routes(aircraft_id)
                    if new_route:
                        await self.send_route_instructions(aircraft_id, new_route)
            

            await asyncio.sleep(2)

        async def send_route_instructions(self, aircraft_id, new_route):
            # Criar uma mensagem ACL
            msg = Message(to=f"airplane{aircraft_id}@localhost")  # Substituir pelo JID correto do agente da aeronave
            msg.set_metadata("performative", "inform")
            msg.set_metadata("language", "English")
            msg.set_metadata("ontology", "AirTrafficControl")

            # Incluir as instruções de rota na mensagem
            msg.body = f"New route instructions: {new_route}"

            # Enviar a mensagem
            await self.send(msg)
            #print(f"Sent new route to aircraft {aircraft_id}: {new_route}")



class AircraftAgent(Agent):
    def __init__(self, jid, password, environment, pos):
        super().__init__(jid, password)
        self.environment = environment
        self.id = self.extract_id(jid)
        self.position = pos
        self.route=[]
        self.final_position = self.environment.generate_final_position(pos)  # Pass the initial position
        self.environment.update_aircraft_position(self.id, pos)

    def extract_id(self, jid):
        # Extrair o ID do JID do agente
        parts = jid.split("@")[0].split("e")
        return int(parts[1]) if len(parts) > 1 else 0

    async def setup(self):
        self.add_behaviour(self.AircraftInteraction())

    class AircraftInteraction(CyclicBehaviour):
        async def run(self):
            
            
            # Atualizar a posição da aeronave

            # Comunicar posição atual para o ATC
            #await self.send_instruction_to_atc(self.agent.position)

            # Aguardar instruções de rota do ATC
            #await self.receive_route_instructions()

            self.agent.update_position()

            await asyncio.sleep(1)

        #async def send_instruction_to_atc(self, position):
            # Enviar posição atual para o ATC
         #   msg = Message(to="atc_agent@localhost")
          #  msg.set_metadata("performative", "inform")
           # msg.body = f"Aircraft {self.agent.id} at position {position} requesting instructions."
            #await self.send(msg)

        #async def receive_route_instructions(self):
            # Receber instruções de rota do ATC
         #   msg = await self.receive(timeout=1)  # Esperar por uma mensagem por um tempo limite
          #  if msg:
           #     self.route= msg.body
            #    print(f"Received new route instructions: {self.route}")
                # Atualizar a rota da aeronave conforme necessário

    def update_position(self):
        # Atualizar a posição da aeronave no ambiente
        i=0
        #print(self.environment.grid)
        #print(self.position)
        #print(self.environment.airport_positions["WHITE"])
        self.grid=self.environment.grid
        self.route=a_star_search(self.environment.grid,self.position,self.final_position)
        print(self.position)
        self.position = (self.route[0][0],self.route[0][1])
        print(self.route)
        print(self.position)
        self.environment.update_aircraft_position(self.id, self.position)


async def main():
    # Inicializar o ambiente
    atc_environment = Environment()
    
    atc_environment.generate_airport()

    for airport in atc_environment.airport_positions:
        print(airport)

    # Verificar e criar o arquivo de posições dos aeroportos, se necessário
    if not os.path.exists("airport_positions.json"):
        with open("airport_positions.json", "w") as file:
            json.dump({}, file)

    # Verificar e criar o arquivo de posições dos aviões, se necessário
    if not os.path.exists("aircraft_positions.json"):
        with open("aircraft_positions.json", "w") as file:
            json.dump({}, file)

    # Inicializar e iniciar o agente de controle de tráfego aéreo
    atc_agent = AirTrafficControlAgent("atc_agent@localhost", "password", atc_environment)
    await atc_agent.start(auto_register=True)

    # Inicializar e iniciar os agentes de aeronaves
    aircraft_agents = []
    for i in range(5):
        airport_positions = atc_environment.airport_positions.values()
        pos = random.choice(list(airport_positions))
        #print(airport_positions)
        #print(pos)
        agent = AircraftAgent(f"airplane{i}@localhost", "password", atc_environment, pos)
        aircraft_agents.append(agent)
        await agent.start(auto_register=True)


    atc_environment.save_aircraf_positions()
    # Loop principal
    for aircraft_agent in aircraft_agents:
        print("--------------------------------")
        print(aircraft_agent.final_position, aircraft_agent.position)


    while True:
        await asyncio.sleep(1)  # Intervalo de atualização
    

if __name__ == "__main__":
    spade.run(main())