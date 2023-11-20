from imports import *

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
