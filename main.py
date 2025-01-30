import pygame
import random
import math
import requests
from geopy.distance import geodesic
from io import BytesIO
import reverse_geocoder as rg

print(rg.search((3.440078, 55.791049)))

pygame.init()

WIDTH, HEIGHT = 650, 450
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Игра: Угадай точку на карте")

WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

def get_map_image(zoom=3, width=WIDTH, height=HEIGHT):
    map_url = f"https://static-maps.yandex.ru/1.x/?ll=28.774255,55.484551&size={width},{height}&z={zoom}&l=map"
    response = requests.get(map_url)
    image = pygame.image.load(BytesIO(response.content))
    return image

def generate_random_coordinates():
    lat = random.uniform(35.0, 72.0)
    lon = random.uniform(-25.0, 40.0)
    # Проверяем, является ли координата сушей
    while not is_land(lat, lon):
        lat = random.uniform(35.0, 72.0)
        lon = random.uniform(-25.0, 40.0)
    return lat, lon

def is_land(lat, lon):
    # Проверяем с использованием OpenStreetMap Nominatim API, чтобы узнать, суша ли это
    url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json"
    response = requests.get(url)
    print(response.content)
    data = response.json()
    if 'address' in data:
        # Если в адресе есть страна, это, вероятно, суша
        return True
    return False

target_lat, target_lon = generate_random_coordinates()

font = pygame.font.Font(None, 36)

def draw_text(text, color, x, y):
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, (x, y))

def calculate_distance(lat1, lon1, lat2, lon2):
    coords_1 = (lat1, lon1)
    coords_2 = (lat2, lon2)
    return geodesic(coords_1, coords_2).kilometers

running = True
while running:
    screen.fill(WHITE)

    map_image = get_map_image()

    screen.blit(map_image, (0, 0))

    draw_text("Кликните на карту!", BLUE, 10, 10)

    draw_text(f"Загадано: Широта: {target_lat:.2f}, Долгота: {target_lon:.2f}", GREEN, 10, 50)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos
            clicked_lat = target_lat - (mouse_y / HEIGHT) * (target_lat - 41.0)
            clicked_lon = target_lon - (mouse_x / WIDTH) * (target_lon - 25.0)

            distance = calculate_distance(clicked_lat, clicked_lon, target_lat, target_lon)

            draw_text(f"Расстояние до загаданной точки: {distance:.2f} км", RED, 10, 100)

    pygame.display.update()

pygame.quit()
