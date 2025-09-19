# main.py — To'liq, tekshirilgan Snake o'yini (Pydroid3 / Android)
import pygame, random, sys, os

pygame.init()

# ----------- Ekran / o'lchamlar -----------
info = pygame.display.Info()
WIDTH = info.current_w if info.current_w and info.current_w > 200 else 800
HEIGHT = info.current_h if info.current_h and info.current_h > 300 else 1280
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ilon o'yini — Mukammal")

clock = pygame.time.Clock()

# ----------- Panel balandligi (pastki joystik panel) -----------
PANEL_H = max(int(HEIGHT * 0.25), 180)  # kattaroq panel, o'yin zonasini qisqartiradi
GAME_H = HEIGHT - PANEL_H

# CELL_SIZE avtomatik, katta va mos bo'lsin (minimal qiymat 30)
CELL_SIZE = min(WIDTH // 12, GAME_H // 14)
if CELL_SIZE < 30:
    CELL_SIZE = 30

# Grid o'lchamlari
GRID_W = WIDTH // CELL_SIZE
GRID_H = GAME_H // CELL_SIZE

# Pixelga o'tkazish offset (markazlash uchun)
GRID_PX_W = GRID_W * CELL_SIZE
GRID_PX_H = GRID_H * CELL_SIZE
OFFSET_X = (WIDTH - GRID_PX_W) // 2
OFFSET_Y = 0

# Ranglar
GREEN_BG = (34, 153, 84)
WALL = (230, 230, 230)
SNAKE_BODY = (20, 20, 20)
FOOD_COLOR = (200, 40, 40)
PANEL_BG = (12, 12, 12)
BTN_COLOR = (240, 240, 240)
TXT_COLOR = (255, 255, 255)

# ----------- Harakat tezligi (millisekundda bir qadam) -----------
MOVE_MS = 300  # sekinroq ilon (oldingi 220 -> 300)
MOVE_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(MOVE_EVENT, MOVE_MS)

# HEAD IMAGE yuklash
HEAD_IMG = None
try:
    base_path = os.path.dirname(__file__) if '__file__' in globals() else ""
    img_path = os.path.join(base_path, "head.png") if base_path else "head.png"
    if not os.path.exists(img_path):
        img_path = "head.png"
    HEAD_IMG = pygame.image.load(img_path).convert_alpha()
    HEAD_IMG = pygame.transform.smoothscale(HEAD_IMG, (CELL_SIZE, CELL_SIZE))
except Exception:
    HEAD_IMG = None

# Font
font = pygame.font.SysFont(None, max(20, CELL_SIZE // 2))

# Joystick button size & positions (panel zone)
btn_size = max(int(PANEL_H * 0.45), 64)
panel_top = GAME_H
center_x = WIDTH // 2
center_y = panel_top + PANEL_H // 2

btn_up = pygame.Rect(center_x - btn_size//2, panel_top + 6, btn_size, btn_size)
btn_down = pygame.Rect(center_x - btn_size//2, panel_top + PANEL_H - btn_size - 6, btn_size, btn_size)
btn_left = pygame.Rect(center_x - btn_size - 20 - btn_size//2, panel_top + PANEL_H//2 - btn_size//2, btn_size, btn_size)
btn_right = pygame.Rect(center_x + btn_size//2 + 20, panel_top + PANEL_H//2 - btn_size//2, btn_size, btn_size)

# Start/Restart button rectangles
btn_w = min(360, GRID_PX_W - 40)
btn_h = 64
btn_start = pygame.Rect((WIDTH - btn_w)//2, (GAME_H - btn_h)//2 - 36, btn_w, btn_h)
btn_restart = pygame.Rect((WIDTH - btn_w)//2, (GAME_H - btn_h)//2 + 36, btn_w, btn_h)

# Game state
game_active = False
game_over = False
score = 0

# Grid helpers
def grid_to_pixel(gx, gy):
    return OFFSET_X + gx * CELL_SIZE, OFFSET_Y + gy * CELL_SIZE

def random_food_pos(snake):
    attempts = 0
    while True:
        fx = random.randint(1, GRID_W - 2)
        fy = random.randint(1, GRID_H - 2)
        if (fx, fy) not in snake:
            return fx, fy
        attempts += 1
        if attempts > 2000:
            return 1,1

# Initialize snake/direction/food
def start_game():
    global snake, direction, food, game_active, game_over, score
    midx = GRID_W // 2
    midy = GRID_H // 2
    snake = [(midx, midy), (midx-1, midy), (midx-2, midy)]
    direction = (1, 0)
    food = random_food_pos(snake)
    game_active = True
    game_over = False
    score = 0

# Draw functions
def draw_game_area():
    pygame.draw.rect(screen, GREEN_BG, (OFFSET_X, OFFSET_Y, GRID_PX_W, GRID_PX_H))
    for x in range(GRID_W):
        px, py = grid_to_pixel(x, 0)
        pygame.draw.rect(screen, WALL, (px, py, CELL_SIZE, CELL_SIZE))
        px, py = grid_to_pixel(x, GRID_H - 1)
        pygame.draw.rect(screen, WALL, (px, py, CELL_SIZE, CELL_SIZE))
    for y in range(GRID_H):
        px, py = grid_to_pixel(0, y)
        pygame.draw.rect(screen, WALL, (px, py, CELL_SIZE, CELL_SIZE))
        px, py = grid_to_pixel(GRID_W - 1, y)
        pygame.draw.rect(screen, WALL, (px, py, CELL_SIZE, CELL_SIZE))

def draw_food():
    fx, fy = food
    fx_px, fy_px = grid_to_pixel(fx, fy)
    pygame.draw.rect(screen, FOOD_COLOR, (fx_px+6, fy_px+6, CELL_SIZE-12, CELL_SIZE-12), border_radius=8)

def draw_snake():
    for i, (sx, sy) in enumerate(snake):
        sx_px, sy_px = grid_to_pixel(sx, sy)
        if i == 0:
            if HEAD_IMG:
                screen.blit(HEAD_IMG, (sx_px, sy_px))
            else:
                pygame.draw.rect(screen, (200,180,40), (sx_px+4, sy_px+4, CELL_SIZE-8, CELL_SIZE-8), border_radius=8)
        else:
            pygame.draw.rect(screen, SNAKE_BODY, (sx_px+6, sy_px+6, CELL_SIZE-12, CELL_SIZE-12), border_radius=8)

def draw_panel():
    pygame.draw.rect(screen, PANEL_BG, (0, GAME_H, WIDTH, PANEL_H))
    pygame.draw.ellipse(screen, BTN_COLOR, btn_up)
    pygame.draw.ellipse(screen, BTN_COLOR, btn_down)
    pygame.draw.ellipse(screen, BTN_COLOR, btn_left)
    pygame.draw.ellipse(screen, BTN_COLOR, btn_right)
    small = pygame.font.SysFont(None, max(20, btn_size//3))
    screen.blit(small.render("↑", True, (0,0,0)), (btn_up.centerx - 8, btn_up.centery - 16))
    screen.blit(small.render("↓", True, (0,0,0)), (btn_down.centerx - 8, btn_down.centery - 16))
    screen.blit(small.render("←", True, (0,0,0)), (btn_left.centerx - 10, btn_left.centery - 16))
    screen.blit(small.render("→", True, (0,0,0)), (btn_right.centerx - 8, btn_right.centery - 16))
    score_surf = font.render(f"Score: {score}", True, TXT_COLOR)
    screen.blit(score_surf, (OFFSET_X + 8, 8))

def draw_start_screen():
    draw_game_area()
    draw_food()
    draw_snake()
    overlay = pygame.Surface((GRID_PX_W, GRID_PX_H), pygame.SRCALPHA)
    overlay.fill((0,0,0,120))
    screen.blit(overlay, (OFFSET_X, OFFSET_Y))
    pygame.draw.rect(screen, BTN_COLOR, btn_start, border_radius=10)
    pygame.draw.rect(screen, BTN_COLOR, btn_restart, border_radius=10)
    label = font.render("START", True, (0,0,0))
    screen.blit(label, (btn_start.x + (btn_start.width - label.get_width())//2, btn_start.y + 12))
    label2 = font.render("EXIT", True, (0,0,0))
    screen.blit(label2, (btn_restart.x + (btn_restart.width - label2.get_width())//2, btn_restart.y + 12))

def draw_game_over():
    draw_game_area()
    draw_food()
    draw_snake()
    overlay = pygame.Surface((GRID_PX_W, GRID_PX_H), pygame.SRCALPHA)
    overlay.fill((0,0,0,160))
    screen.blit(overlay, (OFFSET_X, OFFSET_Y))
    big = pygame.font.SysFont(None, max(36, CELL_SIZE))
    text = big.render("GAME OVER", True, (255,255,255))
    screen.blit(text, (OFFSET_X + (GRID_PX_W - text.get_width())//2, OFFSET_Y + (GRID_PX_H//2 - 40)))
    pygame.draw.rect(screen, BTN_COLOR, btn_restart, border_radius=10)
    label2 = font.render("RESTART", True, (0,0,0))
    screen.blit(label2, (btn_restart.x + (btn_restart.width - label2.get_width())//2, btn_restart.y + 12))

# Prepare initial data
snake = []
direction = (1, 0)
food = (1,1)
start_game()
game_active = False
game_over = False

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == MOVE_EVENT:
            if game_active and not game_over:
                hx, hy = snake[0]
                nx, ny = hx + direction[0], hy + direction[1]
                if nx <= 0 or nx >= GRID_W - 1 or ny <= 0 or ny >= GRID_H - 1 or (nx, ny) in snake:
                    game_over = True
                    game_active = False
                else:
                    snake.insert(0, (nx, ny))
                    if (nx, ny) == food:
                        score += 1
                        food = random_food_pos(snake)
                    else:
                        snake.pop()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            if not game_active and not game_over:
                if btn_start.collidepoint((mx, my)):
                    start_game(); game_active = True; game_over = False
                elif btn_restart.collidepoint((mx, my)):
                    start_game(); game_active = True; game_over = False
            elif game_over and btn_restart.collidepoint((mx, my)):
                start_game(); game_active = True; game_over = False
            elif game_active:
                if btn_left.collidepoint((mx, my)) and direction != (1, 0):
                    direction = (-1, 0)
                elif btn_right.collidepoint((mx, my)) and direction != (-1, 0):
                    direction = (1, 0)
                elif btn_up.collidepoint((mx, my)) and direction != (0, 1):
                    direction = (0, -1)
                elif btn_down.collidepoint((mx, my)) and direction != (0, -1):
                    direction = (0, 1)
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT and direction != (1, 0):
                direction = (-1, 0)
            elif event.key == pygame.K_RIGHT and direction != (-1, 0):
                direction = (1, 0)
            elif event.key == pygame.K_UP and direction != (0, 1):
                direction = (0, -1)
            elif event.key == pygame.K_DOWN and direction != (0, -1):
                direction = (0, 1)
            elif event.key == pygame.K_SPACE and not game_active:
                start_game(); game_active = True; game_over = False

    # Draw
    screen.fill((18, 18, 18))
    if not game_active and not game_over:
        draw_start_screen()
    elif game_over:
        draw_game_over()
    else:
        draw_game_area()
        draw_food()
        draw_snake()
        draw_panel()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()