import pygame
import sys
import json
import math
# Inicialização do Pygame
pygame.init()


COLORS = {
    "WHITE":(255,255,255),
    "RED":(255,0,0),
    "GREEN":(0,255,0),
    "YELLOW":(255,255,0),
    "MAGENTA":(255,0,255),
    "BLACK":(0,0,0)
}

def load_aircraft_positions():
    try:
        with open("aircraft_positions.json", "r") as file:
            return json.load(file)
    except json.decoder.JSONDecodeError:
        return load_aircraft_positions()
    
def load_airport_positions():
    try:
        with open("airport_positions.json", "r") as file:
            return json.load(file)
    except json.decoder.JSONDecodeError:
        return {}

def load_aircraft_routes():
    try:
        with open("aircraft_routes.json", "r") as file:
            return json.load(file)
    except json.decoder.JSONDecodeError:
        return load_aircraft_routes()

# Configuração da janela do Pygame
screen_width, screen_height = 1000, 800
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Air Traffic Control Simulation")
clock = pygame.time.Clock()

# Configuração de cores
background_color = (0, 105, 148)  # Azul
aircraft_color = (0, 0, 0)       # Preto

airport_positions=load_airport_positions()
fundo = pygame.image.load('radar.jpg')
# Carregar imagem do avião
airplane_image = pygame.image.load("aviao.png").convert_alpha()
# Redimensionar a imagem para um tamanho adequado
airplane_image = pygame.transform.scale(airplane_image, (70, 70))  # Ajuste o tamanho conforme necessário


# Loop principal
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    aircraft_positions = load_aircraft_positions()
    aircraft_routes = load_aircraft_routes()

    screen.blit(fundo, (0, 0))
    # Desenhar as aeronaves

    # Desenhar os aeroportos
    for color,pos in airport_positions.items():
        pos_x = int(pos[0] * screen_width / 40)
        pos_y = int(pos[1] * screen_height / 30)
        pygame.draw.rect(screen, color, (*[pos_x-10,pos_y-10], 40,40))


    for aircraft_id, route in aircraft_routes.items():
        # Escalar e transformar todos os pontos da rota para as coordenadas da tela
        scaled_route = [(int(point[0]) * screen_width / 40, int(point[1]) * screen_height / 30) for point in route]

        # Desenhar linhas entre cada par de pontos consecutivos na rota
        for i in range(len(scaled_route) - 1):
            start_pos = scaled_route[i]
            end_pos = scaled_route[i + 1]
            # Ajustar a espessura da linha aqui, por exemplo, 3 pixels
            pygame.draw.line(screen, aircraft_positions[aircraft_id][0], start_pos, end_pos, 7)

    for aircraft_id, position in aircraft_positions.items():
        # Ajustar as posições para o tamanho da tela
        pos_x = int(position[1][0] * screen_width / 40)
        pos_y = int(position[1][1] * screen_height / 30)

        # Calcular a direção para o próximo ponto na rota
        if len(aircraft_routes[aircraft_id]) > 1:
            next_point = aircraft_routes[aircraft_id][1]  # Assumindo que o próximo ponto é o segundo na lista
            next_x = int(next_point[0] * screen_width / 40)
            next_y = int(next_point[1] * screen_height / 30)
            
            # Calcular o ângulo de rotação
            dx = next_point[0] - position[1][0]
            dy = -(next_point[1] - position[1][1])
            angle = math.atan2(dy, dx)

            # Rotacionar a imagem do avião
            rotated_airplane = pygame.transform.rotate(airplane_image, math.degrees(angle)-90)

            # Obter o novo rect para blit após a rotação
            rect = rotated_airplane.get_rect(center=(pos_x, pos_y))
        else:
            rotated_airplane = airplane_image
            rect = airplane_image.get_rect(center=(pos_x, pos_y))

        var = pygame.PixelArray(rotated_airplane)
        var.replace(COLORS["WHITE"],COLORS[position[0]])
        del var

        # Desenhar a imagem do avião rotacionada
        screen.blit(rotated_airplane, rect.topleft)
        
    pygame.display.flip()
    clock.tick(1)  # 30 FPS para uma visualização mais suave