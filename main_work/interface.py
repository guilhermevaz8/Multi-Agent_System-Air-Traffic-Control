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

# Configuração da janela do Pygame
screen_width, screen_height = 800, 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Air Traffic Control Simulation")
clock = pygame.time.Clock()

# Configuração de cores
background_color = (0, 105, 148)  # Azul
aircraft_color = (0, 0, 0)       # Preto
airport_color = (255, 255, 255)  # Branco

# Posições dos aeroportos
airport_positions = [(100, 100), (300, 500), (600, 300)]

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
        pygame.draw.circle(screen, aircraft_color, (pos_x, pos_y), 5)

    # Desenhar os aeroportos
    for pos in airport_positions:
        pygame.draw.rect(screen, airport_color, (*pos, 30, 30))

    pygame.display.flip()
    clock.tick(1)  # 30 FPS para uma visualização mais suave
