import pygame
import time
import random
from constants import *
from entities import Player, Alien, Projectile, Scout, Tank, Bomber, Shifter, BossAlien
import save_system

class WaveManager:
    def __init__(self):
        self.current_wave = 1
        self.alien_speed = ALIEN_INITIAL_SPEED
        self.alien_direction = 1

    def get_wave_settings(self):
        # Scale counts and speed based on wave
        cols = ALIEN_COLS + (self.current_wave // 2)
        rows = ALIEN_ROWS + (self.current_wave // 3)
        return cols, rows, self.alien_speed

    def next_wave(self):
        self.current_wave += 1
        self.alien_speed += 0.3
        return self.current_wave

    def is_boss_wave(self):
        return self.current_wave % 5 == 0

class Game:
    def __init__(self):
        pygame.init()
        # Use RESIZABLE flag to allow window resizing
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption("Terminal Invaders: Rogue Edition")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 24)
        self.bold_font = pygame.font.SysFont("Arial", 32, bold=True)

        self.player = Player()
        self.wave_manager = WaveManager()

        self.aliens = []
        self.projectiles = []
        self.enemy_projectiles = []

        # Game States
        self.state = "MENU" # MENU, SHOP, PLAYING, WAVE_CLEAR, GAMEOVER
        self.game_over = False
        self.paused = False

        self.setup_aliens()

    def setup_aliens(self):
        self.aliens = []
        cols, rows, speed = self.wave_manager.get_wave_settings()
        start_x = SCREEN_WIDTH - 50
        start_y = (SCREEN_HEIGHT - (rows * ALIEN_SPACING_Y)) // 2

        if self.wave_manager.is_boss_wave():
            # Spawn one big boss in the center
            self.aliens.append(BossAlien(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, self.wave_manager.current_wave))
            return

        for col in range(cols):
            for row in range(rows):
                x = start_x - (col * ALIEN_SPACING_X)
                y = start_y + (row * ALIEN_SPACING_Y)
                if y >= SCREEN_HEIGHT: continue

                rand = random.random()
                tank_chance = 0.15 + (self.wave_manager.current_wave * 0.01)
                bomber_chance = 0.15 + (self.wave_manager.current_wave * 0.01)
                shifter_chance = 0.10 + (self.wave_manager.current_wave * 0.01)

                if rand < tank_chance:
                    self.aliens.append(Tank(x, y))
                elif rand < tank_chance + bomber_chance:
                    self.aliens.append(Bomber(x, y))
                elif rand < tank_chance + bomber_chance + shifter_chance:
                    self.aliens.append(Shifter(x, y))
                else:
                    self.aliens.append(Scout(x, y))

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.VIDEORESIZE:
                # Update screen size on resize
                self.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    return False
                if event.key == pygame.K_p:
                    self.paused = not self.paused

                if self.state == "WAVE_CLEAR" and event.key == pygame.K_SPACE:
                    self.wave_manager.next_wave()
                    self.setup_aliens()
                    self.state = "PLAYING"

        keys = pygame.key.get_pressed()
        if self.state == "PLAYING":
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
                if (self.wave_manager.alien_direction == 1 and a.rect.bottom >= SCREEN_HEIGHT - 20) or \
                   (self.wave_manager.alien_direction == -1 and a.rect.top <= 20):
                    hit_boundary = True
                    break

        if hit_boundary:
            self.alien_direction *= -1 # Reverse vertical direction
            for a in self.aliens:
                if a.active:
                    # We use the alien's own update to handle the X-shift
                    # and we pass 0 for dy since we just reversed direction
                    a.update(-15, 0)
        else:
            for a in self.aliens:
                if a.active:
                    # Only update the shared vertical movement
                    # The entities handle their own x-logic (like Shifters)
                    a.update(0, self.alien_direction * self.alien_speed)

        # Decentralized Firing Logic
        for a in self.aliens:
            if a.active and a.should_fire():
                self.enemy_projectiles.append(Projectile(a.rect.left, a.rect.centery, direction=-1, color=COLOR_ENEMY_PROJ))

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

        if self.state == "WAVE_CLEAR":
            txt = self.bold_font.render("WAVE CLEAR!", True, COLOR_GREEN)
            self.screen.blit(txt, (self.screen.get_width() // 2 - txt.get_width() // 2, self.screen.get_height() // 2 - 50))
            instr = self.font.render("Press SPACE to start next wave", True, COLOR_WHITE)
            self.screen.blit(instr, (self.screen.get_width() // 2 - instr.get_width() // 2, self.screen.get_height() // 2 + 20))
            pygame.display.flip()
            return

        health_bar = "#" * self.player.health + "-" * (self.player.max_health - self.player.health)
        status = f"Wave: {self.wave_manager.current_wave} | Score: {self.player.score} | HP: [{health_bar}]"
        ui_txt = self.font.render(status, True, COLOR_WHITE)
        self.screen.blit(ui_txt, (10, 10))
        self.player.draw(self.screen)
        for a in self.aliens: a.draw(self.screen)
        for p in self.projectiles: p.draw(self.screen)
        for ep in self.enemy_projectiles: ep.draw(self.screen)
        if self.game_over:
            msg = self.bold_font.render("GAME OVER!", True, COLOR_RED)
            self.screen.blit(msg, (self.screen.get_width() // 2 - msg.get_width() // 2, self.screen.get_height() // 2))
        pygame.display.flip()

    def run(self):
        while True:
            if not self.show_main_menu():
                pygame.quit()
                return

            if not self.show_shop():
                pygame.quit()
                return

            # Reset game state for a new run
            self.game_over = False
            self.paused = False
            self.wave_manager = WaveManager()
            self.player.health = self.player.max_health
            self.player.score = 0
            self.player.xp = 0
            self.player.level = 1
            self.player.xp_to_next_level = 10

            # Load permanent upgrades
            save_data = save_system.load_game_data()
            self.player.apply_permanent_upgrades(save_data.get("permanent_upgrades", {}))

            self.setup_aliens()
            self.state = "PLAYING"

            while not self.game_over:
                if not self.handle_input():
                    pygame.quit()
                    return
                self.update()
                self.draw()
                self.clock.tick(FPS)

            self.draw()
            time.sleep(2)
            # Instead of quitting, we loop back to the main menu

    def show_main_menu(self):
        waiting = True
        while waiting:
            self.screen.fill(COLOR_BLACK)
            title = self.bold_font.render("TERMINAL INVADERS", True, COLOR_WHITE)
            self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 150))

            options = ["1. Start Game", "2. Settings", "3. Quit"]
            for i, opt in enumerate(options):
                opt_txt = self.font.render(opt, True, COLOR_WHITE)
                self.screen.blit(opt_txt, (SCREEN_WIDTH // 2 - opt_txt.get_width() // 2, 300 + i * 50))

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1:
                        return True
                    if event.key == pygame.K_2:
                        self.show_settings()
                    if event.key == pygame.K_3:
                        return False
        return False

    def show_settings(self):
        waiting = True
        while waiting:
            self.screen.fill(COLOR_BLACK)
            title = self.bold_font.render("SETTINGS", True, COLOR_WHITE)
            self.screen.blit(title, (self.screen.get_width() // 2 - title.get_width() // 2, 150))

            instructions = "Window is now Resizable!"
            instr_txt = self.font.render(instructions, True, COLOR_WHITE)
            self.screen.blit(instr_txt, (self.screen.get_width() // 2 - instr_txt.get_width() // 2, 250))

            scale_txt = self.font.render("Game elements scale automatically to window size", True, COLOR_YELLOW)
            self.screen.blit(scale_txt, (self.screen.get_width() // 2 - scale_txt.get_width() // 2, 300))

            back_txt = self.font.render("Press 'B' to go Back", True, COLOR_WHITE)
            self.screen.blit(back_txt, (self.screen.get_width() // 2 - back_txt.get_width() // 2, 400))

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.VIDEORESIZE:
                    self.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_b:
                        waiting = False
        return False

    def show_shop(self):
        waiting = True
        while waiting:
            self.screen.fill(COLOR_BLACK)
            data = save_system.load_game_data()
            credits = data.get("total_credits", 0)
            perm = data.get("permanent_upgrades", {})

            title = self.bold_font.render("--- PERMANENT SHOP ---", True, COLOR_WHITE)
            self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 50))

            credits_txt = self.font.render(f"Total Credits: {credits}", True, COLOR_YELLOW)
            self.screen.blit(credits_txt, (SCREEN_WIDTH // 2 - credits_txt.get_width() // 2, 100))

            upgrades = [
                ("Max Health (+1)", 50, "max_health"),
                ("Fire Rate Boost", 100, "fire_rate_boost"),
                ("Starting XP (+5)", 30, "starting_xp"),
            ]

            for i, (name, cost, key) in enumerate(upgrades):
                level = perm.get(key, 0)
                upg_txt = self.font.render(f"{i+1}. {name} (Lvl {level}) - Cost: {cost}", True, COLOR_WHITE)
                self.screen.blit(upg_txt, (SCREEN_WIDTH // 2 - 150, 200 + i * 50))

            start_txt = self.font.render("Press 'S' to Start Game", True, COLOR_GREEN)
            self.screen.blit(start_txt, (SCREEN_WIDTH // 2 - start_txt.get_width() // 2, 450))

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_s:
                        return True
                    elif event.key == pygame.K_1:
                        save_system.buy_upgrade("max_health", 50)
                    elif event.key == pygame.K_2:
                        save_system.buy_upgrade("fire_rate_boost", 100)
                    elif event.key == pygame.K_3:
                        save_system.buy_upgrade("starting_xp", 30)
        return False

