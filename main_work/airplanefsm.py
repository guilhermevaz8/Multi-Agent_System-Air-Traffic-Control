from math import dist
import spade
from spade.agent import Agent
from spade.behaviour import FSMBehaviour, State, CyclicBehaviour
from spade.message import Message
import numpy as np
import asyncio
import json
from random import randint
import random


from a import a_star_search


STATE_ONE = "takeoff"
STATE_TWO = "moving"
STATE_THREE = "landing"

class Environment:
    def __init__(self):
        self.aircraft_positions = {}
        self.grid = np.zeros((40,30))
        self.airport_positions = {}
        self.routes = {}

    def generate_airport(self):
        DISTANCE_BET_AIRP = 15
        airport_colors = ["RED","GREEN"] 
        for i in range(len(airport_colors)):
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
    
    def generate_final_position(self, initial_position, last_airport):
        tmp = self.airport_positions.copy()
        tmp.pop(last_airport)
        available_airports = list(tmp.items())
        destination = random.choice(available_airports)
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






class ExampleFSMBehaviour(FSMBehaviour):
    async def on_start(self):
        print(f"Airplane FSM starting at initial state {self.current_state}")

    async def on_end(self):
        print(f"Airplane FSM finished at state {self.current_state}")
        await self.agent.stop()



class StateOne(State):
    async def run(self):
        print("Vou pedir para levantar")
        msg = Message()
        msg.to = f"{self.agent.last_airport}@localhost"
        msg.body = "Permition to takeoff?"
        msg.set_metadata("request", "takeoff")
        await self.send(msg)
        msg_answer = await self.receive(timeout=10)
        if msg_answer:
            print(f"Message received by {self.agent.jid}: {msg_answer}")
            answer = msg_answer.metadata["request_answer"]
            while answer == "no":
                print("Vou pedir outra vez para levantar")
                await self.send(msg)
                msg_answer = await self.receive(timeout=10)
                answer = msg_answer.metadata["request_answer"]
        
        self.set_next_state(STATE_TWO)

    
class StateTwo(State):
    async def run(self):
        print("Moving...\nMoving...")
        print(f"Aircraft {self.agent.jid} is moving!")
        jids_list=[]
        for i in range(2):
            jids_list.append(f"airplane{i}@localhost")

        jids_list.remove(str(self.agent.jid))
        
        airplanes_position = []
        
        for jid in jids_list:
            msg = Message()
            msg.to = jid
            msg.body = "What is your position?"
            msg.set_metadata("request", "position")

            await self.send(msg)
            msg_answer = await self.receive(timeout=10)
            if msg_answer:
                position = msg_answer.metadata["request_answer"].split(" ")
                airplanes_position.append(position)

        for position in airplanes_position:
            self.agent.update_grid(position)

        conflict = self.agent.check_route_conflict()
        print(f"Conflito: {conflict}")
        while conflict==True:
            self.agent.route=a_star_search(self.agent.grid,self.agent.position,self.agent.final_position)
            conflict = self.agent.check_route_conflict()
        
        print(f"Posicao antes: {self.agent.position}")
        self.agent.position = self.agent.route[0]
        print(f"Posicao depois: {self.agent.position}")


      

        self.agent.route=self.agent.route[1:]

        if len(self.agent.route) ==1:
            print("A chegar ao aeroporto")
            print("Vou pedir para aterrar")
            self.set_next_state(STATE_THREE)
            return

        self.set_next_state(STATE_TWO)



        

class StateThree(State):
    async def run(self):
        msg = Message()
        msg.to = f"{self.agent.last_airport}@localhost"
        msg.body = "Permition to land?"
        msg.set_metadata("request", "landing")
        await self.send(msg)
        msg_answer = await self.receive(timeout=10)
        print("Ola, estou depois do recieve")
        if msg_answer:
            print(f"Message received by {self.agent.jid}: {msg_answer}")
            answer = msg_answer.metadata["request_answer"]
            if answer == "no":
                self.set_next_state(STATE_TWO)
                return
        self.set_next_state(STATE_ONE)

class AirplaneFSMAgent(Agent):
    def __init__(self, jid, password, environment, position, last_airport):
        super().__init__(jid, password)
        self.environment = environment
        self.position = position
        self.grid=np.zeros((40,30))
        self.last_airport = last_airport
        self.generate_new_destination()
        self.count=0


    def generate_new_destination(self):
        destination = self.environment.generate_final_position(self.position,self.last_airport)  # Pass the initial position
        print(f"-> Destination chosen: {destination}")
        self.destination_airport = destination[0]
        self.final_position = destination[1]
        print(f"\tFinal position: {self.final_position}")
        print(f"\tRota para {self.destination_airport} : {self.environment.routes[self.position][self.final_position]}")
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
        fsm = ExampleFSMBehaviour()
        fsm.add_state(name=STATE_ONE, state=StateOne(), initial=True)
        fsm.add_state(name=STATE_TWO, state=StateTwo())
        fsm.add_state(name=STATE_THREE, state=StateThree())
        fsm.add_transition(source=STATE_ONE, dest=STATE_TWO)
        fsm.add_transition(source=STATE_TWO, dest=STATE_THREE)
        fsm.add_transition(source=STATE_THREE, dest=STATE_ONE)
        fsm.add_transition(source=STATE_THREE, dest=STATE_TWO)
        fsm.add_transition(source=STATE_TWO, dest=STATE_TWO)
        self.add_behaviour(fsm)

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
        if rng >= 0.5:
            self.badWeather = False
        else:
            self.badWeather = True


    async def send_answer(self, msg_sender, answer, request_type):
        msg = Message()
        msg.to = str(msg.sender)
        msg.sender = str(self.agent.jid)
        msg.body = request_type + " rejected" if answer == "no" else request_type + " accepted"
        msg.set_metadata("request_answer",answer)
        msg.set_metadata("request", request_type)
        await self.send(msg)


    async def setup(self):
        self.add_behaviour(self.AeroportoBehaviour())

    class AeroportoBehaviour(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=3) # wait for a message for 10 seconds
            if msg:
                print(f"Message received by {self.agent.jid}: {msg}")
                request_type = msg.metadata["request"]
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
                msg.set_metadata("request", request_type)
                await self.send(msg)


async def main():
    print("Initializing environment...")
    environment = Environment()
    environment.generate_airport()
    environment.generate_all_routes()
    print(f"-> Airport positions: {environment.airport_positions}")

    print("-> Environment initialized successfully")

    airport_agent = []
    i=0
    for key in environment.airport_positions:
        value=environment.airport_positions[key]
        print(f"Starting the agent airport_agent at position:{value}...")
        agentAirport = AeroportoAgent(f"{key.lower()}@localhost", "password", environment,value)
        airport_agent.append(agentAirport)
        print(f"Agent airport_agent at position:{agentAirport.position} created successfully")
        i+=1
    print(f"Airport positions created: {environment.airport_positions}")

    aircraft_agents = []
    i=0
    for i in range(2):
        pos= random.choice(list(environment.airport_positions.items()))
        airport_color, position=pos
        print(f"Starting the agent airplane{i}...")
        agentAircraft = AirplaneFSMAgent(f"airplane{i}@localhost", "password", environment, position, airport_color)
        aircraft_agents.append(agentAircraft)
        print(f"Agent airplane{i} started successfully")


    await asyncio.gather(
       airport_agent[0].start(auto_register=True),
       airport_agent[1].start(auto_register=True),
       aircraft_agents[0].start(auto_register=True),
       aircraft_agents[1].start(auto_register=True)
    )
    
    
if __name__ == "__main__":
    spade.run(main())