import pygame
import random

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

bg = pygame.image.load('bg.jpg')


class Player(pygame.sprite.Sprite):
    right = True

    def __init__(self):
        super().__init__()
        self.image = pygame.image.load('idle.png')
        self.rect = self.image.get_rect()
        self.change_x = 0
        self.change_y = 0

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

    def go_left(self):
        self.change_x = -9
        if self.right:
            self.flip()
            self.right = False

    def go_right(self):
        self.change_x = 9
        if not self.right:
            self.flip()
            self.right = True

    def stop(self):
        self.change_x = 0

    def flip(self):
        self.image = pygame.transform.flip(self.image, True, False)

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
        self.image = pygame.image.load('platform.png')
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
        self.image = pygame.image.load('star.png')
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed_x = random.choice([-5, -4, -3, 3, 4, 5])
        self.speed_y = random.choice([-5, -4, -3, 3, 4, 5])
        self.life = 100

    def update(self):
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y
        self.life -= 1
        if self.life <= 0:
            self.kill()


class Flag(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # Рисуем флажок. Используем прямоугольник для простоты.
        self.image = pygame.Surface((20, 30))
        self.image.fill((255, 0, 0))  # Красный цвет
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Level(object):
    def __init__(self, player):
        self.platform_list = pygame.sprite.Group()
        self.player = player
        self.respawn_y = 300
        self.flag = None  # Флажок

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


class Level_01(Level):
    def __init__(self, player):
        Level.__init__(self, player)
        level = [
            [200, 32, 300, 500],
            [200, 32, 75, 425],
            [200, 32, 500, 350],
            [200, 32, 100, 275],
            [150, 32, 550, 200],
            [150, 32, 750, 75],
            [150, 32, 500, -25],
            [150, 32, 100, -75],
            [150, 32, -50, -190]
        ]
        for platform in level:
            block = Platform(platform[0], platform[1], platform[2], platform[3])
            block.player = self.player
            self.platform_list.add(block)

        # Флажок на самой высокой платформе
        self.flag = Flag(350, -250)  # Размещение флажка на y = -250
        self.platform_list.add(self.flag)

        # Устанавливаем стартовую позицию игрока на первой платформе
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

    while not done:
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

        active_sprite_list.update()
        current_level.update()

        if player.rect.right > SCREEN_WIDTH:
            player.rect.right = SCREEN_WIDTH
        if player.rect.left < 0:
            player.rect.left = 0

        current_level.draw(screen, player)

        # Проверка на столкновение с флажком
        if pygame.sprite.collide_rect(player, current_level.flag):
            for _ in range(30):  # Генерация частиц
                particle = Particle(player.rect.centerx, player.rect.centery)
                particles.add(particle)
                active_sprite_list.add(particle)

        active_sprite_list.draw(screen)
        particles.update()
        particles.draw(screen)

        clock.tick(30)
        pygame.display.flip()

    pygame.quit()

main()
