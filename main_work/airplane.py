from imports import *

STATE_ONE = "takeoff"
STATE_TWO = "moving"
STATE_THREE = "landing"


class AircraftComs(CyclicBehaviour):
    async def run(self):
        msg = await self.receive(timeout=1)  # Esperar por uma mensagem por um tempo limite
        if msg:
            print(f"Message recieved: {msg}")
            request_type = msg.metadata["request"]
            if request_type == "position" and "request_answer" not in msg.metadata:
                msg_res = Message()
                msg_res.to = str(msg.sender)
                msg_res.sender = str(self.agent.jid)
                msg_res.body = "Sending my position"
                msg_res.set_metadata("request", "position")
                msg_res.set_metadata("request_answer", str(self.agent.position[0]) + " " + str(self.agent.position[1]))
                
                print(f"Message sent: {msg_res}")
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
        print("Asking to takeoff")
        msg = Message()
        msg.to = f"{self.agent.last_airport}@localhost"
        msg.body = "Permition to takeoff?"
        msg.set_metadata("request", "takeoff")
        print(f"Message sent: {msg}")
        await self.send(msg)
        msg_answer = await self.receive(timeout=10)
        if msg_answer and "request_answer" in msg_answer.metadata:
            print(f"Message received by {self.agent.jid}: {msg_answer}")
            answer = msg_answer.metadata["request_answer"]
            while answer == "no":
                print("Asking again to takeoff")
                print(f"Message sent: {msg}")
                await self.send(msg)
                msg_answer = await self.receive(timeout=10)
                answer = msg_answer.metadata["request_answer"]
        
        await asyncio.sleep(1)

        self.set_next_state(STATE_TWO)

    
class StateTwo(State):
    async def run(self):
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
            print(f"Message sent: {msg}")
            await self.send(msg)
            
            
        while len(self.agent.airplanes_positions) < 4:
            await asyncio.sleep(0.5)

        for position in self.agent.airplanes_positions:
            self.agent.update_grid(position)
        


        conflict = self.agent.check_route_conflict()
        while conflict==True:
            self.agent.route=a_star_search(self.agent.grid,self.agent.position,self.agent.final_position)
            conflict = self.agent.check_route_conflict()
            self.agent.flag=True
        if self.agent.flag==True:
            self.agent.save_route_to_file()
            self.agent.flag=False
        self.agent.grid=np.zeros((40,30))
        self.agent.position = self.agent.route[0]


        msg_up = Message()
        msg_up.to = "gestor@localhost"
        msg_up.sender = str(self.agent.jid)
        msg_up.body = str(self.agent.position)
        msg_up.set_metadata("request", "update_position")
        print(f"Message sent: {msg_up}")
        await self.send(msg_up)

        self.agent.save_route_to_file()
        self.agent.route=self.agent.route[1:]
        

        self.agent.airplanes_positions=[]

        await asyncio.sleep(1)
        if len(self.agent.route) ==1:
            print("Arriving to airport")
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
        print(f"Message sent: {msg}")
        await self.send(msg)
        msg_answer = await self.receive(timeout=10)
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
        self.destination_airport = destination[0]
        self.final_position = destination[1]
        self.environment.destinos[str(self.jid)]=self.destination_airport
        print(f"\tRoute to {self.destination_airport} : {self.environment.routes[self.position][self.final_position]}")
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
