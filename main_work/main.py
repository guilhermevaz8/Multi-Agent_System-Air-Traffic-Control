from environment import *
from aeroporto import *
from gestor import *
from airplane import *



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