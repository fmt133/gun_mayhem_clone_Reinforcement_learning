import pygame
import random
import numpy as np

# Khởi tạo pygame
pygame.init()

# Kích thước màn hình
WIDTH, HEIGHT = 800, 600
# screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
screen = pygame.display.set_mode((WIDTH, HEIGHT))

pygame.display.set_caption("Gun Mayhem Clone")

# Màu sắc
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)

# FPS
clock = pygame.time.Clock()
FPS = 60

# Lớp nhân vật
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, color, controls=None, is_ai=False):
        super().__init__()
        self.image = pygame.Surface((40, 50))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.vel_x = 0
        self.vel_y = 0
        self.jump_power = -12
        self.gravity = 0.5
        self.on_ground = False
        self.speed = 5
        self.direction = 1
        self.controls = controls
        self.is_ai = is_ai
        self.shoot_cooldown = 0

    def update(self, platforms, bullets=None, target=None):
        self.vel_y += self.gravity
        self.rect.y += self.vel_y
        self.on_ground = False
        for platform in platforms:
            if self.rect.colliderect(platform.rect) and self.vel_y > 0:
                self.rect.bottom = platform.rect.top
                self.vel_y = 0
                self.on_ground = True
        
        self.rect.x += self.vel_x
        
        if self.is_ai and target:
            self.ai_behavior(target, bullets)
        
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
        
        if self.rect.top > HEIGHT or self.rect.right < 0 or self.rect.left > WIDTH:
            show_menu()

    def jump(self):
        if self.on_ground:
            self.vel_y = self.jump_power
            self.on_ground = False

    def move(self, direction):
        self.vel_x = direction * self.speed
        if direction != 0:
            self.direction = direction

    def shoot(self, bullets):
        if self.shoot_cooldown == 0:
            bullet = Bullet(self.rect.right if self.direction > 0 else self.rect.left, self.rect.centery, self.direction, self)
            bullets.add(bullet)
            self.shoot_cooldown = 20

    def ai_behavior(self, target, bullets):
        if abs(self.rect.x - target.rect.x) > 50:
            self.move(1 if self.rect.x < target.rect.x else -1)
        if random.randint(0, 100) < 5 and self.on_ground:
            self.jump()
        if self.shoot_cooldown <= 0 and random.randint(0, 100) < 10:
            self.shoot(bullets)
        for bullet in bullets:
            if bullet.rect.colliderect(self.rect.inflate(20, 20)):
                self.jump()

# Lớp đạn
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction, owner):
        super().__init__()
        self.image = pygame.Surface((10, 5))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = 10 * direction
        self.owner = owner
    
    def update(self):
        self.rect.x += self.speed
        if self.rect.right < 0 or self.rect.left > WIDTH:
            self.kill()
        
        for player in players:
            if player != self.owner and self.rect.colliderect(player.rect):
                knockback_direction = 1 if self.speed > 0 else -1
                player.rect.x += knockback_direction * 20  # Tăng lực đẩy lùi
                player.vel_x = knockback_direction * 5  # Cập nhật vận tốc để hiệu ứng rõ ràng hơn
                player.vel_y = -5  # Đẩy lên một chút để tạo hiệu ứng giật lùi
                self.kill()

# Q-learning AI cho bot
class QLearningAI:
    def __init__(self, actions, learning_rate=0.1, discount_factor=0.9, epsilon=0.1):
        self.q_table = {}
        self.actions = actions
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.epsilon = epsilon

    def get_q_values(self, state):
        return self.q_table.setdefault(state, np.zeros(len(self.actions)))

    def choose_action(self, state):
        if random.uniform(0, 1) < self.epsilon:
            return random.choice(self.actions)  # Chọn hành động ngẫu nhiên
        q_values = self.get_q_values(state)
        return self.actions[np.argmax(q_values)]  # Chọn hành động có giá trị Q cao nhất

    def update_q_value(self, state, action, reward, next_state):
        q_values = self.get_q_values(state)
        next_q_values = self.get_q_values(next_state)
        action_index = self.actions.index(action)
        q_values[action_index] += self.learning_rate * (reward + self.discount_factor * np.max(next_q_values) - q_values[action_index])

# Thêm AI bot sử dụng Q-learning
class AIBot(Player):
    def __init__(self, x, y, color):
        super().__init__(x, y, color, is_ai=True)
        self.ai = QLearningAI(actions=["left", "right", "jump", "shoot", "idle"])

    def ai_behavior(self, target, bullets):
        state = (self.rect.x, self.rect.y, target.rect.x, target.rect.y)
        action = self.ai.choose_action(state)
        
        if action == "left":
            self.move(-1)
        elif action == "right":
            self.move(1)
        elif action == "jump" and self.on_ground:
            self.jump()
        elif action == "shoot" and self.shoot_cooldown == 0:
            self.shoot(bullets)
        
        next_state = (self.rect.x, self.rect.y, target.rect.x, target.rect.y)
        reward = 0
        if self.rect.colliderect(target.rect):
            reward -= 10  # Trừ điểm nếu va chạm
        for bullet in bullets:
            if bullet.owner == self and bullet.rect.colliderect(target.rect):
                reward += 20  # Cộng điểm nếu bắn trúng
        
        self.ai.update_q_value(state, action, reward, next_state)
# Lớp nền tảng
class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

def show_menu():
    screen.fill(BLACK)
    font = pygame.font.Font(None, 74)
    text = font.render("New Game", True, WHITE)
    text_rect = text.get_rect(center=(WIDTH//2, HEIGHT//2))
    screen.blit(text, text_rect)
    pygame.display.flip()
    pygame.time.delay(2000)
    reset_game()

def reset_game():
    global players, bullets
    players.empty()
    bullets.empty()
    players.add(Player(300, 100, WHITE, {"left": pygame.K_LEFT, "right": pygame.K_RIGHT, "jump": pygame.K_UP, "shoot": pygame.K_RETURN}))
    players.add(Player(500, 100, GREEN, is_ai=True))

# Khởi tạo nhân vật
players = pygame.sprite.Group()
bullets = pygame.sprite.Group()
reset_game()

platforms = pygame.sprite.Group()
platforms.add(Platform(150, 500, 500, 20))
platforms.add(Platform(50, 400, 250, 20))
platforms.add(Platform(500, 400, 250, 20))
platforms.add(Platform(300, 300, 200, 20))
platforms.add(Platform(50, 550, 700, 20))
platforms.add(Platform(650, 300, 150, 20))
platforms.add(Platform(250, 200, 150, 20))
platforms.add(Platform(450, 200, 150, 20))

# Chạy trò chơi
running = True
while running:
    clock.tick(FPS)
    screen.fill(BLACK)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    keys = pygame.key.get_pressed()
    player1 = list(players)[0]
    player1.move(keys[player1.controls["right"]] - keys[player1.controls["left"]])
    if keys[player1.controls["jump"]]:
        player1.jump()
    if keys[player1.controls["shoot"]]:
        player1.shoot(bullets)
    
    players.update(platforms, bullets, list(players)[1])
    bullets.update()
    
    players.draw(screen)
    bullets.draw(screen)
    platforms.draw(screen)
    
    pygame.display.flip()

pygame.quit()