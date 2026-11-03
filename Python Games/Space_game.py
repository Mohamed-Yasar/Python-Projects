import pygame
import random
import math

# --- CONFIGURATION ---
WIDTH, HEIGHT = 1200, 800
FPS = 60
NEON_CYAN = (0, 255, 255)
NEON_MAGENTA = (255, 0, 255)
NEON_LIME = (50, 255, 50)
NEON_ORANGE = (255, 100, 50)
NEON_WHITE = (220, 220, 255)

# --- INIT ---
pygame.init()
pygame.display.set_caption("NEON INFINITE // THE VOID")
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()


# --- UTILS ---
def approach(val, target, amount):
    if val < target: return min(val + amount, target)
    if val > target: return max(val - amount, target)
    return val


class Vector2:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, o): return Vector2(self.x + o.x, self.y + o.y)

    def __sub__(self, o): return Vector2(self.x - o.x, self.y - o.y)

    def __mul__(self, s): return Vector2(self.x * s, self.y * s)

    def length(self): return math.sqrt(self.x ** 2 + self.y ** 2)

    def normalize(self):
        l = self.length()
        if l != 0: return Vector2(self.x / l, self.y / l)
        return Vector2(0, 0)

    def astuple(self): return (int(self.x), int(self.y))


# --- PARTICLES ---
class Particle:
    def __init__(self, x, y, color, life=60, speed=2, decay=0.95):
        self.pos = Vector2(x, y)
        angle = random.uniform(0, math.pi * 2)
        v = random.uniform(0.5, speed)
        self.vel = Vector2(math.cos(angle) * v, math.sin(angle) * v)
        self.color = color
        self.life = float(life)
        self.max_life = float(life)
        self.decay = decay

    def update(self):
        self.pos = self.pos + self.vel
        self.vel = self.vel * self.decay
        self.life -= 1
        return self.life > 0

    def draw(self, surf):
        alpha = int((self.life / self.max_life) * 255)
        # Additive blending simulation by drawing layers
        # Center core
        pygame.draw.circle(surf, self.color, self.pos.astuple(), 2)
        # Glow
        radius = 4 * (self.life / self.max_life)
        glow_surf = pygame.Surface((radius * 4, radius * 4), pygame.SRCALPHA)
        c = (self.color[0], self.color[1], self.color[2], alpha * 0.5)
        pygame.draw.circle(glow_surf, c, (radius * 2, radius * 2), radius)
        surf.blit(glow_surf, (self.pos.x - radius * 2, self.pos.y - radius * 2), special_flags=pygame.BLEND_ADD)


# --- ENTITIES ---
class Player:
    def __init__(self):
        self.pos = Vector2(WIDTH / 2, HEIGHT / 2)
        self.vel = Vector2(0, 0)
        self.angle = 0
        self.cooldown = 0
        self.lives = 3  # V2: 3 Lives
        self.invulnerable = 0

    def update(self):
        keys = pygame.key.get_pressed()
        acc = Vector2(0, 0)
        speed = 0.5
        if keys[pygame.K_w]: acc.y -= speed
        if keys[pygame.K_s]: acc.y += speed
        if keys[pygame.K_a]: acc.x -= speed
        if keys[pygame.K_d]: acc.x += speed

        self.vel = (self.vel + acc) * 0.95  # Friction
        self.pos = self.pos + self.vel

        # Screen wrap
        if self.pos.x < 0: self.pos.x = WIDTH
        if self.pos.x > WIDTH: self.pos.x = 0
        if self.pos.y < 0: self.pos.y = HEIGHT
        if self.pos.y > HEIGHT: self.pos.y = 0

        # Mouse Aim
        mx, my = pygame.mouse.get_pos()
        self.angle = math.atan2(my - self.pos.y, mx - self.pos.x)
        self.cooldown = max(0, self.cooldown - 1)
        self.invulnerable = max(0, self.invulnerable - 1)

    def draw(self, surf):
        if self.invulnerable > 0 and (self.invulnerable // 4) % 2 == 0:
            return  # Blink when hit

        # Ship geometry
        tip = Vector2(math.cos(self.angle) * 20, math.sin(self.angle) * 20)
        left = Vector2(math.cos(self.angle + 2.5) * 15, math.sin(self.angle + 2.5) * 15)
        right = Vector2(math.cos(self.angle - 2.5) * 15, math.sin(self.angle - 2.5) * 15)

        p1 = (self.pos + tip).astuple()
        p2 = (self.pos + left).astuple()
        p3 = (self.pos + right).astuple()

        pygame.draw.polygon(surf, NEON_CYAN, [p1, p2, p3], 2)
        # Engine trails
        if random.random() < 0.5:
            game.particles.append(Particle(p2[0], p2[1], NEON_CYAN, 20, 1))
            game.particles.append(Particle(p3[0], p3[1], NEON_CYAN, 20, 1))


class Bullet:
    def __init__(self, x, y, angle):
        self.pos = Vector2(x, y)
        self.vel = Vector2(math.cos(angle) * 15, math.sin(angle) * 15)
        self.life = 60

    def update(self):
        self.pos = self.pos + self.vel
        self.life -= 1
        # Trail
        game.particles.append(Particle(self.pos.x, self.pos.y, NEON_WHITE, 10, 0.5))
        return self.life > 0

    def draw(self, surf):
        pygame.draw.circle(surf, NEON_WHITE, self.pos.astuple(), 3)


class Enemy:
    def __init__(self):
        side = random.randint(0, 3)
        if side == 0:
            self.pos = Vector2(random.randint(0, WIDTH), -50)
        elif side == 1:
            self.pos = Vector2(random.randint(0, WIDTH), HEIGHT + 50)
        elif side == 2:
            self.pos = Vector2(-50, random.randint(0, HEIGHT))
        else:
            self.pos = Vector2(WIDTH + 50, random.randint(0, HEIGHT))

        self.vel = Vector2(0, 0)
        self.color = NEON_MAGENTA
        self.type = random.choice(['CHASER', 'DASHER'])
        self.speed_mult = random.uniform(0.8, 1.2)

    def update(self, player_pos):
        diff = player_pos - self.pos
        dist = diff.length()
        if dist == 0: dist = 1

        if self.type == 'CHASER':
            acc = diff.normalize() * 0.2 * self.speed_mult
            self.vel = (self.vel + acc) * 0.96
        elif self.type == 'DASHER':
            if dist > 200:
                acc = diff.normalize() * 0.5 * self.speed_mult
                self.vel = (self.vel + acc) * 0.90
            else:
                self.vel = self.vel * 1.05  # Lunge

        self.pos = self.pos + self.vel

    def draw(self, surf):
        rect = pygame.Rect(self.pos.x - 10, self.pos.y - 10, 20, 20)
        pygame.draw.rect(surf, self.color, rect, 2)
        # Trail
        if random.random() < 0.3:
            game.particles.append(Particle(self.pos.x, self.pos.y, self.color, 15, 1))


# --- CONFIGURATION (UPDATED) ---
TIME_SCALE = 1.0


# --- ABILITIES ---
class GravityBomb:
    def __init__(self, x, y):
        self.pos = Vector2(x, y)
        self.life = 120  # 2 seconds
        self.radius = 0
        self.active = True

    def update(self, enemies):
        self.life -= 1
        self.radius = approach(self.radius, 200, 5)  # Grow grav field

        # SUCK ENEMIES
        for e in enemies:
            diff = self.pos - e.pos
            dist = diff.length()
            if dist < self.radius + 50:
                pull = diff.normalize() * 2  # Strong pull
                e.pos = e.pos + pull

        if self.life <= 0:
            self.explode(enemies)
            return False
        return True

    def explode(self, enemies):
        game.shake += 50
        # Destroy enemies in range
        for e in enemies[:]:
            if (self.pos - e.pos).length() < 250:
                enemies.remove(e)
                game.score += 200
                for _ in range(10):
                    game.particles.append(Particle(e.pos.x, e.pos.y, NEON_MAGENTA, 40, 4))

        # Visuals
        for _ in range(100):
            game.particles.append(Particle(self.pos.x, self.pos.y, NEON_CYAN, 80, 10))

    def draw(self, surf):
        # Black Hole Core
        pygame.draw.circle(surf, (0, 0, 0), self.pos.astuple(), 10)
        pygame.draw.circle(surf, NEON_MAGENTA, self.pos.astuple(), 12, 2)

        # Event Horizon
        if self.life % 10 < 5:
            pygame.draw.circle(surf, NEON_CYAN, self.pos.astuple(), int(self.radius), 1)


class Pickup:
    def __init__(self, x, y):
        self.pos = Vector2(x, y)
        self.vel = Vector2(random.uniform(-1, 1), random.uniform(-1, 1))
        self.life = 600  # 10 seconds

    def update(self, player_pos):
        # Magnetic Pull
        diff = player_pos - self.pos
        dist = diff.length()
        if dist < 150:
            self.vel = self.vel + diff.normalize() * 0.5

        self.pos = self.pos + self.vel
        self.vel = self.vel * 0.95
        self.life -= 1
        return self.life > 0

    def draw(self, surf):
        pygame.draw.circle(surf, NEON_LIME, self.pos.astuple(), 3)
        # Glow
        if random.random() < 0.2:
            pygame.draw.circle(surf, NEON_WHITE, self.pos.astuple(), 5, 1)


# --- GAME ENGINE ---
class Game:
    def __init__(self):
        self.reset_game()
        self.bloom_surf = pygame.Surface((WIDTH, HEIGHT))

    def reset_game(self):
        self.player = Player()
        self.bullets = []
        self.enemies = []
        self.particles = []
        self.bombs = []
        self.pickups = []  # V4: Pickups
        self.score = 0
        self.shake = 0
        self.spawn_timer = 0
        self.game_over = False
        self.bomb_ammo = 1  # Start with 1, earn more
        self.bomb_charge = 0  # 0 to 100
        self.hyper_timer = 0  # V5: Hyper Mode
        self.time_scale = 1.0

    def run(self):
        running = True
        while running:
            # 1. EVENTS
            for event in pygame.event.get():
                if event.type == pygame.QUIT: running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE: running = False
                    if event.key == pygame.K_r and self.game_over: self.reset_game()
                    if event.key == pygame.K_SPACE and not self.game_over and self.bomb_ammo > 0:
                        self.bombs.append(GravityBomb(self.player.pos.x, self.player.pos.y))
                        self.bomb_ammo -= 1
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.player.cooldown = 0

            if not self.game_over:
                # TIME DILATION LOGIC
                target_ts = 1.0
                for b in self.bombs:
                    if b.life < 10: target_ts = 0.1
                self.time_scale = approach(self.time_scale, target_ts, 0.05)

                if pygame.mouse.get_pressed()[0] and self.player.cooldown == 0:
                    # SPLIT SHOT
                    if self.hyper_timer > 0:
                        self.bullets.append(Bullet(self.player.pos.x, self.player.pos.y, self.player.angle))
                        self.bullets.append(Bullet(self.player.pos.x, self.player.pos.y, self.player.angle + 0.2))
                        self.bullets.append(Bullet(self.player.pos.x, self.player.pos.y, self.player.angle - 0.2))
                        self.player.cooldown = 4
                    else:
                        self.bullets.append(Bullet(self.player.pos.x, self.player.pos.y, self.player.angle))
                        self.player.cooldown = 5
                    self.shake += 2

                # 2. UPDATE (Scaled by Time)
                if self.time_scale < 1.0 and random.random() > self.time_scale:
                    pass
                else:
                    self.player.update()

                    # Hyper Decay
                    if self.hyper_timer > 0:
                        self.hyper_timer -= 1
                        self.player.cooldown = max(0, self.player.cooldown - 2)  # RAPID FIRE
                        if self.hyper_timer % 10 == 0:
                            game.particles.append(Particle(self.player.pos.x, self.player.pos.y, NEON_WHITE, 20, 2))

                    self.spawn_timer += 1
                    if self.spawn_timer > max(20, 60 - self.score / 100):
                        self.enemies.append(Enemy())
                        self.spawn_timer = 0

                    for b in self.bullets[:]:
                        if not b.update(): self.bullets.remove(b)

                    for e in self.enemies[:]:
                        e.update(self.player.pos)
                        # Collision with Player
                        is_hit = (e.pos - self.player.pos).length() < 25
                        if is_hit and self.player.invulnerable == 0 and self.hyper_timer == 0:
                            self.shake += 50
                            self.player.lives -= 1
                            self.player.invulnerable = 120
                            for _ in range(50): self.particles.append(
                                Particle(self.player.pos.x, self.player.pos.y, NEON_CYAN, 60, 5))
                            self.enemies.remove(e)
                            if self.player.lives <= 0:
                                self.game_over = True
                                for _ in range(100): self.particles.append(
                                    Particle(self.player.pos.x, self.player.pos.y, NEON_WHITE, 100, 8))
                        elif is_hit and self.hyper_timer > 0:
                            # RAMMING SPEED
                            self.enemies.remove(e)
                            self.score += 500
                            self.shake += 10
                            for _ in range(20): self.particles.append(Particle(e.pos.x, e.pos.y, NEON_ORANGE, 40, 5))

                    # Bombs
                    for b in self.bombs[:]:
                        if not b.update(self.enemies): self.bombs.remove(b)

                    # Pickups
                    for p in self.pickups[:]:
                        if not p.update(self.player.pos):
                            self.pickups.remove(p)
                        # Collect
                        elif (p.pos - self.player.pos).length() < 30:
                            self.pickups.remove(p)
                            self.score += 10
                            if self.hyper_timer == 0: self.bomb_charge += 5

                            if self.bomb_charge >= 100:
                                self.bomb_charge = 0
                                self.hyper_timer = 300  # 5 Seconds of HYPER FLUX
                                self.bomb_ammo += 1
                                game.shake += 20
                                for _ in range(50): game.particles.append(
                                    Particle(self.player.pos.x, self.player.pos.y, NEON_LIME, 60, 5))

                    for b in self.bullets[:]:
                        hit = False
                        for e in self.enemies[:]:
                            if (b.pos - e.pos).length() < 20:
                                self.enemies.remove(e);
                                hit = True;
                                self.score += 100;
                                self.shake += 5
                                for _ in range(10): self.particles.append(
                                    Particle(e.pos.x, e.pos.y, NEON_MAGENTA, 30, 3))
                                for _ in range(random.randint(1, 3)): self.pickups.append(Pickup(e.pos.x, e.pos.y))
                                break
                        if hit: self.bullets.remove(b)

            for p in self.particles[:]:
                if not p.update(): self.particles.remove(p)

            game.shake = max(0, game.shake * 0.9)

            # 3. DRAW
            screen.fill((10, 10, 15))
            offset_x = random.uniform(-self.shake, self.shake)
            offset_y = random.uniform(-self.shake, self.shake)
            view_surf = pygame.Surface((WIDTH, HEIGHT));
            view_surf.fill((10, 10, 15))

            # Draw Grid
            spacing = 50
            for x in range(0, WIDTH, spacing): pygame.draw.line(view_surf, (20, 20, 40), (x, 0), (x, HEIGHT))
            for y in range(0, HEIGHT, spacing): pygame.draw.line(view_surf, (20, 20, 40), (0, y), (WIDTH, y))

            if not self.game_over:
                # Hyper Draw
                if self.hyper_timer > 0:
                    pygame.draw.circle(view_surf, NEON_WHITE, self.player.pos.astuple(),
                                       30 + math.sin(self.hyper_timer * 0.5) * 5, 2)
                self.player.draw(view_surf)

            for b in self.bombs: b.draw(view_surf)
            for p in self.pickups: p.draw(view_surf)
            for e in self.enemies: e.draw(view_surf)
            for b in self.bullets: b.draw(view_surf)
            for p in self.particles: p.draw(view_surf)

            screen.blit(view_surf, (offset_x, offset_y))

            # UI
            font = pygame.font.SysFont("monospace", 30)
            screen.blit(font.render(f"SCORE: {self.score}", True, NEON_WHITE), (20, 20))
            screen.blit(font.render(f"LIVES: {self.player.lives}", True, NEON_CYAN), (20, 60))

            # Bomb Bar
            bar_width = 200
            pygame.draw.rect(screen, (50, 50, 50), (20, 110, bar_width, 20))
            if self.hyper_timer > 0:
                fill = (self.hyper_timer / 300) * bar_width
                pygame.draw.rect(screen, NEON_WHITE, (20, 110, fill, 20))
                screen.blit(font.render(f"HYPER FLUX!", True, NEON_WHITE), (230, 105))
            else:
                fill = (self.bomb_charge / 100) * bar_width
                pygame.draw.rect(screen, NEON_LIME, (20, 110, fill, 20))
                screen.blit(font.render(f"SINGULARITY: {self.bomb_ammo}", True, NEON_LIME), (230, 105))
            pygame.draw.rect(screen, NEON_WHITE, (20, 110, bar_width, 20), 2)

            if self.game_over:
                over_font = pygame.font.SysFont("monospace", 80)
                tr = over_font.render("GAME OVER", True, NEON_ORANGE).get_rect(center=(WIDTH / 2, HEIGHT / 2))
                screen.blit(over_font.render("GAME OVER", True, NEON_ORANGE), tr)
                screen.blit(font.render("PRESS 'R' TO RESTART", True, NEON_WHITE), (WIDTH / 2 - 140, HEIGHT / 2 + 60))

            pygame.display.flip()
            clock.tick(FPS)

        pygame.quit()


game = Game()
game.run()
