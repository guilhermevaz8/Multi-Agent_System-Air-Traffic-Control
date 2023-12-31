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
from spade.template import Template
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
        self.destinos={}

    def generate_airport(self):
        DISTANCE_BET_AIRP = 15
        airport_colors = ["RED","GREEN","YELLOW","WHITE","MAGENTA"] 
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

        # Criar rotas entre todos os pares
        #  de posições de aeroportos
        for start_pos in airport_positions:
            self.routes[start_pos] = {}
            for goal_pos in airport_positions:
                if start_pos != goal_pos:
                    # Usar o A* para calcular a rota
                    print(f"pos start: {start_pos}, pos_final : {goal_pos}")
                    route = a_star_search(self.grid,start_pos, goal_pos)
                    self.routes[start_pos][goal_pos] = route


    def update_position(self,aircraf_id,x,y):
        self.aircraft_positions[aircraf_id]=[x,y]

    
    def save_aircraft_positions(self):
        with open("aircraft_positions.json", "w") as file:
            save_data = {}
            for key, destino in self.destinos.items():
                save_data[key]=(destino,self.aircraft_positions[key])
            print("Saving aircraft positions to JSON")
            json.dump(save_data, file)
            print("Aircraft Positions Saved to JSON")
            print("-------------------------------")

    def get_aircraft_positions(self):
        return self.aircraft_positions




class AircraftComs(CyclicBehaviour):
    async def run(self):
        msg = await self.receive(timeout=1)  # Esperar por uma mensagem por um tempo limite
        if msg:
            print(f"Recebi: {msg}")
            request_type = msg.metadata["request"]
            if request_type == "position" and "request_answer" not in msg.metadata:
                msg_res = Message()
                msg_res.to = str(msg.sender)
                msg_res.sender = str(self.agent.jid)
                msg_res.body = "Sending my position"
                msg_res.set_metadata("request", "position")
                msg_res.set_metadata("request_answer", str(self.agent.position[0]) + " " + str(self.agent.position[1]))
                
                print(f"Enviei: {msg_res}")
                await self.send(msg_res)
            elif "request_answer" in msg.metadata:
                pos = [int(x) for x in msg.metadata["request_answer"].split(" ")]
                
                self.agent.airplanes_positions.append(pos)



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
        if msg_answer and "request_answer" in msg_answer.metadata:
            print(f"Message received by {self.agent.jid}: {msg_answer}")
            answer = msg_answer.metadata["request_answer"]
            while answer == "no":
                print("Vou pedir outra vez para levantar")
                await self.send(msg)
                msg_answer = await self.receive(timeout=10)
                answer = msg_answer.metadata["request_answer"]
        
        await asyncio.sleep(1)

        self.set_next_state(STATE_TWO)

    
class StateTwo(State):
    async def run(self):
        print("Moving...\nMoving...")
        print(f"Aircraft {self.agent.jid} is moving!")
        jids_list=[]
        for i in range(5):
            jids_list.append(f"airplane{i}@localhost")

        jids_list.remove(str(self.agent.jid))
        
        
        for jid in jids_list:
            msg = Message()
            msg.to = jid
            msg.sender = str(self.agent.jid)
            msg.body = "What is your position?"
            msg.set_metadata("request", "position")
            print(f"Mandei mensagem: {msg}")
            await self.send(msg)
            
            
        while len(self.agent.airplanes_positions) < 4:
            print("ola")
            print(self.agent.airplanes_positions)
            await asyncio.sleep(0.5)

        print(f" ola {self.agent.airplanes_positions}")

        for position in self.agent.airplanes_positions:
            self.agent.update_grid(position)
        

        print("ola dois")

        conflict = self.agent.check_route_conflict()
        print(f"Conflito: {conflict}")
        while conflict==True:
            print(f"vai errar : {self.agent.final_position}")
            self.agent.route=a_star_search(self.agent.grid,self.agent.position,self.agent.final_position)
            print("depois do a star")
            conflict = self.agent.check_route_conflict()
            self.agent.flag=True
        if self.agent.flag==True:
            self.agent.save_route_to_file()
            self.agent.flag=False
        self.agent.grid=np.zeros((40,30))
        print(f"Posicao antes: {self.agent.position}")
        self.agent.position = self.agent.route[0]
        print(f"Posicao depois: {self.agent.position}")


        msg_up = Message()
        msg_up.to = "gestor@localhost"
        msg_up.sender = str(self.agent.jid)
        msg_up.body = str(self.agent.position)
        msg_up.set_metadata("request", "update_position")
        await self.send(msg_up)

        self.agent.save_route_to_file()
        self.agent.route=self.agent.route[1:]
        

        self.agent.airplanes_positions=[]

        await asyncio.sleep(1)
        if len(self.agent.route) ==1:
            print("A chegar ao aeroporto")
            print("Vou pedir para aterrar")
            self.set_next_state(STATE_THREE)
            return

        self.set_next_state(STATE_TWO)



        

class StateThree(State):
    async def run(self):
        self.agent.position = self.agent.route[0]
        self.agent.save_route_to_file()
        self.agent.route=self.agent.route[1:]
        self.agent.environment.update_position(str(self.agent.jid), self.agent.position[0],self.agent.position[1]) 
        self.agent.environment.save_aircraft_positions()
        msg = Message()
        msg.to = f"{self.agent.last_airport}@localhost"
        msg.body = "Permition to land?"
        msg.set_metadata("request", "landing")
        await self.send(msg)
        msg_answer = await self.receive(timeout=10)
        print("Ola, estou depois do recieve")
        if msg_answer and "request_answer" in msg_answer.metadata:
            print(f"Message received by {self.agent.jid}: {msg_answer}")
            answer = msg_answer.metadata["request_answer"]
            if answer == "no":
                self.set_next_state(STATE_TWO)
                return
        self.agent.last_airport = self.agent.destination_airport
        self.agent.generate_new_destination()
        self.agent.save_route_to_file()
        self.set_next_state(STATE_ONE)

class AirplaneFSMAgent(Agent):
    def __init__(self, jid, password, environment, position, last_airport):
        super().__init__(jid, password)
        self.environment = environment
        self.position = position
        self.grid=np.zeros((40,30))
        self.last_airport = last_airport
        self.generate_new_destination()
        self.save_route_to_file()
        self.count=0
        self.flag=False
        self.airplanes_positions = []
        self.environment.update_position(str(self.jid),self.position[0],self.position[1])


    def generate_new_destination(self):
        destination = self.environment.generate_final_position(self.position,self.last_airport)  # Pass the initial position
        print(f"-> Destination chosen: {destination}")
        self.destination_airport = destination[0]
        self.final_position = destination[1]
        self.environment.destinos[str(self.jid)]=self.destination_airport
        print(f"\tFinal position: {self.final_position}")
        print(f"AP: {self.environment.airport_positions}")
        print(f"\tRota para {self.destination_airport} : {self.environment.routes[self.position][self.final_position]}")
        self.route = self.environment.routes[self.position][self.final_position]
    
    
    def save_route_to_file(self, file_name="aircraft_routes.json"):
    # Carrega os dados existentes do arquivo, se ele existir
        try:
            with open(file_name, 'r') as file:
                data = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            data = {}
        # Adiciona a nova rota ao dicionário de dados
        new_entry =self.route
        data[str(self.jid)] = new_entry  # Você pode mudar a chave conforme necessário

        # Escreve os dados atualizados de volta ao arquivo
        with open(file_name, 'w') as file:
            json.dump(data, file)
        print(f"Route added to {file_name}")
        

    
    def update_grid(self, position):
        position_list = tuple(position)
        airport_pos = list(self.environment.airport_positions.values())
        if position_list in airport_pos:
            return
        for x in range(position[0] - 1, position[0] + 2):
            for y in range(position[1] - 1, position[1] + 2):
                if 0 <= x < len(self.grid) and 0 <= y < len(self.grid[0]):
                    self.grid[x][y] = 1  # Marcar a célula e as células adjacentes como ocupadas
        for pos in airport_pos:
            self.grid[pos[0],pos[1]]=0

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
        t = Template()
        t.set_metadata("request","position")
        self.add_behaviour(AircraftComs(), template=t)

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
        msg.to = str(msg_sender)
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
                if request_type == "landing":
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

class GestorEspaco(Agent):
    def __init__(self, jid, password, environment):
        super().__init__(jid, password)
        self.environment = environment
        self.count=0

    async def setup(self):
        t=Template()
        t.set_metadata("request","update_position")
        self.add_behaviour(self.ReceivePositionUpdates(), template=t)

    class ReceivePositionUpdates(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=5)  # Esperar por uma mensagem por um tempo limite
            if msg:
                print(f"posicao recebida: {msg.body}")
                position = msg.body.replace('(', '').replace(')', '').replace(' ', '')
                x_str, y_str = position.split(',')
                x = int(x_str)
                y = int(y_str)
                self.agent.environment.update_position(str(msg.sender), x,y) 
                self.agent.count+=1
            if self.agent.count==5:
                self.agent.count=0
                self.agent.environment.save_aircraft_positions()




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
    possible_air = list(environment.airport_positions.items())
    for i in range(5):
        pos= random.choice(possible_air)
        possible_air.remove(pos)
        airport_color, position=pos
        print(f"Starting the agent airplane{i}...")
        agentAircraft = AirplaneFSMAgent(f"airplane{i}@localhost", "password", environment, position, airport_color)
        aircraft_agents.append(agentAircraft)
        print(f"Agent airplane{i} started successfully")


    gestor = GestorEspaco("gestor@localhost","password",environment)


    await asyncio.gather(
        airport_agent[0].start(auto_register=True),
        airport_agent[1].start(auto_register=True),
        airport_agent[2].start(auto_register=True),
        airport_agent[3].start(auto_register=True),
        airport_agent[4].start(auto_register=True),
        aircraft_agents[0].start(auto_register=True),
        aircraft_agents[1].start(auto_register=True),
        aircraft_agents[2].start(auto_register=True),
        aircraft_agents[3].start(auto_register=True),
        aircraft_agents[4].start(auto_register=True),
        gestor.start(auto_register=True)
    )
    
    
if __name__ == "__main__":
    spade.run(main())