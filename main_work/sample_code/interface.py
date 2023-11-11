import pygame
import sys
import json

def load_aircraft_positions():
    try:
        with open("aircraft_positions.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

#abrir a janeula do pygame
screen_width, screen_height = 800, 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Air Traffic Control Simulation")
clock = pygame.time.Clock()

#colores hermanos
background_color = (0, 105, 148)  # Cor de fundo: Azul
aircraft_color = (0, 0, 0)       # Cor dos aviões: Preto
airport_color = (255, 255, 255)  # Cor dos aeroportos: Branco

# Posições dos aeroportos
airport_positions = [(100, 100), (300, 500), (600, 300)]

# ir verificando e atualizando 
while True:
    # Tratamento de eventos (fechar janela, etc.)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    
    aircraft_positions = load_aircraft_positions()

    
    screen.fill(background_color)

    # Desenhar os avioneitos lindos
    for aircraft_id, position in aircraft_positions.items():
        pos_x, pos_y = int(position[0]), int(position[1])
        pygame.draw.circle(screen, aircraft_color, (pos_x, pos_y), 5)

    # Desenhar os aeroportos
    for pos in airport_positions:
        pygame.draw.rect(screen, airport_color, (*pos, 30, 30))

    # Atualizar
    pygame.display.flip()

    # fipisi (fpesses)
    clock.tick(1)
