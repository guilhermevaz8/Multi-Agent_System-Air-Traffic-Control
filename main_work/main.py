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
    environment = Environment()
    
    # Verificar e criar o arquivo de posições dos aeroportos, se necessário
    if not os.path.exists("airport_positions.json"):
        with open("airport_positions.json", "w") as file:
            json.dump({}, file)

    # Verificar e criar o arquivo de posições dos aviões, se necessário
    if not os.path.exists("aircraft_positions.json"):
        with open("aircraft_positions.json", "w") as file:
            json.dump({}, file)

    #Inicializar e iniciar o agente gestor do espaço aereo
    gestorEspaco = gestor_espaco("gestorEspaco_agent@localhost", "password", environment)
    await gestorEspaco.start(auto_register=True)

    # Inicializar e iniciar o agente de controle do aeroporto 
    airport_agent = []
    for i in range(5):
        agentAirport = AeroportoAgent("airport_agent@localhost", "password", environment)
        airport_agent.append(agentAirport)
        await agentAirport.start(auto_register=True)

    # Inicializar e iniciar os agentes de aeronaves
    aircraft_agents = []
    for i in range(5):
        pos = random.choice(list(environment.airport_positions.items()))
        agentAircraft = Avião(f"airplane{i}@localhost", "password", environment, pos[1], pos[0])
        aircraft_agents.append(agentAircraft)
        await agentAircraft.start(auto_register=True)

    while True:
        await asyncio.sleep(1)  # Intervalo de atualização
    

if __name__ == "__main__":
    spade.run(main())