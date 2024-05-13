import pygame
import chess
import chess.svg
from io import BytesIO
import sys

# Constants
WIDTH, HEIGHT = 800, 950
BOARD_SIZE = 800
INFO_HEIGHT = HEIGHT - BOARD_SIZE
FPS = 30
SQUARE_SIZE = BOARD_SIZE // 8

# Pygame Initialization
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Chess")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)

# Chess board and game state
board = chess.Board()
move_log = []
last_time = pygame.time.get_ticks()
game_time = 300  # Total time in seconds
increment = 0
white_time_left = game_time
black_time_left = game_time

# Button class


class Button:
    def __init__(self, x, y, width, height, text, callback):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.callback = callback
        self.color = pygame.Color('dodgerblue')
        self.text_color = pygame.Color('white')
        self.font = pygame.font.Font(None, 36)

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.callback()


def load_image(board):
    svg = chess.svg.board(board=board, size=BOARD_SIZE, lastmove=board.peek() if board.move_stack else None)  # noqa: E501
    image = pygame.image.load(BytesIO(svg.encode('utf-8')))
    image = pygame.transform.scale(image, (BOARD_SIZE, BOARD_SIZE))
    return image


def draw_board(screen):
    board_image = load_image(board)
    screen.blit(board_image, (0, 0))


def update_timers():
    global white_time_left, black_time_left, last_time
    current_time = pygame.time.get_ticks()
    delta_time = (current_time - last_time) / 1000.0
    if board.turn == chess.WHITE:
        white_time_left = max(0, white_time_left - delta_time)
    else:
        black_time_left = max(0, black_time_left - delta_time)
    last_time = current_time


def draw_timers():
    timer_surf = pygame.Surface((WIDTH, INFO_HEIGHT // 4))
    timer_surf.fill(pygame.Color('gray'))
    white_timer = font.render(f"White Time: {int(white_time_left)}s", True, pygame.Color('black'))  # noqa: E501
    black_timer = font.render(f"Black Time: {int(black_time_left)}s", True, pygame.Color('black'))  # noqa: E501
    timer_surf.blit(white_timer, (10, 10))
    timer_surf.blit(black_timer, (10, 40))
    screen.blit(timer_surf, (0, BOARD_SIZE))


def save_game():
    with open("saved_game.fen", "w") as f:
        f.write(board.fen())
    print("Game saved.")


def load_game():
    with open("saved_game.fen", "r") as f:
        fen = f.read()
        board.set_fen(fen)
    print("Game loaded.")


save_button = Button(650, 800, 140, 50, "Save Game", save_game)
load_button = Button(650, 860, 140, 50, "Load Game", load_game)


def game_loop():
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()
            save_button.handle_event(event)
            load_button.handle_event(event)

        update_timers()
        screen.fill(pygame.Color('white'))
        draw_board(screen)
        save_button.draw(screen)
        load_button.draw(screen)
        draw_timers()
        pygame.display.flip()
        clock.tick(FPS)


def main():
    game_loop()


if __name__ == "__main__":
    main()
