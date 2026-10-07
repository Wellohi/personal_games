import pygame
from constants import *

class Projectile:
    def __init__(self, x, y, direction=1, color=COLOR_PROJECTILE, char=None):
        self.rect = pygame.Rect(x, y, PROJ_WIDTH, PROJ_HEIGHT)
        self.direction = direction # 1 for right, -1 for left
        self.color = color
        self.char = char
        self.active = True

    def update(self, screen_width):
        if self.direction == 1:
            self.rect.x += PROJECTILE_SPEED
        else:
            self.rect.x -= PROJECTILE_SPEED

        if self.rect.right < 0 or self.rect.left > screen_width:
            self.active = False

    def draw(self, screen):
        if self.active:
            pygame.draw.circle(screen, self.color, self.rect.center, PROJ_WIDTH // 2)

class Player:
    def __init__(self):
        self.rect = pygame.Rect(PLAYER_START_X, SCREEN_HEIGHT // 2, PLAYER_WIDTH, PLAYER_HEIGHT)
        self.score = 0
        self.level = 1
        self.xp = 0
        self.xp_to_next_level = 10
        self.fire_rate = 500 # Milliseconds
        self.last_shot_time = 0
        self.projectiles_per_shot = 1
        self.piercing = 0
        self.max_health = 3
        self.health = 3
        self.font = pygame.font.SysFont("Consolas", 20)

    def move(self, dy):
        self.rect.y += dy * PLAYER_SPEED
        self.rect.top = max(0, min(self.rect.top, SCREEN_HEIGHT - self.rect.height))

    def draw(self, screen):
        text = self.font.render("A", True, PLAYER_COLOR)
        screen.blit(text, (self.rect.x, self.rect.y))

class Alien:
    def __init__(self, x, y, health=1, xp_value=1, color=COLOR_ALIEN, alien_type="regular"):
        self.rect = pygame.Rect(x, y, ALIEN_WIDTH, ALIEN_HEIGHT)
        self.health = health
        self.max_health = health
        self.xp_value = xp_value
        self.color = color
        self.alien_type = alien_type
        self.active = True
        self.font = pygame.font.SysFont("Consolas", 16)

    def update(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy

    def draw(self, screen):
        if self.active:
            char = "B" if self.alien_type == "boss" else "M"
            text = self.font.render(char, True, self.color)
            screen.blit(text, (self.rect.x, self.rect.y))
