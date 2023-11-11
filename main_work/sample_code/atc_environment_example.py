# Import necessary SPADE modules
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.template import Template
from spade.message import Message
import asyncio
import spade
import random
import json

class Environment:
    def __init__(self):
        self.aircraft_positions = {}
        self.weather_conditions = {}
        self.runway_status = {}
        self.airport_positions = [(100, 100), (300, 500), (600, 300)]

    def update_aircraft_position(self, aircraft_id, position):
        self.aircraft_positions[aircraft_id] = position

    def move_aircraft(self):
        for aircraft_id, position in self.aircraft_positions.items():
            if isinstance(position, tuple) and len(position) == 2:
                new_x = position[0] + random.randint(-10, 10)
                new_y = position[1] + random.randint(-10, 10)
                self.aircraft_positions[aircraft_id] = (new_x, new_y)
        with open("aircraft_positions.json", "w") as file:
            json.dump(self.aircraft_positions, file)

    def update_weather(self, weather_data):
        self.weather_conditions = weather_data
        print(self.weather_conditions)

    def update_runway_status(self, runway_id, status):
        self.runway_status[runway_id] = status
        print(self.runway_status)

    def get_aircraft_positions(self):
        return self.aircraft_positions

    def get_weather_data(self):
        # Implementar a lógica para obter dados meteorológicos
        # Por simplicidade, podemos retornar um valor fixo ou gerado aleatoriamente
        return {"wind": random.choice(["N", "S", "E", "W"]), "visibility": random.choice(["good", "moderate", "poor"])}

    def get_runway_status(self):
        # Implementar a lógica para obter o status da pista
        # Por simplicidade, podemos retornar um valor fixo ou gerado aleatoriamente
        return {"runway1": random.choice(["free", "occupied", "maintenance"])}


class AirTrafficControlAgent(Agent):
    def __init__(self, jid, password, environment):
        super().__init__(jid, password)
        self.environment = environment

    async def setup(self):
        # Define a behavior to perceive and interact with the environment
        class EnvironmentInteraction(CyclicBehaviour):
            async def run(self):
                print("EnvironmentInteraction behavior is running")
                # Perceive environment data - you can use ACL messages or other means
                aircraft_positions = self.get_aircraft_position()
                weather_data = self.get_weather_data()
                runway_status = self.get_runway_status()

                # Make decisions based on perceptions and update the environment
                # Example: Check for conflicts and send instructions to aircraft
                await asyncio.sleep(10)

            def get_aircraft_position(self):
            # Implementar a lógica para recuperar as posições das aeronaves do ambiente
                return self.agent.environment.get_aircraft_positions()

            def get_weather_data(self):
                # Implementar a lógica para recuperar os dados meteorológicos do ambiente
                return self.agent.environment.get_weather_data()

            def get_runway_status(self):
                # Implementar a lógica para recuperar o status da pista do ambiente
                return self.agent.environment.get_runway_status()

        # Add the behavior to the agent
        self.add_behaviour(EnvironmentInteraction())


class AircraftAgent(Agent):
    def __init__(self, jid, password, environment, pos):
        super().__init__(jid, password)
        self.environment = environment
        tmp=str.split(jid,"@")
        tmp2=str.split(tmp[0],"e")
        self.id=int(tmp2[1])
        print(self.id)
        self.environment.update_aircraft_position(self.id,pos)

    async def setup(self):
        # Define a behavior to interact with the environment and air traffic control
        class AircraftInteraction(CyclicBehaviour):
            async def run(self):
                print("AircraftInteraction behavior is running")
                # Atualizar posição da aeronave
                new_pos = (random.randint(0, 1000), random.randint(0, 1000))
                self.agent.environment.update_aircraft_position(self.agent.id, new_pos)
                print("AircraftInteraction behavior is running")
                # Perceive environment data
                # Communicate with air traffic control
                print(new_pos)
                await self.send_instruction_to_atc(new_pos)
                await asyncio.sleep(3)

            def get_aircraft_position(self):
                    # Acessar o objeto de ambiente para recuperar a posição da aeronave
                    return self.agent.environment.aircraft_positions[self.agent.id]

            async def send_instruction_to_atc(self, position):
                # Create an ACL message to send data to the air traffic control agent
                msg = Message(to="atc_agent@localhost")  # Replace with the correct ATC agent JID
                msg.set_metadata("performative", "inform")
                msg.body = f"Aircraft at position {position} requesting instructions."

                # Send the message
                await self.send(msg)

        # Add the behavior to the agent
        self.add_behaviour(AircraftInteraction())


async def main():
    atc_environment = Environment()

    # Inicializar e iniciar o agente de controle de tráfego aéreo
    atc_agent = AirTrafficControlAgent("atc_agent@localhost", "password", atc_environment)
    await atc_agent.start(auto_register=True)

    # Inicializar e iniciar os agentes de aeronaves
    aircraft_agents = []
    for i in range(5):
        pos = (random.randint(0, 100), random.randint(0, 100))
        agent = AircraftAgent(f"airplane{i}@localhost", "password", atc_environment, pos)
        aircraft_agents.append(agent)
        await agent.start(auto_register=True)

    # Loop para atualizar as posições dos aviões
    while True:
        atc_environment.move_aircraft()
        await asyncio.sleep(1)

if __name__ == "__main__":
    spade.run(main())