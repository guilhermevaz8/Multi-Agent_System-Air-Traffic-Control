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



class Avião(Agent):
    def __init__(self, jid, password, environment, position, last_airport):
        super().__init__(jid, password)
        print(f"pos = {position}, last_air = {last_airport}")
        self.environment = environment
        self.position = position
        self.grid=np.zeros((40,30))
        self.last_airport = last_airport
        self.generate_new_destination()
        self.phase = "levantar"
        self.count=0
        


    def generate_new_destination(self):
        destination = self.environment.generate_final_position(self.position,self.last_airport)  # Pass the initial position
        print(f"Destination chosen: {destination}")
        self.destination_airport = destination[0]
        self.final_position = destination[1]
        print(f"Initial position: {self.position}")
        print(f"Final position: {self.final_position}")
        print(f"Rota para {self.destination_airport} : {self.environment.routes[self.position][self.final_position]}")
        self.route = self.environment.routes[self.position][self.final_position]
    
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
        #self.add_behaviour(self.AircraftComs())
    
    class MainLoop(CyclicBehaviour):
        async def run(self):
            if self.agent.phase == "levantar":
                if self.agent.count==0:
                    self.agent.add_behaviour(self.agent.AircraftAirportDepart())
                    self.agent.count=1
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
            msg.to = f"{self.agent.last_airport}@localhost"
            #msg.sender = str(self.agent.jid)
            msg.body = "Permition to takeoff?"
            msg.set_metadata("request", "takeoff")
            await self.send(msg)
            await asyncio.sleep(1)
            
            msg_answer = await self.receive(timeout=10)
            if msg_answer:
                print(f"Message received: {msg_answer}")
                answer = msg_answer.metadata["request_answer"]
                if answer == "yes":
                    self.agent.phase = "moving"
                    await self.stop()

    class AircraftMoving(CyclicBehaviour):
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
                if msg_answer:
                    position = msg_answer["request_answer"].split(" ")
                    airplanes_position.append(position)

            for position in airplanes_position:
                self.agent.environment.update_grid(position)

            conflict = self.agent.check_route_conflict()
            while conflict==True:
                self.agent.route=a_star_search(self.agent.grid,self.agent.position,self.agent.final_position)
                conflict = self.agent.check_route_conflict()
            self.position = self.agent.route[0]


            msg = Message()
            msg.to = "gestor@localhost"
            msg.sender = str(self.agent.jid)
            msg.body = str(self.position)
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
            if msg_answer:
                answer = msg_answer.metadata["request_answer"]
                if answer == "yes":
                    self.agent.last_airport = self.agent.destination_airport
                    self.agent.generate_new_destination()
                    self.agent.phase = "levantar"
                    await self.agent.stop()


# Import necessary SPADE modules




class Environment:
    def __init__(self):
        self.aircraft_positions = {}
        self.grid = np.zeros((40,30))
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
        print(f"Airport positions: {self.airport_positions}")
        print(last_airport)
        tmp.pop(last_airport)
        available_airports = list(tmp.items())
        destination = random.choice(available_airports)
        print(f"Destination: {destination}")
        return destination
    
    def generate_all_routes(self):
        # Inicializar o dicionário de rotas

        # Obter todas as posições dos aeroportos
        airport_positions = list(self.airport_positions.values())

        # Criar rotas entre todos os pares de posições de aeroportos
        for start_pos in airport_positions:
            self.routes[start_pos] = {}
            for goal_pos in airport_positions:
                if start_pos != goal_pos:
                    # Usar o A* para calcular a rota
                    route = a_star_search(self.grid,start_pos, goal_pos)
                    self.routes[start_pos][goal_pos] = route


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





class AeroportoAgent(Agent):
    def __init__(self, jid, password, environment, position):
        super().__init__(jid, password)
        self.environment = environment
        self.isFree = True
        self.position = position
        self.badWeather = False     
        self.routes = {}
        self.sector = 0

    
    def change_isFree_status(self, value):
        self.isFree = value

    def rng_badWeather(self):
        rng = np.random.uniform()
        if rng >= 0.05:
            self.badWeather = False
        else:
            self.badWeather = True


    async def send_answer(self, msg_sender, answer, request_type):
        msg = Message()
        msg.to = str(msg.sender)
        msg.sender = str(self.agent.jid)
        msg.body = request_type + " rejected" if answer == "no" else request_type + " accepted"
        msg.set_metadata("request_answer",answer)
        msg.set_metadata("request_type", request_type)
        print(msg.body)
        await self.send(msg)


    async def setup(self):
        template=Template()
        template.to=str(self.jid)
        self.add_behaviour(self.AeroportoBehaviour(),template)

    class AeroportoBehaviour(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=10) # wait for a message for 10 seconds
            if msg:
                print("Message receivedaaaaaaa")
                print(f"Message received: {msg}")
                request_type = msg.metadata["request"]
                print(f"Request type: {request_type}")
                if request_type == "Landing":
                    answer = "no" if self.agent.badWeather or not self.agent.isFree else "yes"
                    if answer == "yes":
                        self.agent.change_isFree_status(False)
                else:
                    answer = "no" if self.agent.badWeather else "yes"
                    if answer == "yes":
                        self.agent.change_isFree_status(True)
                receiver=str(msg.sender)
                msg = Message()
                msg.to = receiver
                msg.sender = str(self.agent.jid)
                msg.body = request_type + " rejected" if answer == "no" else request_type + " accepted"
                msg.set_metadata("request_answer",answer)
                msg.set_metadata("request_type", request_type)
                print(msg.body)
                await self.send(msg)

                    



async def main():
    # Inicializar o ambiente
    print("Initializing environment...")
    environment = Environment()
    environment.generate_airport()
    environment.generate_all_routes()
    print(f"-> Airport positions: {environment.airport_positions}")

    print("-> Environment initialized successfully")
    
    # Verificar e criar o arquivo de posições dos aeroportos, se necessário
    if not os.path.exists("airport_positions.json"):
        with open("airport_positions.json", "w") as file:
            json.dump({}, file)

    # Verificar e criar o arquivo de posições dos aviões, se necessário
    if not os.path.exists("aircraft_positions.json"):
        with open("aircraft_positions.json", "w") as file:
            json.dump({}, file)

    #Inicializar e iniciar o agente gestor do espaço aereo
    print("Starting the agent gestorEspaco...")
    gestorEspaco = gestor_espaco("gestorEspaco_agent@localhost", "password", environment)
    await gestorEspaco.start(auto_register=True)
    print("Agent gestorEspaco started successfully")

    # Inicializar e iniciar o agente de controle do aeroporto 
    airport_agent = []
    i=0
    for key in environment.airport_positions:
        value=environment.airport_positions[key]
        print(f"Starting the agent airport_agent at position:{value}...")
        agentAirport = AeroportoAgent(f"{key.lower()}@localhost", "password", environment,value)
        airport_agent.append(agentAirport)
        print(f"Agent airport_agent at position:{agentAirport.position} created successfully")
        await agentAirport.start(auto_register=True)
        i+=1
    print("All airport agents started successfully OOOOOOOOOOOOOOOOOO")
    print(f"Airport positions created: {environment.airport_positions}")
    # Inicializar e iniciar os agentes de aeronaves
    aircraft_agents = []
    i=0
    for i in range(5):
        pos= random.choice(list(environment.airport_positions.items()))
        airport_color, position=pos
        print(f"Starting the agent airplane{i}...")
        agentAircraft = Avião(f"airplane{i}@localhost", "password", environment, position, airport_color)
        aircraft_agents.append(agentAircraft)
        await agentAircraft.start(auto_register=True)
        print(f"Agent airplane{i} started successfully")
    while True:
        await asyncio.sleep(1)  # Intervalo de atualização
    

if __name__ == "__main__":
    spade.run(main())
