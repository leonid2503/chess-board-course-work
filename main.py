import pygame
import chess
import sys
import os

# Constants
WIDTH, HEIGHT = 1000, 800
BOARD_SIZE = 800
SQUARE_SIZE = BOARD_SIZE // 8
PIECE_PATH = "chess_pieces"

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Chess Game")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)

# Chess board initialization
board = chess.Board()

# Load chess piece images
piece_images = {}


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
    """Loads images for each chess piece into a dictionary."""
    for piece in ['king', 'queen', 'rook', 'bishop', 'knight', 'pawn']:
        for color in ['white', 'black']:
            filename = f"{color}_{piece}.png"
            filepath = os.path.join(PIECE_PATH, filename)
            image = pygame.image.load(filepath)
            piece_images[f"{color[0]}{piece[0].upper()}"] = pygame.transform.scale(image, (SQUARE_SIZE, SQUARE_SIZE))


def draw_board_and_pieces():
    """Draws the board and places pieces based on the board state."""
    board_colors = [pygame.Color("white"), pygame.Color("gray")]
    for row in range(8):
        for col in range(8):
            color = board_colors[(row + col) % 2]
            pygame.draw.rect(screen, color, pygame.Rect(col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
            piece = board.piece_at(row * 8 + col)
            if piece:
                symbol = piece.symbol()
                if piece.color == chess.WHITE:
                    piece_key = 'w' + symbol.upper()

                else:
                    piece_key = 'b' + symbol.upper()
                piece_image = piece_images[piece_key]
                screen.blit(piece_image, (col * SQUARE_SIZE, row * SQUARE_SIZE))


# Initialize buttons
save_button = Button(850, 50, 140, 50, "Save Game", lambda: save_game(board))
load_button = Button(850, 120, 140, 50, "Load Game", lambda: load_game(board))


def save_game(board):
    """Saves the current game state to a file."""
    with open("saved_game.fen", "w") as f:
        f.write(board.fen())
    print("Game saved.")


def load_game(board):
    """Loads a game state from a file."""
    with open("saved_game.fen", "r") as f:
        fen = f.read()
        board.set_fen(fen)
    print("Game loaded.")


def game_loop():
    """Main game loop that handles events and updates the display."""
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            save_button.handle_event(event)
            load_button.handle_event(event)

        screen.fill(pygame.Color('white'))
        draw_board_and_pieces()
        save_button.draw(screen)
        load_button.draw(screen)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


def main():
    load_piece_images()
    game_loop()


if __name__ == "__main__":
    main()
