import pygame
import random
import requests
from pygame.locals import *
from io import BytesIO
from geopy.distance import geodesic

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Местоположение на карте")

WHITE = (255, 255, 255)
MARK_COLOR = (255, 0, 0)

font = pygame.font.SysFont("Arial", 24)
small_font = pygame.font.SysFont("Arial", 18)
large_font = pygame.font.SysFont("Arial", 48)

images = [
    "Materials/EyfelTower.jpg", "Materials/NemoMuseum.jpeg",
    "Materials/NationalPragaMuseum.jpeg", "Materials/PolishRevolutionMuseum.jpg",
    "Materials/OxfordStreet.jpeg", "Materials/MuseumOfBearGuiness.jpg",
    "Materials/ParlamentOfVena.jpeg", "Materials/NikolaTeslaMuseum.jpeg",
    "Materials/MaydanNez.jpg", "Materials/SquareOfSpain.jpeg",
    "Materials/25AprilBridge.jpeg", "Materials/Panteon.jpeg",
    "Materials/SquareOfFreedom.jpeg", "Materials/SenatSquare.jpeg",
    "Materials/NationalSwedenMuseum.jpeg", "Materials/MSU.jpeg"
]

image_descriptions = [
    ("Эйфелева башня", "Париж, Франция"),
    ("Музей Немо", "Амстердам, Нидерланды"),
    ("Национальный музей", "Прага, Чехия"),
    ("Музей Варшавского Восстания", "Варшава, Польша"),
    ("Улица Оксфорд-стрит", "Лондон, Великобритания"),
    ("Музей пива Гиннесс", "Дублин, Ирландия"),
    ("Здание парламента", "Вена, Австрия"),
    ("Музей Николы Теслы", "Белград, Сербия"),
    ("Майдан Незалежности", "Киев, Украина"),
    ("Площадь Испании", "Мадрид, Испания"),
    ("Мост 25 апреля", "Лиссабон, Португалия"),
    ("Пантеон", "Рим, Италия"),
    ("Площадь Независимости", "Минск, Белоруссия"),
    ("Сенатская Площадь", "Хельсинки, Финляндия"),
    ("Национальный музей Швеции", "Стокгольм, Швеция"),
    ("Воробьёвы горы и МГУ", "Москва, Россия")
]


def read_api_key():
    from API_KEY import YANDEX_API_KEY
    return YANDEX_API_KEY


YANDEX_API_KEY = read_api_key()


def get_coordinates(place):
    url = f'https://geocode-maps.yandex.ru/1.x/?geocode={place}&format=json&apikey={YANDEX_API_KEY}'
    response = requests.get(url)
    data = response.json()

    if data['response']['GeoObjectCollection']['featureMember']:
        coords = data['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['Point']['pos']
        lon, lat = map(float, coords.split())
        return lat, lon
    else:
        return None, None


def get_map_image():
    lat, lon = 50.0, 10.0
    static_map_url = f"https://static-maps.yandex.ru/1.x/?lang=ru_RU&ll={lon},{lat}&spn=25.0,20.0&size=650,450&l=map"
    response = requests.get(static_map_url)

    image_data = BytesIO(response.content)
    map_image = pygame.image.load(image_data)

    map_image = scale_image_proportionally(map_image, WIDTH, HEIGHT)

    return map_image


def scale_image_proportionally(image, max_width, max_height):
    original_width, original_height = image.get_size()
    scale_width = max_width / original_width
    scale_height = max_height / original_height
    scale = min(scale_width, scale_height)

    new_width = int(original_width * scale)
    new_height = int(original_height * scale)

    scaled_image = pygame.transform.scale(image, (new_width, new_height))

    return scaled_image


def calculate_distance(lat1, lon1, lat2, lon2):
    coords_1 = (lat1, lon1)
    coords_2 = (lat2, lon2)
    return geodesic(coords_1, coords_2).kilometers


def game_loop():
    running = True
    clock = pygame.time.Clock()

    index = random.choice(range(len(images)))
    image_path = images[index]
    description, place = image_descriptions[index]

    image = pygame.image.load(image_path)
    image = scale_image_proportionally(image, 600, 400)

    target_lat, target_lon = get_coordinates(place)

    if target_lat is None or target_lon is None:
        print(f"Ошибка при получении координат для {place}")
        return

    map_image = None
    show_map = False
    mark_position = None
    map_rect = None

    button_image = pygame.image.load('button.png')
    button_image = pygame.transform.scale(button_image, (80, 80))
    button_rect = button_image.get_rect(bottomright=(WIDTH - 10, HEIGHT - 25))

    center_lat, center_lon = 50.0, 10.0
    distance_message = None
    show_image_and_description = False
    start_time = None

    while running:
        screen.fill(WHITE)

        for event in pygame.event.get():
            if event.type == QUIT:
                running = False

            if event.type == MOUSEBUTTONDOWN:
                x, y = event.pos

                if button_rect.collidepoint(x, y):
                    if show_image_and_description:
                        game_loop()
                        return
                    elif show_map and mark_position:
                        user_lat, user_lon = get_user_location_on_map(mark_position, map_rect, center_lat, center_lon)
                        distance = calculate_distance(target_lat, target_lon, user_lat, user_lon)
                        print(f"Расстояние до места: {distance:.2f} км.")

                        if distance < 200:
                            distance_message = "Правильно"
                            show_image_and_description = True
                            start_time = pygame.time.get_ticks()
                        else:
                            distance_message = None
                        break
                    elif not show_map:
                        map_image = get_map_image()
                        map_rect = map_image.get_rect(center=(WIDTH // 2, HEIGHT // 2))
                        show_map = True
                        mark_position = None

                if show_map and map_rect.collidepoint(x, y):
                    mark_position = (x - map_rect.x, y - map_rect.y)

        if show_map:
            screen.blit(map_image, map_rect)

            if mark_position:
                pygame.draw.circle(screen, MARK_COLOR, (mark_position[0], mark_position[1] + 20), 10)

            mark_lat, mark_lon = get_user_location_on_map(mark_position, map_rect, center_lat, center_lon)
            coords_text = small_font.render(f"Lat: {mark_lat:.5f}, Lon: {mark_lon:.5f}", True, (0, 0, 0))
            screen.blit(coords_text, (10, 30))

        else:
            image_width, image_height = image.get_size()
            image_x = (WIDTH - image_width) // 2
            image_y = (HEIGHT - image_height) // 2
            screen.blit(image, (image_x, image_y))

        if distance_message:
            message_text = large_font.render(distance_message, True, (0, 255, 0))
            text_rect = message_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            pygame.draw.rect(screen, (0, 0, 0), text_rect.inflate(20, 20), 3)
            pygame.draw.rect(screen, (255, 255, 255), text_rect.inflate(20, 20))
            screen.blit(message_text, text_rect)

        if show_image_and_description:
            if pygame.time.get_ticks() - start_time > 1500:
                description_text = font.render(f"{description} - {place}", True, (0, 0, 0))
                screen.fill(WHITE)
                screen.blit(description_text, (WIDTH // 2 - description_text.get_width() // 2, 50))
                screen.blit(image, (WIDTH // 2 - image.get_width() // 2, HEIGHT // 2 - 150))

        screen.blit(button_image, button_rect)

        pygame.display.flip()
        clock.tick(60)


def get_user_location_on_map(mark_position, map_rect, center_lat, center_lon):
    map_width, map_height = map_rect.width, map_rect.height

    lat_range = 25.0
    lon_range = 55.0

    offset_x = mark_position[0] - map_width / 2
    offset_y = mark_position[1] - map_height / 2

    scale_x = lon_range / map_width
    scale_y = lat_range / map_height

    user_lat = center_lat - (offset_y * scale_y)
    user_lon = center_lon + (offset_x * scale_x)

    return user_lat, user_lon


def main_menu():
    running = True
    clock = pygame.time.Clock()

    play_image = pygame.image.load("images/play.png")
    help_image = pygame.image.load("images/help.jpg")

    play_image = pygame.transform.scale(play_image, (185, 69))
    help_image = pygame.transform.scale(help_image, (164, 60))

    play_button_rect = play_image.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    help_button_rect = help_image.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 80))

    click_count = 0

    while running:
        screen.fill(WHITE)

        title_text = large_font.render("DuckCapitals", True, (0, 0, 0))
        screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 4))

        screen.blit(play_image, play_button_rect)
        screen.blit(help_image, help_button_rect)

        readme_logo = pygame.image.load("images/ReadMeLogo.jpg")
        readme_logo = scale_image_proportionally(readme_logo, 60, 60)
        logo_rect = readme_logo.get_rect(bottomleft=(10, HEIGHT - 10))
        screen.blit(readme_logo, logo_rect)

        for event in pygame.event.get():
            if event.type == QUIT:
                running = False

            if event.type == MOUSEBUTTONDOWN:
                x, y = event.pos

                if play_button_rect.collidepoint(x, y):
                    game_loop()
                elif help_button_rect.collidepoint(x, y):
                    show_help()

                if logo_rect.collidepoint(x, y):
                    click_count += 1
                    if click_count == 3:
                        show_secret_window()

        pygame.display.flip()
        clock.tick(60)


def show_help():
    running = True
    clock = pygame.time.Clock()

    back_image = pygame.image.load("images/back.png")

    back_image = pygame.transform.scale(back_image, (170 ,75))

    back_button_rect = back_image.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 100))

    random_help_text = random.choice([
        "Используйте карту, чтобы найти местоположение.",
        "Кликните на карту, чтобы пометить ваше местоположение.",
        "Смотрите расстояние до цели, когда отметите местоположение."
    ])

    while running:
        screen.fill(WHITE)

        help_title = large_font.render("Помощь", True, (0, 0, 0))
        screen.blit(help_title, (WIDTH // 2 - help_title.get_width() // 2, HEIGHT // 4))

        help_text = small_font.render(random_help_text, True, (0, 0, 0))
        screen.blit(help_text, (WIDTH // 2 - help_text.get_width() // 2, HEIGHT // 2))

        screen.blit(back_image, back_button_rect)

        for event in pygame.event.get():
            if event.type == QUIT:
                running = False

            if event.type == MOUSEBUTTONDOWN:
                x, y = event.pos

                if back_button_rect.collidepoint(x, y):
                    running = False

        pygame.display.flip()
        clock.tick(60)


def show_secret_window():
    running = True
    clock = pygame.time.Clock()

    secret_text = large_font.render("Пасхалка раскрыта!", True, (0, 255, 0))

    while running:
        screen.fill(WHITE)
        screen.blit(secret_text, (WIDTH // 2 - secret_text.get_width() // 2, HEIGHT // 2))

        pygame.display.flip()
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == QUIT:
                running = False

    main_menu()


if __name__ == "__main__":
    main_menu()
    pygame.quit()
