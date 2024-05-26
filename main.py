import pygame
import chess
import sys
import os
import time

# Constants
WIDTH, HEIGHT = 1200, 800
BOARD_SIZE = 800
SQUARE_SIZE = BOARD_SIZE // 8
PIECE_PATH = "chess_pieces"
MOVE_LOG_PANEL_WIDTH = WIDTH - BOARD_SIZE
MOVE_LOG_PANEL_HEIGHT = HEIGHT

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Chess Game")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)

board = chess.Board()
selected_square = None
highlighted_moves = []
move_log = []
white_time = 900
black_time = 900
last_update_time = time.time()

piece_images = {}


class InputBox:
    def __init__(self, x, y, w, h, text=''):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = pygame.Color('lightskyblue3')
        self.text = text
        self.txt_surface = font.render(text, True, self.color)
        self.active = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = not self.active
                self.color = pygame.Color('dodgerblue') if self.active else pygame.Color('lightskyblue3')  # noqa: E501
            else:
                self.active = False
                self.color = pygame.Color('lightskyblue3')
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    try:
                        return int(self.text) * 60
                    except ValueError:
                        self.text = ''
                        self.txt_surface = font.render(self.text, True, self.color)  # noqa: E501
                        return None
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode
                self.txt_surface = font.render(self.text, True, self.color)

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect, 2)
        screen.blit(self.txt_surface, (self.rect.x+5, self.rect.y+5))


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


def load_piece_images():
    for piece, code in [('king', 'K'), ('queen', 'Q'), ('rook', 'R'), ('bishop', 'B'), ('knight', 'N'), ('pawn', 'P')]:  # noqa: E501
        for color in ['white', 'black']:
            filename = f"{color}_{piece}.png"
            filepath = os.path.join(PIECE_PATH, filename)
            image = pygame.image.load(filepath)
            piece_key = f"{color[0].lower()}{code}"
            piece_images[piece_key] = pygame.transform.scale(image, (SQUARE_SIZE, SQUARE_SIZE))  # noqa: E501


load_piece_images()


def draw_board_and_pieces():
    """Draws the board and places pieces based on the board state."""
    board_colors = [pygame.Color("white"), pygame.Color("gray")]
    for row in range(8):
        for col in range(8):
            square = row * 8 + col
            color = board_colors[(row + col) % 2]
            pygame.draw.rect(screen, color, pygame.Rect(col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))  # noqa: E501
            piece = board.piece_at(square)
            if piece:
                color_prefix = 'w' if piece.color == chess.WHITE else 'b'
                piece_key = f"{color_prefix}{piece.symbol().upper()}"
                if piece_key in piece_images:
                    piece_image = piece_images[piece_key]
                    screen.blit(piece_image, (col * SQUARE_SIZE, row * SQUARE_SIZE))  # noqa: E501
                else:
                    print(f"Warning: No image for {piece_key}")


def handle_mouse_click(pos):
    global selected_square, highlighted_moves, board, move_log
    col = pos[0] // SQUARE_SIZE
    row = pos[1] // SQUARE_SIZE
    if col >= 8 or row >= 8:
        return

    clicked_square = row * 8 + col

    if selected_square is None:
        piece = board.piece_at(clicked_square)
        if piece and piece.color == board.turn:
            selected_square = clicked_square
            highlighted_moves = [move for move in board.legal_moves if move.from_square == clicked_square]  # noqa: E501
            print(f"Selected {chess.SQUARE_NAMES[clicked_square]} for {piece.symbol()} moves.")  # noqa: E501
        else:
            print(f"Click at {chess.SQUARE_NAMES[clicked_square]}: No piece to select or not the player's turn.")  # noqa: E501
    else:
        if selected_square == clicked_square:
            selected_square = None
            highlighted_moves = []
            print(f"Deselected {chess.SQUARE_NAMES[clicked_square]}")
        else:
            move = chess.Move.from_uci(f"{chess.SQUARE_NAMES[selected_square]}{chess.SQUARE_NAMES[clicked_square]}")  # noqa: E501
            if move in board.legal_moves:
                board.push(move)
                try:
                    move_uci = move.uci()
                    move_log.append(move_uci)
                    print(f"Move made: {move_uci}, Board FEN: {board.fen()}")
                except AssertionError as e:
                    print(f"Error: {str(e)} - This error should not occur since the move was validated as legal.")  # noqa: E501
                selected_square = None
                highlighted_moves = []
            else:
                print(f"Illegal move attempted: {move.uci()} from {chess.SQUARE_NAMES[selected_square]} to {chess.SQUARE_NAMES[clicked_square]}")  # noqa: E501
                for legal_move in board.legal_moves:
                    if legal_move.from_square == selected_square:
                        print(f" - {legal_move.uci()} to {chess.SQUARE_NAMES[legal_move.to_square]}")  # noqa: E501
                selected_square = None
                highlighted_moves = []


def draw_move_log():
    move_log_x = 850
    move_log_y = 100
    max_moves_displayed = 10
    start_index = max(0, len(move_log) - max_moves_displayed)
    log_y_offset = 0
    for move in move_log[start_index:]:
        move_surf = font.render(move, True, pygame.Color('black'))
        screen.blit(move_surf, (move_log_x, move_log_y + log_y_offset))
        log_y_offset += 30


def draw_highlights():
    if selected_square is not None:
        s = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE))
        s.set_alpha(128)
        s.fill(pygame.Color('blue'))
        row, col = divmod(selected_square, 8)
        screen.blit(s, (col * SQUARE_SIZE, row * SQUARE_SIZE))

        for move in highlighted_moves:
            end_square = move.to_square
            s = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE))
            s.set_alpha(128)
            s.fill(pygame.Color('green'))
            end_row, end_col = divmod(end_square, 8)
            screen.blit(s, (end_col * SQUARE_SIZE, end_row * SQUARE_SIZE))


def update_timers():
    global last_update_time, white_time, black_time
    current_time = time.time()
    elapsed = current_time - last_update_time
    last_update_time = current_time

    if board.turn == chess.WHITE:
        white_time -= elapsed
    else:
        black_time -= elapsed

    white_time = max(0, white_time)
    black_time = max(0, black_time)


def draw_timers():
    white_minutes, white_seconds = divmod(int(white_time), 60)
    black_minutes, black_seconds = divmod(int(black_time), 60)

    white_time_text = f"White: {white_minutes}:{white_seconds:02d}"
    black_time_text = f"Black: {black_minutes}:{black_seconds:02d}"

    timer_x = 850
    timer_y = 0

    pygame.draw.rect(screen, pygame.Color('darkgrey'), (timer_x, timer_y, 200, 80))  # noqa: E501
    white_time_surface = font.render(white_time_text, True, pygame.Color('black'))  # noqa: E501
    black_time_surface = font.render(black_time_text, True, pygame.Color('black'))  # noqa: E501

    screen.blit(white_time_surface, (timer_x + 10, timer_y + 10))
    screen.blit(black_time_surface, (timer_x + 10, timer_y + 40))


def save_game():
    with open("saved_game.fen", "w") as f:
        f.write(board.fen())
    print("Game saved.")


def load_game():
    with open("saved_game.fen", "r") as f:
        fen = f.read()
        board.set_fen(fen)
    print("Game loaded.")


save_button = Button(850, 700, 140, 50, "Save Game", save_game)
load_button = Button(850, 760, 140, 50, "Load Game", load_game)


def select_time_control():
    controls = [
        "Bullet (1 min)",
        "Blitz (3 min + 2 sec)",
        "Rapid (10 min)",
        "Custom"
    ]
    time_settings = {
        "Bullet (1 min)": (60, 60),
        "Blitz (3 min + 2 sec)": (180, 180),
        "Rapid (10 min)": (600, 600)
    }

    input_box = InputBox(WIDTH // 2 - 100, HEIGHT // 2 - 20, 200, 50)

    def draw_menu():
        screen.fill(pygame.Color('black'))
        for i, control in enumerate(controls):
            text_surf = font.render(control, True, pygame.Color('white'))
            screen.blit(text_surf, (WIDTH // 2 - 100, 30 + i * 40))
        if input_box.active:
            input_box.draw(screen)
        pygame.display.flip()

    running = True
    while running:
        draw_menu()
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                index = (y - 30) // 40
                if 0 <= index < len(controls):
                    selected_control = controls[index]
                    if selected_control == "Custom":
                        input_box.active = True
                        continue
                    else:
                        return time_settings[selected_control]
            elif event.type == pygame.KEYDOWN:
                if input_box.active:
                    result = input_box.handle_event(event)
                    if result is not None:
                        return (result, 0)
            elif event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()


def show_message_box(screen, message):
    font = pygame.font.Font(None, 36)
    box_width, box_height = 400, 200
    box_x, box_y = (WIDTH - box_width) // 2, (HEIGHT - box_height) // 2

    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))

    pygame.draw.rect(screen, (255, 255, 255), [box_x, box_y, box_width, box_height])  # noqa: E501
    pygame.draw.rect(screen, (0, 0, 0), [box_x, box_y, box_width, box_height], 3)  # noqa: E501

    lines = message.splitlines()
    line_height = font.get_height()
    for i, line in enumerate(lines):
        text_surface = font.render(line, True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=(WIDTH // 2, box_y + 50 + i * line_height))  # noqa: E501
        screen.blit(text_surface, text_rect)

    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                waiting = False


def game_over(message):
    show_message_box(screen, message)
    pygame.quit()
    sys.exit()


def check_game_end():
    if board.is_checkmate():
        winning_color = "White" if board.turn == chess.BLACK else "Black"
        game_over(f"Checkmate. {winning_color} wins!")
    elif board.is_stalemate() or board.is_insufficient_material():
        game_over("Stalemate or insufficient material. The game is a draw.")
    elif white_time <= 0:
        game_over("Time out. Black wins!")
    elif black_time <= 0:
        game_over("Time out. White wins!")


def game_loop():
    global white_time, black_time, last_update_time
    time_control = select_time_control()
    white_time, black_time = time_control
    last_update_time = time.time()

    running = True
    while running:
        update_timers()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                handle_mouse_click(event.pos)
            save_button.handle_event(event)
            load_button.handle_event(event)

        screen.fill(pygame.Color('white'))

        check_game_end()

        draw_board_and_pieces()
        draw_highlights()
        draw_timers()
        draw_move_log()

        save_button.draw(screen)
        load_button.draw(screen)

        pygame.display.flip()

        clock.tick(60)


def main():
    game_loop()


if __name__ == "__main__":
    pygame.init()
    main()
