"""
2D SNAKE GAMES
A classic snake game with player and AI modes
"""

import pygame
import random
from enum import Enum
from collections import deque
import os

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 640
WINDOW_HEIGHT = 480
# Menu (start/title) window size — keep larger so menu looks good
MENU_WIDTH = 800
MENU_HEIGHT = 600
GRID_SIZE = 20
GRID_WIDTH = WINDOW_WIDTH // GRID_SIZE
GRID_HEIGHT = WINDOW_HEIGHT // GRID_SIZE
FPS = 10

# Reserve some rows at the top for title/score (no grid there)
TOP_ROWS = 3
# Number of playable rows
GRID_HEIGHT = (WINDOW_HEIGHT // GRID_SIZE) - TOP_ROWS
# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)


def load_icon_or_create():
    """Try to load static/snake.png; if missing try to run generator; otherwise return a fallback Surface."""
    base = os.path.dirname(__file__) or os.getcwd()
    icon_path = os.path.join(base, "static", "snake.png")
    if not os.path.isfile(icon_path):
        icon_path = os.path.join(os.getcwd(), "static", "snake.png")

    # Try loading existing file
    try:
        if os.path.isfile(icon_path):
            icon_surf = pygame.image.load(icon_path).convert_alpha()
            return pygame.transform.smoothscale(icon_surf, (32, 32))
    except Exception:
        pass

    # Try to generate the placeholder using the bundled generator script
    try:
        import generate_snake_png
        try:
            generate_snake_png.main()
            if os.path.isfile(icon_path):
                icon_surf = pygame.image.load(icon_path).convert_alpha()
                return pygame.transform.smoothscale(icon_surf, (32, 32))
        except Exception:
            pass
    except Exception:
        pass

    # Fallback: create a simple programmatic icon (green circle)
    surf = pygame.Surface((32, 32), pygame.SRCALPHA)
    surf.fill((0, 0, 0, 0))
    try:
        pygame.draw.circle(surf, GREEN, (16, 16), 14)
    except Exception:
        surf.fill(GREEN)
    return surf

class Direction(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)

class SnakeGame:
    def __init__(self, ai_mode=False):
        self.display = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Snake Game - AI Mode: {}".format("ON" if ai_mode else "OFF"))
        # Try to set a custom window icon (load/generate/fallback)
        try:
            icon_surf = load_icon_or_create()
            pygame.display.set_icon(icon_surf)
        except Exception:
            pass
        self.clock = pygame.time.Clock()
        self.ai_mode = ai_mode
        
        self.reset()
    
    def setup_opengl(self):
        """Setup OpenGL settings"""
        pass
    
    def reset(self):
        """Reset the game state"""
        start_x = GRID_WIDTH // 2
        start_y = GRID_HEIGHT // 2
        
        self.snake = deque([(start_x, start_y), (start_x - 1, start_y), (start_x - 2, start_y)])
        self.food = self.spawn_food()
        self.direction = Direction.RIGHT
        self.next_direction = Direction.RIGHT
        self.score = 0
        self.game_over = False
    
    def spawn_food(self):
        """Spawn food at a random location"""
        while True:
            x = random.randint(0, GRID_WIDTH - 1)
            y = random.randint(0, GRID_HEIGHT - 1)
            if (x, y) not in self.snake:
                return (x, y)
    
    def handle_input(self):
        """Handle keyboard input"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.KEYDOWN:
                # Arrow keys and WASD controls
                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    if self.direction != Direction.DOWN:
                        self.next_direction = Direction.UP
                elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    if self.direction != Direction.UP:
                        self.next_direction = Direction.DOWN
                elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    if self.direction != Direction.RIGHT:
                        self.next_direction = Direction.LEFT
                elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    if self.direction != Direction.LEFT:
                        self.next_direction = Direction.RIGHT
                elif event.key == pygame.K_SPACE:
                    # Reset game
                    self.reset()
        
        return True
    
    def ai_move(self):
        """AI logic to move the snake towards food"""
        head_x, head_y = self.snake[0]
        food_x, food_y = self.food
        
        # Calculate possible moves
        possible_moves = []
        
        # Check all directions
        for direction in Direction:
            new_x = head_x + direction.value[0]
            new_y = head_y + direction.value[1]
            
            # Check if move is valid (not into wall or itself)
            if (0 <= new_x < GRID_WIDTH and 
                0 <= new_y < GRID_HEIGHT and 
                (new_x, new_y) not in self.snake):
                
                # Calculate distance to food
                distance = abs(new_x - food_x) + abs(new_y - food_y)
                possible_moves.append((distance, direction))
        
        if possible_moves:
            # Pick move with smallest distance (avoid comparing Direction objects)
            _, best_direction = min(possible_moves, key=lambda t: t[0])
            
            # Only move if it's not opposite to current direction
            if best_direction != self.get_opposite_direction(self.direction):
                self.next_direction = best_direction
    
    def get_opposite_direction(self, direction):
        """Get the opposite direction"""
        opposites = {
            Direction.UP: Direction.DOWN,
            Direction.DOWN: Direction.UP,
            Direction.LEFT: Direction.RIGHT,
            Direction.RIGHT: Direction.LEFT
        }
        return opposites[direction]
    
    def update(self):
        """Update game state"""
        if self.game_over:
            return
        
        self.direction = self.next_direction
        
        # Move snake
        head_x, head_y = self.snake[0]
        dx, dy = self.direction.value
        new_head = (head_x + dx, head_y + dy)
        
        # Check collision with walls
        if not (0 <= new_head[0] < GRID_WIDTH and 0 <= new_head[1] < GRID_HEIGHT):
            self.game_over = True
            return
        
        # Check collision with self
        if new_head in self.snake:
            self.game_over = True
            return
        
        self.snake.appendleft(new_head)
        
        # Check if food is eaten
        if new_head == self.food:
            self.score += 10
            self.food = self.spawn_food()
        else:
            self.snake.pop()
    
    def draw(self):
        """Draw the game"""
        self.display.fill(BLACK)
        
        # Draw grid
        # Draw grid only in the playfield (below the top UI rows)
        top_px = TOP_ROWS * GRID_SIZE
        for x in range(0, WINDOW_WIDTH, GRID_SIZE):
            pygame.draw.line(self.display, (40, 40, 40), (x, top_px), (x, WINDOW_HEIGHT))
        for y in range(top_px, WINDOW_HEIGHT, GRID_SIZE):
            pygame.draw.line(self.display, (40, 40, 40), (0, y), (WINDOW_WIDTH, y))
        
        # Draw food
        # Draw food (offset by top UI rows)
        food_x, food_y = self.food
        pygame.draw.rect(self.display, RED, (food_x * GRID_SIZE, (food_y + TOP_ROWS) * GRID_SIZE, GRID_SIZE, GRID_SIZE))
        
        # Draw snake
        for i, (x, y) in enumerate(self.snake):
            color = GREEN if i == 0 else YELLOW  # Head is green, body is yellow
            pygame.draw.rect(self.display, color, (x * GRID_SIZE, (y + TOP_ROWS) * GRID_SIZE, GRID_SIZE, GRID_SIZE))
        
        # Draw title and UI in the reserved top area
        title_font = pygame.font.Font(None, 48)
        title_text = title_font.render("2D SNAKE GAMES", True, BLUE)
        title_rect = title_text.get_rect(center=(WINDOW_WIDTH // 2, 20))
        self.display.blit(title_text, title_rect)

        # Draw score and mode inside the top UI area (not over the grid)
        font = pygame.font.Font(None, 36)
        top_px = TOP_ROWS * GRID_SIZE
        ui_y = max(10, top_px - 30)
        score_text = font.render(f"Score: {self.score}", True, WHITE)
        self.display.blit(score_text, (10, ui_y))

        # Draw mode indicator on the right side of the top UI area
        mode_text = font.render("AI: {}".format("ON" if self.ai_mode else "OFF"), True, BLUE)
        mode_x = WINDOW_WIDTH - mode_text.get_width() - 10
        self.display.blit(mode_text, (mode_x, ui_y))
        
        # Draw game over message
        if self.game_over:
            # Center game over messages in the playfield (below the UI area)
            playfield_center_y = top_px + (WINDOW_HEIGHT - top_px) // 2
            large_font = pygame.font.Font(None, 72)
            game_over_text = large_font.render("GAME OVER", True, RED)
            text_rect = game_over_text.get_rect(center=(WINDOW_WIDTH // 2, playfield_center_y - 30))
            self.display.blit(game_over_text, text_rect)
            
            small_font = pygame.font.Font(None, 36)
            restart_text = small_font.render("Press SPACE to restart", True, WHITE)
            restart_rect = restart_text.get_rect(center=(WINDOW_WIDTH // 2, playfield_center_y + 30))
            self.display.blit(restart_text, restart_rect)
        
        pygame.display.flip()
    
    def run(self):
        """Main game loop"""
        running = True
        while running:
            running = self.handle_input()
            
            if self.ai_mode:
                self.ai_move()
            
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()

def main():
    """Main function to choose game mode (uses in-window menu)"""
    ai_mode = select_mode_ui()
    game = SnakeGame(ai_mode=ai_mode)

    print("\nControls:")
    print("- Arrow Keys or WASD to move")
    print("- SPACE to restart after game over")
    print("\nStarting game...")

    game.run()


def select_mode_ui():
    """Show a simple Pygame menu to choose No AI (player) or AI Mode.

    Returns:
        bool: True for AI Mode, False for No AI (player control).
    """
    # Create a temporary window for menu (use MENU_WIDTH/HEIGHT so menu size differs)
    screen = pygame.display.set_mode((MENU_WIDTH, MENU_HEIGHT))
    pygame.display.set_caption("2D Snake Games - Select Mode")
    # Try to set the same icon as the game window (load/generate/fallback)
    try:
        icon_surf = load_icon_or_create()
        pygame.display.set_icon(icon_surf)
    except Exception:
        pass

    font = pygame.font.Font(None, 48)
    small_font = pygame.font.Font(None, 32)

    button_w = 300
    button_h = 70
    gap = 30
    center_x = MENU_WIDTH // 2
    start_y = MENU_HEIGHT // 2 - (button_h + gap // 2)

    btn_no_ai = pygame.Rect(center_x - button_w // 2, start_y, button_w, button_h)
    btn_ai = pygame.Rect(center_x - button_w // 2, start_y + button_h + gap, button_w, button_h)

    clock = pygame.time.Clock()
    selecting = True
    selected_ai = False
    while selecting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    raise SystemExit()
                if event.key == pygame.K_1:
                    selected_ai = False
                    selecting = False
                if event.key == pygame.K_2:
                    selected_ai = True
                    selecting = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                if btn_no_ai.collidepoint(mx, my):
                    selected_ai = False
                    selecting = False
                if btn_ai.collidepoint(mx, my):
                    selected_ai = True
                    selecting = False

        screen.fill(BLACK)

        # Title
        title = font.render("2D SNAKE GAMES", True, WHITE)
        title_rect = title.get_rect(center=(MENU_WIDTH // 2, 100))
        screen.blit(title, title_rect)

        # Subtitle
        sub = small_font.render("Select mode: (1) No AI  (2) AI Mode or click a button", True, WHITE)
        sub_rect = sub.get_rect(center=(MENU_WIDTH // 2, 160))
        screen.blit(sub, sub_rect)

        # Draw buttons
        pygame.draw.rect(screen, (70, 130, 180), btn_no_ai)
        pygame.draw.rect(screen, (34, 177, 76), btn_ai)

        no_text = small_font.render("No AI (Player) - Press 1", True, WHITE)
        ai_text = small_font.render("AI Mode (Watch) - Press 2", True, WHITE)

        screen.blit(no_text, (btn_no_ai.x + 14, btn_no_ai.y + 20))
        screen.blit(ai_text, (btn_ai.x + 14, btn_ai.y + 20))

        # Footer
        foot = small_font.render("Use Arrow keys / WASD in player mode. Esc to quit.", True, (200, 200, 200))
        foot_rect = foot.get_rect(center=(MENU_WIDTH // 2, MENU_HEIGHT - 40))
        screen.blit(foot, foot_rect)

        pygame.display.flip()
        clock.tick(30)

    # Clear any pending events (mouse clicks) before starting the game
    pygame.event.clear()
    return selected_ai

if __name__ == "__main__":
    main()
