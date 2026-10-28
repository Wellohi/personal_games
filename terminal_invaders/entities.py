import pygame
import math
import random
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

    def apply_permanent_upgrades(self, upgrades):
        # upgrades is a dict: {"max_health": level, "fire_rate_boost": level, ...}
        health_boost = upgrades.get("max_health", 0)
        self.max_health += health_boost
        self.health = self.max_health

        fr_boost = upgrades.get("fire_rate_boost", 0)
        self.fire_rate *= (0.95 ** fr_boost)

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

    def should_fire(self):
        return False # Base class doesn't fire

    def draw(self, screen):
        if self.active:
            char = "M"
            text = self.font.render(char, True, self.color)
            screen.blit(text, (self.rect.x, self.rect.y))

class Scout(Alien):
    def __init__(self, x, y, **kwargs):
        super().__init__(x, y, health=1, xp_value=1, color=COLOR_SCOUT, alien_type="scout", **kwargs)

    def update(self, dx, dy):
        # Scouts move at the same vertical speed as others to avoid breaking the fleet loop
        super().update(dx, dy)

    def draw(self, screen):
        if self.active:
            text = self.font.render("S", True, self.color)
            screen.blit(text, (self.rect.x, self.rect.y))

class Tank(Alien):
    def __init__(self, x, y, **kwargs):
        super().__init__(x, y, health=3, xp_value=3, color=COLOR_TANK, alien_type="tank", **kwargs)

    def draw(self, screen):
        if self.active:
            text = self.font.render("T", True, self.color)
            screen.blit(text, (self.rect.x, self.rect.y))

class Bomber(Alien):
    def __init__(self, x, y, **kwargs):
        super().__init__(x, y, health=1, xp_value=2, color=COLOR_BOMBER, alien_type="bomber", **kwargs)
        self.fire_timer = random.randint(0, 2000)

    def should_fire(self):
        self.fire_timer += 16 # Approx 60 FPS
        if self.fire_timer >= 2000: # Fire every 2 seconds
            self.fire_timer = 0
            return True
        return False

    def draw(self, screen):
        if self.active:
            text = self.font.render("B", True, self.color)
            screen.blit(text, (self.rect.x, self.rect.y))

class Shifter(Alien):
    def __init__(self, x, y, **kwargs):
        super().__init__(x, y, health=1, xp_value=2, color=COLOR_SHIFTER, alien_type="shifter", **kwargs)
        self.base_x = x
        self.timer = 0

    def update(self, dx, dy):
        self.timer += 0.05
        # Weave horizontally using sine wave
        offset = math.sin(self.timer) * 20
        self.base_x += dx
        self.rect.x = self.base_x + offset
        self.rect.y += dy

    def draw(self, screen):
        if self.active:
            text = self.font.render("X", True, self.color)
            screen.blit(text, (self.rect.x, self.rect.y))

class BossAlien(Alien):
    def __init__(self, x, y, wave):
        # Bosses have huge health that scales with wave
        health = 20 + (wave * 5)
        super().__init__(x, y, health=health, xp_value=50, color=COLOR_BOSS, alien_type="boss")
        self.fire_timer = 0

    def should_fire(self):
        self.fire_timer += 16
        if self.fire_timer >= 1000: # Fires more frequently than bombers
            self.fire_timer = 0
            return True
        return False

    def draw(self, screen):
        if self.active:
            # Render the boss character
            text = self.font.render("B", True, self.color)
            screen.blit(text, (self.rect.x, self.rect.y))

            # Render a small health bar above the boss
            bar_width = 40
            bar_height = 5
            fill_width = int((self.health / self.max_health) * bar_width)

            pygame.draw.rect(screen, (100, 0, 0), (self.rect.x, self.rect.y - 10, bar_width, bar_height))
            pygame.draw.rect(screen, (0, 255, 0), (self.rect.x, self.rect.y - 10, fill_width, bar_height))
