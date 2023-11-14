
import pygame
import sys
import json

# Inicialização do Pygame
pygame.init()

def load_aircraft_positions():
    try:
        with open("aircraft_positions.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}
    
def load_airport_positions():
    try:
        with open("airport_positions.json", "r") as file:
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

airport_positions=load_airport_positions()


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
        pos_x = int(position[0] * screen_width / 40)
        pos_y = int(position[1] * screen_height / 30)
        pygame.draw.circle(screen, aircraft_color, (pos_x, pos_y), 10)

    # Desenhar os aeroportos
    for color,pos in airport_positions.items():
        pos_x = int(pos[0] * screen_width / 40)
        pos_y = int(pos[1] * screen_height / 30)
        pygame.draw.rect(screen, color, (*[pos_x-10,pos_y-10], 20,20))

    pygame.display.flip()
    clock.tick(1)  # 30 FPS para uma visualização mais suave
