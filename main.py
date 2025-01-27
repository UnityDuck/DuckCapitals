import pygame
import sys

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Duck Capitals")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

duck_image = pygame.image.load('duck.png')
duck_image = pygame.transform.scale(duck_image, (50, 50))

font = pygame.font.Font(None, 36)
input_font = pygame.font.Font(None, 30)

duck_x = 100
duck_y = 100
duck_speed = 5
input_text = ''
correct_answer = 'paris'
question_text = "What is the capital of France?"

MIN_Y = 100
MAX_Y = 200

keyboard = [
    ['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P'],
    ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L'],
    ['Z', 'X', 'C', 'V', 'B', 'N', 'M']
]

key_width = 50
key_height = 50
key_margin = 10

def draw_keyboard():
    y_offset = SCREEN_HEIGHT - 3 * (key_height + key_margin) - 20
    for row_idx, row in enumerate(keyboard):
        x_offset = 50
        for key_idx, key in enumerate(row):
            pygame.draw.rect(screen, GREEN, (x_offset, y_offset, key_width, key_height))
            text = font.render(key, True, BLACK)
            screen.blit(text, (x_offset + 15, y_offset + 10))
            x_offset += key_width + key_margin
        y_offset += key_height + key_margin

def draw_duck():
    screen.blit(duck_image, (duck_x, duck_y))

def draw_input_text():
    text = input_font.render(input_text, True, BLACK)
    screen.blit(text, (50, SCREEN_HEIGHT - 100))

def check_key_pressed():
    y_offset = SCREEN_HEIGHT - 3 * (key_height + key_margin) - 20
    for row_idx, row in enumerate(keyboard):
        x_offset = 50
        for key_idx, key in enumerate(row):
            if duck_x + 50 > x_offset and duck_x < x_offset + key_width and duck_y + 50 > y_offset and duck_y < y_offset + key_height:
                return key
            x_offset += key_width + key_margin
        y_offset += key_height + key_margin
    return None

running = True
while running:
    screen.fill(WHITE)

    question = font.render(question_text, True, BLACK)
    screen.blit(question, (50, 50))

    draw_keyboard()

    draw_duck()

    draw_input_text()

    keys = pygame.key.get_pressed()

    if keys[pygame.K_w] and duck_y > MIN_Y:
        duck_y -= duck_speed
    if keys[pygame.K_s] and duck_y < MAX_Y:
        duck_y += duck_speed
    if keys[pygame.K_a] and duck_x > 0:
        duck_x -= duck_speed
    if keys[pygame.K_d] and duck_x < SCREEN_WIDTH - 50:
        duck_x += duck_speed

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                key_pressed = check_key_pressed()
                if key_pressed:
                    input_text += key_pressed.lower()

                if input_text.lower() == correct_answer:
                    print("Correct!")
                    input_text = ''
                else:
                    print("Incorrect, try again!")
                    input_text = ''

    pygame.display.update()

pygame.quit()
sys.exit()
