# Import necessary SPADE modules
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.template import Template
from spade.message import Message
import spade
import asyncio
import json
import os 
import random
from aeroporto import AeroportoAgent
from gestor import Environment, gestor_espaco
from aviao import Avião

async def main():
    # Inicializar o ambiente
    print("Initializing environment...")
    environment = Environment()
    environment.generate_airport()
    print(environment.airport_positions)

    print("Environment initialized successfully")
    
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
    for value in environment.airport_positions.values():
        print(f"Starting the agent airport_agent{value}...")
        print("Airport position: ")
        print(environment.airport_positions)
        agentAirport = AeroportoAgent("airport_agent{i}@localhost", "password", environment,value)
        airport_agent.append(agentAirport)
        print("Agent airport_agent{value} started successfully")
        await agentAirport.start(auto_register=True)
    print("All airport agents started successfully OOOOOOOOOOOOOOOOOO")
    # Inicializar e iniciar os agentes de aeronaves
    aircraft_agents = []
    for i in range(5):
        pos= random.choice(list(environment.airport_positions.values()))
        x,y=pos
        print(f"Starting the agent airplane{i}...")
        agentAircraft = Avião(f"airplane{i}@localhost", "password", environment, x, y)
        aircraft_agents.append(agentAircraft)
        await agentAircraft.start(auto_register=True)
        print("Agent airplane{i} started successfully")
    while True:
        await asyncio.sleep(1)  # Intervalo de atualização
    

if __name__ == "__main__":
    spade.run(main())