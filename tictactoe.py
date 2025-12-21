import pygame
import sys
from pygame import Rect
import argparse
import os


def draw_gradient(surface, color_top, color_bottom):
    """Draw a vertical gradient over the surface."""
    top_r, top_g, top_b = color_top
    bot_r, bot_g, bot_b = color_bottom
    height = surface.get_height()
    for y in range(height):
        t = y / max(1, height - 1)
        r = int(top_r + (bot_r - top_r) * t)
        g = int(top_g + (bot_g - top_g) * t)
        b = int(top_b + (bot_b - top_b) * t)
        pygame.draw.line(surface, (r, g, b), (0, y), (surface.get_width(), y))


class TicTacToe:
    def __init__(self, size=600, player_name=None, age=None, country=None):
        pygame.init()

        # create window first (ensures icon change takes effect on Windows)
        self.size = size
        self.screen = pygame.display.set_mode((size, size))

        # load icon from the project's static folder and set it as the window icon
        try:
            base = os.path.dirname(__file__) or os.getcwd()
            icon_path = os.path.join(base, "static", "images.png")
            if not os.path.isfile(icon_path):
                # fallback to cwd/static/images.png
                icon_path = os.path.join(os.getcwd(), "static", "images.png")
            if os.path.isfile(icon_path):
                icon_surf = pygame.image.load(icon_path).convert_alpha()
                # ensure a small square icon (32x32) which works well on Windows
                icon_surf = pygame.transform.smoothscale(icon_surf, (32, 32))
                pygame.display.set_icon(icon_surf)
        except Exception:
            # ignore icon errors
            pass

        # set caption after icon (keeps title consistent)
        title = "Tic Tac Toe"
        if player_name:
            title = f"{title} - {player_name}"
        pygame.display.set_caption(title)

        # remaining initialization
        self.clock = pygame.time.Clock()
        self.grid_rect = Rect(50, 50, size - 100, size - 100)
        self.cell_size = self.grid_rect.width // 3

        # store user info (optional display)
        self.player_name = player_name
        self.age = age
        self.country = country

        # Colors (styled like a modern app)
        self.bg_top = (18, 24, 38)    # deep navy
        self.bg_bottom = (36, 50, 77)  # blue gradient
        self.line_color = (220, 220, 230)
        self.x_color = (255, 105, 180)  # pink
        self.o_color = (129, 236, 236)  # mint

        pygame.font.init()
        self.title_font = pygame.font.SysFont('Segoe UI', 36, bold=True)
        self.info_font = pygame.font.SysFont('Arial', 18)

        # Game state: 0 empty, 1 X, 2 O
        self.board = [[0] * 3 for _ in range(3)]
        self.turn = 1
        self.winner = 0
        self.running = True

    def reset(self):
        self.board = [[0] * 3 for _ in range(3)]
        self.turn = 1
        self.winner = 0

    def draw_background(self):
        # load and draw Chrysanthemum.jpg as background
        try:
            base = os.path.dirname(__file__) or os.getcwd()
            bg_path = os.path.join(base, "static", "Chrysanthemum.jpg")
            if not os.path.isfile(bg_path):
                # fallback to cwd/static/Chrysanthemum.jpg
                bg_path = os.path.join(os.getcwd(), "static", "Chrysanthemum.jpg")
            if os.path.isfile(bg_path):
                bg_surf = pygame.image.load(bg_path).convert()
                bg_surf = pygame.transform.scale(bg_surf, (self.size, self.size))
                self.screen.blit(bg_surf, (0, 0))
            else:
                # fallback to gradient if image not found
                draw_gradient(self.screen, self.bg_top, self.bg_bottom)
        except Exception:
            # fallback to gradient on load error
            draw_gradient(self.screen, self.bg_top, self.bg_bottom)

    def draw_ui(self):
        # Title (centered)
        title_surf = self.title_font.render('Tic Tac Toe', True, self.line_color)
        title_x = (self.size - title_surf.get_width()) // 2
        self.screen.blit(title_surf, (title_x, 10))

        # show optional player info under title
        if self.player_name or self.country or self.age:
            info_text = ""
            if self.player_name:
                info_text += f"{self.player_name}"
            if self.age:
                info_text += f" • {self.age}"
            if self.country:
                info_text += f" • {self.country}"
            info_surf = self.info_font.render(info_text, True, (200, 200, 210))
            info_x = (self.size - info_surf.get_width()) // 2
            self.screen.blit(info_surf, (info_x, 54))

        # Info line bottom-left
        info = 'Click to place. R to reset. Esc to quit.'
        info_surf = self.info_font.render(info, True, (200, 200, 210))
        self.screen.blit(info_surf, (20, self.size - 30))

        # Winner top-right
        if self.winner:
            txt = 'X wins!' if self.winner == 1 else ('O wins!' if self.winner == 2 else 'Tie!')
            wsurf = self.title_font.render(txt, True, self.line_color)
            self.screen.blit(wsurf, (self.size - 20 - wsurf.get_width(), 10))

    def draw_board(self):
        # board background
        board_surf = pygame.Surface((self.grid_rect.width, self.grid_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(board_surf, (255, 255, 255, 6), board_surf.get_rect(), border_radius=16)
        # grid lines
        for i in range(1, 3):
            # vertical
            x = i * self.cell_size
            pygame.draw.line(board_surf, self.line_color, (x, 0), (x, self.grid_rect.height), 4)
            # horizontal
            y = i * self.cell_size
            pygame.draw.line(board_surf, self.line_color, (0, y), (self.grid_rect.width, y), 4)

        # draw marks
        for r in range(3):
            for c in range(3):
                val = self.board[r][c]
                cx = c * self.cell_size + self.cell_size // 2
                cy = r * self.cell_size + self.cell_size // 2
                if val == 1:
                    # draw X
                    offset = self.cell_size // 3
                    pygame.draw.line(board_surf, self.x_color, (cx - offset, cy - offset), (cx + offset, cy + offset), 8)
                    pygame.draw.line(board_surf, self.x_color, (cx - offset, cy + offset), (cx + offset, cy - offset), 8)
                elif val == 2:
                    pygame.draw.circle(board_surf, self.o_color, (cx, cy), self.cell_size // 3, 8)

        # highlight winning line if any
        win_line = self.get_win_line()
        if win_line:
            (r1, c1), (r2, c2) = win_line
            start = (c1 * self.cell_size + self.cell_size // 2, r1 * self.cell_size + self.cell_size // 2)
            end = (c2 * self.cell_size + self.cell_size // 2, r2 * self.cell_size + self.cell_size // 2)
            pygame.draw.line(board_surf, (255, 215, 0), start, end, 10)

        self.screen.blit(board_surf, (self.grid_rect.x, self.grid_rect.y))

    def get_win_line(self):
        b = self.board
        # rows
        for r in range(3):
            if b[r][0] and b[r][0] == b[r][1] == b[r][2]:
                return (r, 0), (r, 2)
        # cols
        for c in range(3):
            if b[0][c] and b[0][c] == b[1][c] == b[2][c]:
                return (0, c), (2, c)
        # diagonals
        if b[0][0] and b[0][0] == b[1][1] == b[2][2]:
            return (0, 0), (2, 2)
        if b[0][2] and b[0][2] == b[1][1] == b[2][0]:
            return (0, 2), (2, 0)
        return None

    def check_winner(self):
        line = self.get_win_line()
        if line:
            (r1, c1), _ = line
            self.winner = self.board[r1][c1]
            return
        # tie
        if all(self.board[r][c] for r in range(3) for c in range(3)):
            self.winner = 3

    def handle_click(self, pos):
        if self.winner:
            return
        x, y = pos
        if not self.grid_rect.collidepoint(x, y):
            return
        # convert to board coords
        bx = x - self.grid_rect.x
        by = y - self.grid_rect.y
        c = bx // self.cell_size
        r = by // self.cell_size
        if 0 <= r < 3 and 0 <= c < 3 and self.board[r][c] == 0:
            self.board[r][c] = self.turn
            self.turn = 2 if self.turn == 1 else 1
            self.check_winner()

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                    elif event.key == pygame.K_r:
                        self.reset()
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.handle_click(event.pos)

            self.draw_background()
            self.draw_board()
            self.draw_ui()

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()


if __name__ == '__main__':
    # Use argparse for robust parsing; also accept old positional args as fallback.
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--name', '-n', default=None)
    parser.add_argument('--age', '-a', default=None)
    parser.add_argument('--country', '-c', default=None)
    # parse_known_args allows us to still accept plain positional invocation
    parsed, _ = parser.parse_known_args()

    # fallback to positional if flags weren't used
    if not (parsed.name or parsed.age or parsed.country):
        pos = sys.argv[1:] + ["", "", ""]
        player_name = pos[0] or None
        age = pos[1] or None
        country = pos[2] or None
    else:
        player_name = parsed.name
        age = parsed.age
        country = parsed.country

    game = TicTacToe(700, player_name=player_name, age=age, country=country)
    game.run()
