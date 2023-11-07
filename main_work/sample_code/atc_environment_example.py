# Import necessary SPADE modules
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.template import Template
from spade.message import Message
import asyncio
import spade
import random


# Define the Environment class to represent the air traffic control environment
class Environment:
    def __init__(self):
        # Initialize environment variables, e.g., aircraft positions, weather, runways, etc.
        self.aircraft_positions = {}
        self.weather_conditions = {}
        self.runway_status = {}

    def update_aircraft_position(self, aircraft_id, position):
        self.aircraft_positions[aircraft_id] = position
        print(self.aircraft_positions)  

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
                # Perceive environment data
                aircraft_position = self.get_aircraft_position()

                # update aircraft position
                self.agent.environment.update_aircraft_position(1, 3000)

                # Communicate with air traffic control
                await self.send_instruction_to_atc(aircraft_position)
                await asyncio.sleep(10)

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
    # Create and initialize the environment
    atc_environment = Environment()

    atc_agent = AirTrafficControlAgent("atc_agent@localhost", "password", atc_environment)
    await atc_agent.start(auto_register=True)

    aircraft_agents=[0]*5
    for i in range(5):
        pos=(random.randint(0,100),random.randint(0,100))
        aircraft_agents[i] = AircraftAgent(f"airplane{i}@localhost", "password", atc_environment, pos)
        print(f"Agente {i} criado com posicao {pos}")

    for i in range(5):
        await aircraft_agents[i].start(auto_register=True)
    

    
    
if __name__ == "__main__":
    spade.run(main())
