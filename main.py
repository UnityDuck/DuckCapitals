import math
import random
import pygame
import requests
from pygame.locals import *
from io import BytesIO
from geopy.distance import geodesic
import sqlite3
from datetime import datetime

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

global_winstreak = 0


def add_day_to_db():
    conn = sqlite3.connect('time.sqlite')
    cursor = conn.cursor()

    current_day = datetime.now().strftime('%Y-%m-%d')

    cursor.execute("SELECT 1 FROM days WHERE day = ?", (current_day,))
    existing_day = cursor.fetchone()

    if existing_day:
        cursor.execute("UPDATE days SET day = ? WHERE day = ?", (current_day, current_day))
    else:
        cursor.execute("INSERT INTO days (day) VALUES (?)", (current_day,))

    conn.commit()
    conn.close()


def update_winstreak():
    conn = sqlite3.connect('time.sqlite')
    cursor = conn.cursor()

    current_day = datetime.now().strftime('%Y-%m-%d')

    cursor.execute("SELECT winstreak FROM days WHERE day = ?", (current_day,))
    result = cursor.fetchone()

    if result:
        current_winstreak = result[0]
        try:
            cursor.execute("UPDATE days SET winstreak = ? WHERE day = ?", (int(current_winstreak) + 1, current_day))
        except TypeError:
            cursor.execute("UPDATE days SET winstreak = ? WHERE day = ?", (1, current_day))

    conn.commit()
    conn.close()


def get_top_winstreaks():
    conn = sqlite3.connect('time.sqlite')
    cursor = conn.cursor()

    cursor.execute("SELECT day, winstreak FROM days WHERE winstreak > 0 ORDER BY winstreak DESC LIMIT 5")
    top_winstreaks = cursor.fetchall()

    conn.close()

    return sorted(top_winstreaks, key=lambda x: int(x[1]))


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


class Particle:
    def __init__(self, x, y, speed, angle, image):
        self.x = x
        self.y = y
        self.speed = speed
        self.angle = angle
        self.image = image
        self.lifetime = 60

    def update(self):
        self.x += self.speed * math.cos(self.angle)
        self.y += self.speed * math.sin(self.angle)
        self.lifetime -= 1

    def draw(self, surface):
        surface.blit(self.image, (int(self.x), int(self.y)))

    def is_alive(self):
        return self.lifetime > 0


def add_global_winstreak_to_db():
    conn = sqlite3.connect('time.sqlite')
    cursor = conn.cursor()

    current_day = datetime.now().strftime('%Y-%m-%d')

    cursor.execute("SELECT winstreak FROM days WHERE day = ?", (current_day,))
    result = cursor.fetchone()

    print(result)

    if result:
        current_winstreak = result[0]
        cursor.execute("UPDATE days SET winstreak = ? WHERE day = ?",
                       (current_winstreak + global_winstreak, current_day))
    else:
        cursor.execute("INSERT INTO days (day, winstreak) VALUES (?, ?)", (current_day, global_winstreak))

    conn.commit()
    conn.close()


def reset_global_winstreak():
    global global_winstreak
    global_winstreak = 0


def main_menu():
    global global_winstreak

    running = True
    clock = pygame.time.Clock()

    add_day_to_db()

    bg_image = pygame.image.load("images/bg_start.jpg")
    bg_image = pygame.transform.scale(bg_image, (WIDTH, HEIGHT))

    play_image = pygame.image.load("images/play.png")
    help_image = pygame.image.load("images/help.jpg")

    play_image = pygame.transform.scale(play_image, (185, 69))
    help_image = pygame.transform.scale(help_image, (212, 90))

    play_button_rect = play_image.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    help_button_rect = help_image.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 80))

    click_count = 0

    while running:
        screen.fill(WHITE)

        screen.blit(bg_image, (0, 0))

        screen.blit(play_image, play_button_rect)
        screen.blit(help_image, help_button_rect)

        top_winstreaks = get_top_winstreaks()
        top_text = small_font.render("Топ по победам:", True, (0, 0, 0))
        screen.blit(top_text, (WIDTH - 200, 20))

        top_winstreaks = sorted(top_winstreaks, key=lambda x: int(x[1]), reverse=True)

        for i, (day, winstreak) in enumerate(top_winstreaks):
            if i == 0:
                color = (255, 200, 0)
            elif i == 1:
                color = (192, 192, 192)
            elif i == 2:
                color = (205, 127, 50)
            else:
                color = (0, 0, 0)

            top_entry_text = small_font.render(f"{i + 1}. {day} - {winstreak} побед", True, color)
            screen.blit(top_entry_text, (WIDTH - 200, 50 + i * 30))

        readme_logo = pygame.image.load("images/logo_start.png")
        readme_logo = scale_image_proportionally(readme_logo, 200, 200)
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

    background_image = pygame.image.load("images/help_image.png")
    background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))

    back_image = pygame.image.load("images/back.png")
    back_image = pygame.transform.scale(back_image, (170, 75))

    back_button_rect = back_image.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 100))

    random_help_text = random.choice([
        "Угадайте местоположение достопримечательности по фото.",
        "Найдите местоположение достопримечательности на карте по фото.",
        "Угадайте местоположение достопримечательности на карте по фото. (Может здесь есть пасхалка? :/)"
    ])

    while running:
        screen.fill(WHITE)

        # Отображение фона
        screen.blit(background_image, (0, 0))

        # Заголовок помощи
        help_title = large_font.render("HELP. Does it really need you?", True, (0, 0, 0))
        screen.blit(help_title, (WIDTH // 2 - help_title.get_width() // 2, HEIGHT // 4))

        # Текст помощи
        help_text = small_font.render(random_help_text, True, (0, 0, 0))
        screen.blit(help_text, (WIDTH // 2 - help_text.get_width() // 2, HEIGHT // 2 - 30))

        # Кнопка назад
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


def game_loop():
    global global_winstreak

    running = True
    clock = pygame.time.Clock()

    background_image = pygame.image.load('images/bg_maingame.jpg')
    background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))

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

    button_image = pygame.image.load('images/button.png')
    button_image = pygame.transform.scale(button_image, (80, 80))
    button_rect = button_image.get_rect(bottomright=(WIDTH - 10, HEIGHT - 25))

    center_lat, center_lon = 50.0, 10.0
    show_image_and_description = False
    start_time = None

    particles = []
    star_image = pygame.image.load("images/star.png")
    broken_heart_image = pygame.image.load("images/broken_heart_image.png")
    broken_heart_image = pygame.transform.scale(broken_heart_image, (40, 40))

    exit_image = pygame.image.load("images/exit_image.png")
    exit_image = pygame.transform.scale(exit_image, (WIDTH, HEIGHT))
    exit_image.set_alpha(30)
    exit_rect = exit_image.get_rect(topleft=(-WIDTH, 0))
    exit_time = pygame.time.get_ticks()

    while running:
        screen.blit(background_image, (0, 0))

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

                        with open("Materials/history.txt", "a") as file:
                            file.write(f"{datetime.now()} - {distance:.2f}\n")

                        if distance < 200:
                            for _ in range(50):
                                angle = random.uniform(0, 2 * 3.14159)
                                speed = random.uniform(2, 5)
                                particle_x = random.randint(WIDTH // 4, 3 * WIDTH // 4)
                                particle_y = random.randint(HEIGHT // 4, 3 * HEIGHT // 4)
                                particles.append(Particle(particle_x, particle_y, speed, angle, star_image))

                            show_image_and_description = True
                            start_time = pygame.time.get_ticks()

                            global_winstreak += 1
                            update_winstreak()
                        else:
                            for _ in range(50):
                                angle = random.uniform(0, 2 * 3.14159)
                                speed = random.uniform(2, 5)
                                particle_x = random.randint(WIDTH // 4, 3 * WIDTH // 4)
                                particle_y = random.randint(HEIGHT // 4, 3 * HEIGHT // 4)
                                particles.append(Particle(particle_x, particle_y, speed, angle, broken_heart_image))
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

        if show_image_and_description:
            if pygame.time.get_ticks() - start_time > 1500:
                description_text = font.render(f"{description} - {place}", True, (255, 255, 255))
                screen.fill(WHITE)
                screen.blit(background_image, (0, 0))
                screen.blit(description_text, (WIDTH // 2 - description_text.get_width() // 2, 50))
                screen.blit(image, (WIDTH // 2 - image.get_width() // 2, HEIGHT // 2 - 150))

        particles = [p for p in particles if p.is_alive()]
        for particle in particles:
            particle.update()
            particle.draw(screen)

        screen.blit(button_image, button_rect)

        if pygame.time.get_ticks() - exit_time < 3000:
            exit_rect.x += 10
            screen.blit(exit_image, exit_rect)

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


def show_secret_window():
    SCREEN_WIDTH = 800
    SCREEN_HEIGHT = 600

    bg = pygame.image.load('images/bg_duckgame.jpg')
    bg = pygame.transform.scale(bg, (800, 600))

    class Player(pygame.sprite.Sprite):
        def __init__(self):
            super().__init__()
            self.frame = 0
            self.images_right = [pygame.image.load(f'sprites/{i}.png') for i in
                                 range(1, 17)]
            self.images_left = [pygame.image.load(f'sprites/-{i}.png') for i in
                                range(1, 17)]

            self.images_right = [pygame.transform.scale(img, (int(img.get_width() * 1.8), int(img.get_height() * 1.8)))
                                 for img in self.images_right]
            self.images_left = [pygame.transform.scale(img, (int(img.get_width() * 1.8), int(img.get_height() * 1.8)))
                                for img in self.images_left]

            self.image = self.images_right[self.frame]
            self.rect = self.image.get_rect()
            self.change_x = 0
            self.change_y = 0
            self.last_update = pygame.time.get_ticks()
            self.walking = False
            self.facing_right = True

        def update(self):
            self.calc_grav()
            self.rect.x += self.change_x
            block_hit_list = pygame.sprite.spritecollide(self, self.level.platform_list, False)
            for block in block_hit_list:
                if self.change_x > 0:
                    self.rect.right = block.rect.left
                elif self.change_x < 0:
                    self.rect.left = block.rect.right
            self.rect.y += self.change_y
            block_hit_list = pygame.sprite.spritecollide(self, self.level.platform_list, False)
            for block in block_hit_list:
                if self.change_y > 0:
                    self.rect.bottom = block.rect.top
                elif self.change_y < 0:
                    self.rect.top = block.rect.bottom
                self.change_y = 0

            if self.rect.top >= self.level.respawn_y:
                self.respawn()

            if self.walking:
                now = pygame.time.get_ticks()
                if now - self.last_update > 100:
                    self.last_update = now
                    self.frame = (self.frame + 1) % len(self.images_right)
                    if self.facing_right:
                        self.image = self.images_right[self.frame]
                    else:
                        self.image = self.images_left[self.frame]

            elif not self.walking:
                if self.facing_right:
                    self.image = self.images_right[0]
                else:
                    self.image = self.images_left[0]

        def go_left(self):
            if self.facing_right:
                self.facing_right = False
            self.change_x = -9
            self.walking = True

        def go_right(self):
            if not self.facing_right:
                self.facing_right = True
            self.change_x = 9
            self.walking = True

        def stop(self):
            self.change_x = 0
            self.walking = False

        def calc_grav(self):
            if self.change_y == 0:
                self.change_y = 1
            else:
                self.change_y += .95
            if self.rect.y >= SCREEN_HEIGHT - self.rect.height and self.change_y >= 0:
                self.change_y = 0
                self.rect.y = SCREEN_HEIGHT - self.rect.height

        def jump(self):
            self.rect.y += 10
            platform_hit_list = pygame.sprite.spritecollide(self, self.level.platform_list, False)
            self.rect.y -= 10
            if len(platform_hit_list) > 0 or self.rect.bottom >= SCREEN_HEIGHT:
                self.change_y = -16

        def respawn(self):
            lowest_platform = None
            for platform in self.level.platform_list:
                if platform.rect.top <= self.level.respawn_y:
                    if lowest_platform is None or platform.rect.top > lowest_platform.rect.top:
                        lowest_platform = platform

            if lowest_platform:
                self.rect.x = lowest_platform.rect.centerx - self.rect.width // 2
                self.rect.y = lowest_platform.rect.top - self.rect.height

    class Platform(pygame.sprite.Sprite):
        def __init__(self, width, height, x, y):
            super().__init__()
            self.image = pygame.image.load('images/platform.png')
            self.rect = self.image.get_rect()
            self.rect.width = width
            self.rect.height = height
            self.rect.x = x
            self.rect.y = y
            if width == 1000:
                self.image = pygame.transform.scale(self.image, (width, height))

    class Particle(pygame.sprite.Sprite):
        def __init__(self, x, y):
            super().__init__()
            self.image = pygame.image.load('images/star.png')
            self.rect = self.image.get_rect()
            self.rect.x = x
            self.rect.y = y
            self.speed_x = random.choice([-5, -4, -3, 3, 4, 5])
            self.speed_y = random.choice([-5, -4, -3, 3, 4, 5])
            self.life = 100

        def update(self):
            self.rect.x += self.speed_x
            self.rect.y += self.speed_y

            if self.rect.left <= 0 or self.rect.right >= SCREEN_WIDTH:
                self.speed_x = -self.speed_x

            if self.rect.top <= 0 or self.rect.bottom >= SCREEN_HEIGHT:
                self.speed_y = -self.speed_y

            self.life -= 1
            if self.life <= 0:
                self.kill()

    class Flag(pygame.sprite.Sprite):
        def __init__(self, x, y):
            super().__init__()
            self.image = pygame.Surface((20, 30))
            self.image.fill((255, 0, 0))
            self.rect = self.image.get_rect()
            self.rect.x = x
            self.rect.y = y

    class Level(object):
        def __init__(self, player):
            self.platform_list = pygame.sprite.Group()
            self.player = player
            self.respawn_y = 300
            self.flag = None

        def update(self):
            self.platform_list.update()

        def draw(self, screen, player):
            offset_x = player.rect.centerx - SCREEN_WIDTH // 2
            offset_y = player.rect.centery - SCREEN_HEIGHT // 2

            screen.blit(bg, (0, 0))
            for platform in self.platform_list:
                platform.rect.x -= offset_x
                platform.rect.y -= offset_y
                screen.blit(platform.image, platform.rect)

            if self.flag:
                self.flag.rect.x -= offset_x
                self.flag.rect.y -= offset_y
                screen.blit(self.flag.image, self.flag.rect)

            player.rect.x -= offset_x
            player.rect.y -= offset_y
            screen.blit(player.image, player.rect)

    def load_level_from_file(filename):
        level_data = []
        try:
            with open(filename, 'r') as file:
                for line in file:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        level_data.append(list(map(int, line.split())))
        except FileNotFoundError:
            print(f"Error: The file {filename} was not found.")
        return level_data

    class Level_01(Level):
        def __init__(self, player, filename="Materials/level.txt"):
            Level.__init__(self, player)

            level_data = load_level_from_file(filename)

            for platform in level_data:
                width, height, x, y = platform
                block = Platform(width, height, x, y)
                block.player = self.player
                self.platform_list.add(block)

            self.flag = Flag(350, -250)
            self.platform_list.add(self.flag)

            for platform in self.platform_list:
                if platform.rect.x == 300 and platform.rect.y == 500:
                    self.player.rect.x = platform.rect.centerx - self.player.rect.width // 2
                    self.player.rect.y = platform.rect.top - self.player.rect.height
                    break

    def main():
        pygame.init()
        size = [SCREEN_WIDTH, SCREEN_HEIGHT]
        screen = pygame.display.set_mode(size)
        pygame.display.set_caption("Платформер")
        player = Player()
        level_list = []
        level_list.append(Level_01(player))
        current_level_no = 0
        current_level = level_list[current_level_no]
        active_sprite_list = pygame.sprite.Group()
        player.level = current_level
        active_sprite_list.add(player)
        particles = pygame.sprite.Group()
        done = False
        clock = pygame.time.Clock()

        intro_image = pygame.image.load('images/intro_image.jpg')
        intro_rect = intro_image.get_rect()
        intro_rect.height = SCREEN_HEIGHT
        intro_rect.width = 0
        start_time = pygame.time.get_ticks()

        while not done:
            screen.fill((0, 0, 0))

            current_time = pygame.time.get_ticks()
            if current_time - start_time < 3000:
                intro_rect.width = int(SCREEN_WIDTH * (current_time - start_time) / 3000)
                scaled_image = pygame.transform.scale(intro_image, (intro_rect.width, SCREEN_HEIGHT))
                screen.blit(scaled_image, (0, 0))

            else:
                scaled_image = pygame.transform.scale(intro_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
                screen.blit(scaled_image, (0, 0))

            if current_time - start_time > 3000:
                active_sprite_list.update()
                current_level.update()

                if player.rect.right > SCREEN_WIDTH:
                    player.rect.right = SCREEN_WIDTH
                if player.rect.left < 0:
                    player.rect.left = 0

                current_level.draw(screen, player)

                if pygame.sprite.collide_rect(player, current_level.flag):
                    for _ in range(30):
                        particle = Particle(player.rect.centerx, player.rect.centery)
                        particles.add(particle)
                        active_sprite_list.add(particle)

                active_sprite_list.draw(screen)
                particles.update()
                particles.draw(screen)

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    done = True
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_a:
                        player.go_left()
                    if event.key == pygame.K_d:
                        player.go_right()
                    if event.key == pygame.K_w:
                        player.jump()
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_a and player.change_x < 0:
                        player.stop()
                    if event.key == pygame.K_d and player.change_x > 0:
                        player.stop()

            clock.tick(30)

        pygame.quit()

    main()

    pygame.quit()


if __name__ == "__main__":
    try:
        main_menu()
        pygame.quit()
    except pygame.error:
        pass
