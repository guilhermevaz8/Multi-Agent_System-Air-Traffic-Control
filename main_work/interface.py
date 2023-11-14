import pygame
import sys
import json
from random import randint
from math import dist

DISTANCE_BET_AIRP = 15

# Inicialização do Pygame
pygame.init()

def load_aircraft_positions():
    try:
        with open("aircraft_positions.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

# Configuração da janela do Pygame
screen_width, screen_height = 800, 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Air Traffic Control Simulation")
clock = pygame.time.Clock()

# Configuração de cores
background_color = (0, 105, 148)  # Azul
aircraft_color = (0, 0, 0)       # Preto
airport_colors = ["RED","GREEN","YELLOW","MAGENTA","WHITE"]  # Branco

airport_positions = {}

# Posições dos aeroportos
for i in range(5):
    pos = (randint(2,38),randint(2,28))
    if airport_positions == {}:
         airport_positions[airport_colors[i]]=pos
         continue
    mindist=False
    while not mindist:
        flag=True
        for key,tmp in airport_positions.items():
            x=tmp[0]
            y=tmp[1]
            while dist(pos,(x,y))<=DISTANCE_BET_AIRP:
                flag=False
                pos = (randint(2,38),randint(2,28))
        if flag:
            mindist=True
        else:
            mindist=False
    airport_positions[airport_colors[i]]=pos



# Loop principal
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    aircraft_positions = load_aircraft_positions()
    screen.fill(background_color)

    # Desenhar as aeronaves
    for aircraft_id, position in aircraft_positions.items():
        # Ajustar as posições para o tamanho da tela
        pos_x = int(position[0] * screen_width / 1000)
        pos_y = int(position[1] * screen_height / 1000)
        pygame.draw.circle(screen, aircraft_color, (pos_x, pos_y), 10)

    # Desenhar os aeroportos
    for color,pos in airport_positions.items():
        pos_x = int(pos[0] * screen_width / 40)
        pos_y = int(pos[1] * screen_height / 30)
        pygame.draw.rect(screen, color, (*[pos_x,pos_y], 20,20))

    pygame.display.flip()
    clock.tick(1)  # 30 FPS para uma visualização mais suave
