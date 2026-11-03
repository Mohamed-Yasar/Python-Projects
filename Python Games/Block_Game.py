import pygame
import random
import sys
import os
import math
import wave
import struct


# --- MUSIC GENERATION LOGIC ---
# This runs first to ensure the asset exists!

def generate_music_if_missing():
    if os.path.exists("background_music.wav"):
        return

    print("Generating soundtrack... (This runs only once)")

    SAMPLE_RATE = 44100
    BPM = 120
    BEAT_DURATION = 60 / BPM  # 0.5 seconds
    BAR_DURATION = BEAT_DURATION * 4
    LOOP_BARS = 4

    def sine_wave(freq, duration, volume=1.0):
        n_samples = int(SAMPLE_RATE * duration)
        return [volume * math.sin(2 * math.pi * freq * i / SAMPLE_RATE) for i in range(n_samples)]

    def kick(duration=0.5):
        n_samples = int(SAMPLE_RATE * duration)
        data = []
        for i in range(n_samples):
            t = i / SAMPLE_RATE
            freq = 150 * math.exp(-15 * t)
            amp = math.exp(-5 * t)
            val = amp * math.sin(2 * math.pi * freq * t)
            if val > 0.8: val = 0.8  # Clip
            if val < -0.8: val = -0.8
            data.append(val)
        return data

    def snare(duration=0.25):
        n_samples = int(SAMPLE_RATE * duration)
        data = []
        for i in range(n_samples):
            t = i / SAMPLE_RATE
            n = (random.random() * 2 - 1) * math.exp(-15 * t)
            tone = math.sin(2 * math.pi * 200 * t) * math.exp(-10 * t) * 0.5
            data.append((n + tone) * 0.7)
        return data

    def mix(buffer1, buffer2):
        max_len = max(len(buffer1), len(buffer2))
        out = [0.0] * max_len
        for i in range(max_len):
            v1 = buffer1[i] if i < len(buffer1) else 0
            v2 = buffer2[i] if i < len(buffer2) else 0
            val = v1 + v2
            if val > 1.0: val = 1.0
            if val < -1.0: val = -1.0
            out[i] = val
        return out

    def sequence_to_audio(sequence, beat_len):
        total_len = int(SAMPLE_RATE * BAR_DURATION * LOOP_BARS)
        master_track = [0.0] * total_len

        for bar in range(LOOP_BARS):
            offset_samples = int(bar * BAR_DURATION * SAMPLE_RATE)
            for beat, sound in sequence:
                wave_data = sound()
                start_idx = offset_samples + int(beat * beat_len * SAMPLE_RATE)
                for i, val in enumerate(wave_data):
                    if start_idx + i < total_len:
                        master_track[start_idx + i] += val

        # Normalize
        max_val = max(abs(x) for x in master_track) if master_track else 1
        return [x / max_val * 0.8 for x in master_track]

    # 1. DRUMS
    drums = []
    for i in range(4):
        drums.append((i, kick))
        if i % 2 == 1:
            drums.append((i, snare))

    # 2. BASS (Off-beat sawtooth)
    bass_freqs = [55, 55, 65.41, 49]  # A1 ...
    bass_track = [0.0] * int(SAMPLE_RATE * BAR_DURATION * LOOP_BARS)

    for bar in range(LOOP_BARS):
        note = bass_freqs[bar % len(bass_freqs)]
        for beat in range(4):
            start_sample = int((bar * BAR_DURATION + beat * BEAT_DURATION + BEAT_DURATION / 2) * SAMPLE_RATE)
            dur = BEAT_DURATION * 0.4
            for i in range(int(SAMPLE_RATE * dur)):
                t = i / SAMPLE_RATE
                val = 0.6 * (math.sin(2 * math.pi * note * t) + 0.5 * math.sin(2 * math.pi * note * 2 * t))
                val *= math.exp(-2 * t)
                if start_sample + i < len(bass_track):
                    bass_track[start_sample + i] += val

    # 3. LEAD (Pentatonic Arpeggio)
    scale = [523.25, 622.25, 698.46, 783.99, 932.33]
    lead_track = [0.0] * int(SAMPLE_RATE * BAR_DURATION * LOOP_BARS)
    random.seed(42)
    for bar in range(LOOP_BARS):
        for sixteenth in range(16):
            if random.random() > 0.4:
                note = random.choice(scale)
                if sixteenth % 4 == 0: note *= 0.5
                start_sample = int((bar * BAR_DURATION + sixteenth * (BEAT_DURATION / 4)) * SAMPLE_RATE)
                dur = BEAT_DURATION / 4 * 0.8
                for i in range(int(SAMPLE_RATE * dur)):
                    t = i / SAMPLE_RATE
                    val = 0.15 * (1 if math.sin(2 * math.pi * note * t) > 0 else -1)
                    if start_sample + i < len(lead_track):
                        lead_track[start_sample + i] += val

    # MIX
    drum_samples_float = sequence_to_audio(drums, BEAT_DURATION)
    final_mix = mix(drum_samples_float, mix(bass_track, lead_track))

    # SAVE
    data = [int(x * 32767) for x in final_mix]
    with wave.open("background_music.wav", 'w') as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(SAMPLE_RATE)
        f.writeframes(struct.pack('<' + ('h' * len(data)), *data))

    print("Soundtrack ready.")


# --- GAME LOGIC ---

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Ensure music exists before trying to load it
try:
    generate_music_if_missing()
except Exception as e:
    print(f"Warning: Could not fallback generate music: {e}")

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Colors
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
NEON_GREEN = (57, 255, 20)
NEON_PINK = (255, 20, 147)
NEON_CYAN = (0, 255, 255)
RED = (255, 0, 0)
BLACK = (10, 10, 20)
YELLOW = (255, 255, 0)

# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Dodge the Blocks! (DELUXE SINGLE FILE)")

# Clock
clock = pygame.time.Clock()

# Load Music
if os.path.exists("background_music.wav"):
    try:
        pygame.mixer.music.load("background_music.wav")
        pygame.mixer.music.play(-1)
        pygame.mixer.music.set_volume(0.6)
    except Exception:
        pass


# --- VISUAL JUICE CLASSES ---

class Particle:
    def __init__(self, x, y, color, speed_x, speed_y, life):
        self.x = x
        self.y = y
        self.color = color
        self.speed_x = speed_x
        self.speed_y = speed_y
        self.life = life
        self.max_life = life
        self.size = random.randint(2, 5)

    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y
        self.life -= 1
        self.size = max(0, self.size - 0.1)

    def draw(self, surface):
        if self.life > 0:
            alpha = int((self.life / self.max_life) * 255)
            s = pygame.Surface((int(self.size * 2), int(self.size * 2)), pygame.SRCALPHA)
            pygame.draw.circle(s, (*self.color, alpha), (int(self.size), int(self.size)), int(self.size))
            surface.blit(s, (self.x, self.y))


class Star:
    def __init__(self):
        self.x = random.randint(0, SCREEN_WIDTH)
        self.y = random.randint(0, SCREEN_HEIGHT)
        self.speed = random.random() * 2 + 0.5
        self.size = random.random() * 2

    def update(self):
        self.y += self.speed
        if self.y > SCREEN_HEIGHT:
            self.y = 0
            self.x = random.randint(0, SCREEN_WIDTH)

    def draw(self, surface):
        pygame.draw.circle(surface, (100, 100, 150), (int(self.x), int(self.y)), int(self.size))


# --- GAME OBJECTS ---

player_size = 40
player_pos = [SCREEN_WIDTH // 2, SCREEN_HEIGHT - 2 * player_size]
player_speed = 10
player_shielded = False
shield_timer = 0
shield_angle = 0

particles = []
stars = [Star() for _ in range(50)]

enemy_size = 40
enemy_list = []
enemy_speed = 6

powerups = []  # List of [x, y, type]

score = 0
font = pygame.font.SysFont("monospace", 35)
big_font = pygame.font.SysFont("monospace", 70, bold=True)

camera_shake = 0


def create_explosion(x, y, color, count=20):
    for _ in range(count):
        sx = (random.random() - 0.5) * 10
        sy = (random.random() - 0.5) * 10
        particles.append(Particle(x, y, color, sx, sy, random.randint(20, 40)))


def drop_enemies(enemy_list):
    delay = random.random()
    rate = 0.05 + (score * 0.001)
    if len(enemy_list) < 15 and delay < rate:
        x_pos = random.randint(0, SCREEN_WIDTH - enemy_size)
        enemy_list.append([x_pos, 0])


def drop_powerup():
    if random.random() < 0.005:
        x = random.randint(50, SCREEN_WIDTH - 50)
        powerups.append([x, -30, "shield"])


def update_game_state():
    global score, enemy_speed, player_shielded, shield_timer, camera_shake

    for star in stars:
        star.update()

    for p in particles:
        p.update()
    particles[:] = [p for p in particles if p.life > 0]

    if player_shielded:
        shield_timer -= 1
        if shield_timer <= 0:
            player_shielded = False

    if camera_shake > 0:
        camera_shake -= 1

    for idx, enemy_pos in enumerate(enemy_list):
        if enemy_pos[1] >= 0 and enemy_pos[1] < SCREEN_HEIGHT:
            enemy_pos[1] += enemy_speed
        else:
            enemy_list.pop(idx)
            score += 1

    for idx, p in enumerate(powerups):
        p[1] += 4
        if p[1] > SCREEN_HEIGHT:
            powerups.pop(idx)

    base_speed = 6
    if score > 20: base_speed = 8
    if score > 50: base_speed = 12
    if score > 100: base_speed = 15
    enemy_speed = base_speed


def check_collisions(player_rect):
    global game_over, score, player_shielded, shield_timer, camera_shake

    p_rect = pygame.Rect(player_pos[0], player_pos[1], player_size, player_size)

    for enemy in enemy_list[:]:
        e_rect = pygame.Rect(enemy[0], enemy[1], enemy_size, enemy_size)
        if p_rect.colliderect(e_rect):
            if player_shielded:
                enemy_list.remove(enemy)
                create_explosion(enemy[0], enemy[1], RED, 30)
                score += 5
                camera_shake = 10
            else:
                game_over = True
                create_explosion(player_pos[0], player_pos[1], NEON_CYAN, 100)

    for p in powerups[:]:
        pu_rect = pygame.Rect(p[0], p[1], 30, 30)
        if p_rect.colliderect(pu_rect):
            powerups.remove(p)
            if p[2] == "shield":
                player_shielded = True
                shield_timer = 300
                score += 10
                create_explosion(player_pos[0], player_pos[1], NEON_GREEN, 50)


# Game Loop
game_over = False
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if game_over and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                game_over = False
                score = 0
                enemy_list = []
                powerups = []
                player_pos = [SCREEN_WIDTH // 2, SCREEN_HEIGHT - 2 * player_size]
                player_shielded = False

    if not game_over:
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player_pos[0] > 0:
            player_pos[0] -= player_speed
            if random.random() < 0.5:
                particles.append(Particle(player_pos[0] + player_size / 2, player_pos[1] + player_size, NEON_CYAN,
                                          (random.random() - 0.5) * 2, 2, 10))

        if keys[pygame.K_RIGHT] and player_pos[0] < SCREEN_WIDTH - player_size:
            player_pos[0] += player_speed
            if random.random() < 0.5:
                particles.append(Particle(player_pos[0] + player_size / 2, player_pos[1] + player_size, NEON_CYAN,
                                          (random.random() - 0.5) * 2, 2, 10))

        drop_enemies(enemy_list)
        drop_powerup()
        update_game_state()
        check_collisions(None)

    screen.fill(BLACK)

    ox = 0
    oy = 0
    if camera_shake > 0:
        ox = random.randint(-5, 5)
        oy = random.randint(-5, 5)

    for star in stars:
        star.draw(screen)

    for p in particles:
        p.draw(screen)

    for p in powerups:
        color = NEON_GREEN if p[2] == "shield" else YELLOW
        pygame.draw.circle(screen, color, (int(p[0] + ox), int(p[1] + oy)), 15)
        pygame.draw.circle(screen, WHITE, (int(p[0] + ox), int(p[1] + oy)), 10)

    for enemy in enemy_list:
        s = pygame.Surface((enemy_size + 10, enemy_size + 10), pygame.SRCALPHA)
        pygame.draw.rect(s, (255, 0, 0, 100), (0, 0, enemy_size + 10, enemy_size + 10))
        screen.blit(s, (enemy[0] - 5 + ox, enemy[1] - 5 + oy))

        pygame.draw.rect(screen, RED, (enemy[0] + ox, enemy[1] + oy, enemy_size, enemy_size))
        pygame.draw.rect(screen, (100, 0, 0), (enemy[0] + ox, enemy[1] + oy, enemy_size, enemy_size), 3)

    if not game_over:
        pygame.draw.rect(screen, NEON_CYAN, (player_pos[0] + ox, player_pos[1] + oy, player_size, player_size))
        pygame.draw.rect(screen, WHITE, (player_pos[0] + ox, player_pos[1] + oy, player_size, player_size), 2)

        if player_shielded:
            shield_angle += 5
            rad = 50
            sx = player_pos[0] + player_size / 2 + math.cos(math.radians(shield_angle)) * rad
            sy = player_pos[1] + player_size / 2 + math.sin(math.radians(shield_angle)) * rad
            pygame.draw.circle(screen, NEON_GREEN, (int(sx + ox), int(sy + oy)), 10)
            pygame.draw.circle(screen, NEON_GREEN,
                               (int(player_pos[0] + player_size / 2 + ox), int(player_pos[1] + player_size / 2 + oy)),
                               60, 2)

    score_col = WHITE
    if player_shielded: score_col = NEON_GREEN
    text = font.render(f"Score: {score}", True, score_col)
    screen.blit(text, (SCREEN_WIDTH - 250, 20))

    if game_over:
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))

        go_text = big_font.render("GAME OVER", True, RED)
        screen.blit(go_text, (SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2 - 50))

        poid_text = font.render("Press SPACE to Restart", True, WHITE)
        screen.blit(poid_text, (SCREEN_WIDTH // 2 - 250, SCREEN_HEIGHT // 2 + 50))

    clock.tick(60)
    pygame.display.update()

pygame.quit()
sys.exit()
