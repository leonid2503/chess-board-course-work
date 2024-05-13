import pygame
import chess
import chess.svg
import chess.engine
from io import BytesIO
import sys

# Constants
WIDTH, HEIGHT = 800, 950
BOARD_SIZE = 800
INFO_HEIGHT = HEIGHT - BOARD_SIZE
FPS = 30
SQUARE_SIZE = BOARD_SIZE // 8
STOCKFISH_PATH = 'C:/Users/LeoBulakh/Downloads/stockfish-windows-x86-64-vnni512'  # noqa: E501

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Chess")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)
engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)

board = chess.Board()
move_log = []
last_time = pygame.time.get_ticks()
game_time = 300
increment = 0
white_time_left = game_time
black_time_left = game_time


def load_image(board):
    svg = chess.svg.board(board=board, size=BOARD_SIZE, lastmove=board.peek() if board.move_stack else None).encode('utf-8')  # noqa: E501
    image = pygame.image.load(BytesIO(svg))
    image = pygame.transform.scale(image, (BOARD_SIZE, BOARD_SIZE))
    return image


def draw_board(screen):
    board_image = load_image(board)
    screen.blit(board_image, (0, 0))


def update_timers():
    global white_time_left, black_time_left, last_time, evaluation
    current_time = pygame.time.get_ticks()
    delta_time = (current_time - last_time) / 1000.0
    if board.turn == chess.WHITE:
        white_time_left = max(0, white_time_left - delta_time)
    else:
        black_time_left = max(0, black_time_left - delta_time)
    last_time = current_time
    result = engine.analyse(board, chess.engine.Limit(time=0.1))
    evaluation = result["score"].relative.score(mate_score=10000)


def draw_timers():
    timer_surf = pygame.Surface((WIDTH, INFO_HEIGHT // 4))
    timer_surf.fill(pygame.Color('gray'))
    white_timer = font.render(f"White Time: {int(white_time_left)}s", True, pygame.Color('black'))  # noqa: E501
    black_timer = font.render(f"Black Time: {int(black_time_left)}s", True, pygame.Color('black'))  # noqa: E501
    evaluation_text = font.render(f"Evaluation: {evaluation}", True, pygame.Color('black'))  # noqa: E501
    timer_surf.blit(white_timer, (10, 10))
    timer_surf.blit(black_timer, (10, 40))
    timer_surf.blit(evaluation_text, (10, 70))
    screen.blit(timer_surf, (0, BOARD_SIZE))


def game_loop():
    global white_time_left, black_time_left, last_time, board, move_log
    selected_piece = None
    running = True
    last_time = pygame.time.get_ticks()
    while running and white_time_left > 0 and black_time_left > 0:
        update_timers()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                engine.quit()
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                column = pos[0] // SQUARE_SIZE
                row = pos[1] // SQUARE_SIZE
                square = row * 8 + column
                if selected_piece is None and board.piece_at(square):
                    selected_piece = square
                elif selected_piece is not None:
                    move = chess.Move(selected_piece, square)
                    if move in board.legal_moves:
                        board.push(move)
                        move_log.append(board.san(move))
                        selected_piece = None
                        if board.turn == chess.WHITE:
                            black_time_left += increment
                        else:
                            white_time_left += increment
                    else:
                        selected_piece = None
        screen.fill(pygame.Color('white'))
        draw_board(screen)
        draw_timers()
        pygame.display.flip()
        clock.tick(FPS)


def main_menu():
    time_controls = {
        "Bullet (1+0)": (60, 0),
        "Blitz (3+0)": (180, 0),
        "Blitz (5+3)": (300, 3),
        "Rapid (10+10)": (600, 10),
        "Custom": "custom"
    }
    running = True
    while running:
        screen.fill(pygame.Color("white"))
        menu_text = font.render("Choose Time Control:", True, pygame.Color("black"))  # noqa: E501
        screen.blit(menu_text, (20, 20))
        y_offset = 60
        for idx, (label, _) in enumerate(time_controls.items()):
            text = font.render(label, True, pygame.Color("blue"))
            screen.blit(text, (40, 20 + y_offset * (idx + 1)))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                idx = (y - 20) // 60 - 1
                if 0 <= idx < len(time_controls):
                    label = list(time_controls.keys())[idx]
                    if label == "Custom":
                        return custom_time_control()
                    return time_controls[label]
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
    return None


def custom_time_control():
    screen.fill(pygame.Color("white"))
    instruction_text = font.render("Enter custom time in format 'minutes:seconds increment'", True, pygame.Color("blue"))  # noqa: E501
    screen.blit(instruction_text, (20, 20))
    pygame.display.flip()

    base_time = ""
    increment = ""
    active_part = 'base_time'
    done = False

    while not done:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if active_part == 'base_time':
                        active_part = 'increment'
                    else:
                        done = True
                elif event.key == pygame.K_BACKSPACE:
                    if active_part == 'base_time':
                        base_time = base_time[:-1]
                    else:
                        increment = increment[:-1]
                else:
                    if active_part == 'base_time':
                        base_time += event.unicode
                    else:
                        increment += event.unicode

            elif event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        screen.fill(pygame.Color("white"))
        text = font.render("Time: " + base_time + " Increment: " + increment, True, pygame.Color("blue"))  # noqa: E501
        screen.blit(text, (20, 50))
        pygame.display.flip()

    try:
        base_time = int(base_time) * 60
        increment = int(increment)
    except ValueError:
        return (300, 0)

    return (base_time, increment)


def main():
    time_control = main_menu()
    if time_control:
        global game_time, increment, white_time_left, black_time_left
        game_time, increment = time_control
        white_time_left = black_time_left = game_time
        game_loop()


if __name__ == "__main__":
    main()
