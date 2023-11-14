
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
pygame.display.set_caption("Air Traffic Control Simulatiqon")
clock = pygame.time.Clock()

# Configuração de cores
background_color = (0, 105, 148)  # Azul
aircraft_color = (0, 0, 0)       # Preto
airport_color = (255, 255, 255)  # Branco

airport_positions = load_airport_positions()

# Loop principal
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    aircraft_positions = load_aircraft_positions()
    print(aircraft_positions)

    screen.fill(background_color)

    # Desenhar as aeronaves
    for aircraft_id, position_aircraft in aircraft_positions.items():
        # Ajustar as posições para o tamanho da tela
        pos_x_aircraft = int(position_aircraft[0] * screen_width / 1000)
        pos_y_aircraft = int(position_aircraft[1] * screen_height / 1000)
        pygame.draw.circle(screen, aircraft_color, (pos_x_aircraft, pos_y_aircraft), 5)

    # Desenhar os aeroportos
    for position_airport in airport_positions:
        # Ajustar as posições para o tamanho da tela
        pos_x_airport = int(position_airport[0] * screen_width / 1000)
        pos_y_airport = int(position_airport[1] * screen_height / 1000)
        pygame.draw.circle(screen, airport_color, (pos_x_airport, pos_y_airport), 5)

    pygame.display.flip()
    clock.tick(1)  # 30 FPS para uma visualização mais suave
