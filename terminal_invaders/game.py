import pygame
import time
import random
from constants import *
from entities import Player, Alien, Projectile
import save_system

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Terminal Invaders: Rogue Edition")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 24)
        self.bold_font = pygame.font.SysFont("Arial", 32, bold=True)

        # Load permanent upgrades
        save_data = save_system.load_game_data()
        perm_upgrades = save_data.get("permanent_upgrades", {})

        self.player = Player()
        health_boost = perm_upgrades.get("max_health", 0)
        self.player.max_health += health_boost
        self.player.health = self.player.max_health
        fr_boost = perm_upgrades.get("fire_rate_boost", 0)
        self.player.fire_rate *= (0.95 ** fr_boost)

        self.aliens = []
        self.projectiles = []
        self.enemy_projectiles = []
        self.game_over = False
        self.paused = False
        self.current_wave = 1
        self.alien_direction = 1 # 1: down, -1: up
        self.alien_move_timer = 0
        self.alien_speed = ALIEN_INITIAL_SPEED

        self.setup_aliens()

    def setup_aliens(self):
        self.aliens = []
        cols = ALIEN_COLS + (self.current_wave // 2)
        rows = ALIEN_ROWS + (self.current_wave // 3)
        start_x = SCREEN_WIDTH - 50
        start_y = (SCREEN_HEIGHT - (rows * ALIEN_SPACING_Y)) // 2

        for col in range(cols):
            for row in range(rows):
                x = start_x - (col * ALIEN_SPACING_X)
                y = start_y + (row * ALIEN_SPACING_Y)
                if y >= SCREEN_HEIGHT: continue
                rand = random.random()
                tank_chance = 0.2 + (self.current_wave * 0.02)
                bomber_chance = 0.1 + (self.current_wave * 0.03)
                if rand < tank_chance:
                    self.aliens.append(Alien(x, y, health=3 + (self.current_wave // 5), xp_value=3, color=COLOR_TANK, alien_type="tank"))
                elif rand < tank_chance + bomber_chance:
                    self.aliens.append(Alien(x, y, health=1, xp_value=2, color=COLOR_BOMBER, alien_type="bomber"))
                else:
                    self.aliens.append(Alien(x, y, health=1, xp_value=1, color=COLOR_ALIEN, alien_type="regular"))

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    return False
                if event.key == pygame.K_p:
                    self.paused = not self.paused

        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            self.player.move(-1)
        if keys[pygame.K_DOWN]:
            self.player.move(1)
        if keys[pygame.K_SPACE]:
            self.shoot()
        return True

    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.player.last_shot_time >= self.player.fire_rate:
            for i in range(self.player.projectiles_per_shot):
                offset = (i - (self.player.projectiles_per_shot - 1) / 2) * 10
                self.projectiles.append(Projectile(self.player.rect.right, self.player.rect.centery + offset))
            self.player.last_shot_time = now

    def update(self):
        if self.paused: return

        for p in self.projectiles: p.update(SCREEN_WIDTH)
        self.projectiles = [p for p in self.projectiles if p.active]

        for ep in self.enemy_projectiles: ep.update(SCREEN_WIDTH)
        self.enemy_projectiles = [ep for ep in self.enemy_projectiles if ep.active]

        # Corrected Alien Movement Logic
        hit_boundary = False
        for a in self.aliens:
            if a.active:
                # check boundaries
                if (self.alien_direction == 1 and a.rect.bottom >= SCREEN_HEIGHT - 20) or \
                   (self.alien_direction == -1 and a.rect.top <= 20):
                    hit_boundary = True
                    break

        if hit_boundary:
            self.alien_direction *= -1 # Reverse vertical direction
            for a in self.aliens:
                if a.active:
                    a.update(-15, 0) # Move a bit closer to player
        else:
            for a in self.aliens:
                if a.active:
                    a.update(0, self.alien_direction * self.alien_speed)

        if random.random() < 0.02:
            bombers = [a for a in self.aliens if a.active and a.alien_type == "bomber"]
            if bombers:
                b = random.choice(bombers)
                self.enemy_projectiles.append(Projectile(b.rect.left, b.rect.centery, direction=-1, color=COLOR_ENEMY_PROJ, char="*"))

        for p in self.projectiles:
            for a in self.aliens:
                if a.active and p.rect.colliderect(a.rect):
                    a.health -= 1
                    if a.health <= 0:
                        a.active = False
                        self.player.score += 10
                        self.player.xp += a.xp_value
                        save_system.add_credits(1)
                        self.check_level_up()
                    if self.player.piercing <= 0:
                        p.active = False
                    else:
                        self.player.piercing -= 1

        for ep in self.enemy_projectiles:
            if ep.rect.colliderect(self.player.rect):
                ep.active = False
                self.player.health -= 1
                if self.player.health <= 0:
                    self.game_over = True

        if all(not a.active for a in self.aliens):
            self.current_wave += 1
            self.alien_speed += 0.5
            self.setup_aliens()

        for a in self.aliens:
            if a.active and a.rect.left <= self.player.rect.right:
                self.game_over = True

    def check_level_up(self):
        if self.player.xp >= self.player.xp_to_next_level:
            self.player.xp -= self.player.xp_to_next_level
            self.player.level += 1
            self.player.xp_to_next_level = int(self.player.xp_to_next_level * 1.5)
            self.show_upgrade_menu()

    def show_upgrade_menu(self):
        self.paused = True
        upgrades = [
            ("Double Shot", "proj_count"),
            ("Rapid Fire", "fire_rate"),
            ("Piercing", "piercing"),
            ("Speed", "player_speed"),
        ]
        choices = random.sample(upgrades, 3)
        waiting = True
        while waiting:
            self.screen.fill(COLOR_BLACK)
            txt = self.bold_font.render("LEVEL UP! Press 1, 2, or 3", True, COLOR_WHITE)
            self.screen.blit(txt, (SCREEN_WIDTH // 2 - txt.get_width() // 2, 200))
            for i, (name, key) in enumerate(choices):
                opt_txt = self.font.render(f"{i+1}. {name}", True, COLOR_WHITE)
                self.screen.blit(opt_txt, (SCREEN_WIDTH // 2 - 100, 300 + i * 40))
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1: self.apply_upgrade(choices[0][1]); waiting = False
                    if event.key == pygame.K_2: self.apply_upgrade(choices[1][1]); waiting = False
                    if event.key == pygame.K_3: self.apply_upgrade(choices[2][1]); waiting = False

    def apply_upgrade(self, utype):
        if utype == "proj_count": self.player.projectiles_per_shot += 1
        elif utype == "fire_rate": self.player.fire_rate = max(100, self.player.fire_rate * 0.8)
        elif utype == "piercing": self.player.piercing += 1
        self.paused = False

    def draw(self):
        self.screen.fill(COLOR_BLACK)
        health_bar = "#" * self.player.health + "-" * (self.player.max_health - self.player.health)
        status = f"Wave: {self.current_wave} | Score: {self.player.score} | HP: [{health_bar}]"
        ui_txt = self.font.render(status, True, COLOR_WHITE)
        self.screen.blit(ui_txt, (10, 10))
        self.player.draw(self.screen)
        for a in self.aliens: a.draw(self.screen)
        for p in self.projectiles: p.draw(self.screen)
        for ep in self.enemy_projectiles: ep.draw(self.screen)
        if self.game_over:
            msg = self.bold_font.render("GAME OVER!", True, COLOR_RED)
            self.screen.blit(msg, (SCREEN_WIDTH // 2 - msg.get_width() // 2, SCREEN_HEIGHT // 2))
        pygame.display.flip()

    def run(self):
        while not self.game_over:
            if not self.handle_input(): break
            self.update()
            self.draw()
            self.clock.tick(FPS)
        self.draw()
        time.sleep(2)
        pygame.quit()
