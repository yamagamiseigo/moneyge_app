import pygame
import sys
import random
import math
import numpy as np

# 音声ミキサー初期化
pygame.mixer.init(frequency=44100, size=-16, channels=1)

# --- リアルタイム効果音生成 ---
def create_sfx(sfx_type, volume=0.4):
    sr = 44100
    if sfx_type == "launch":
        dur = 0.5
        n = int(sr * dur)
        t = np.linspace(0, dur, n)
        freq = np.linspace(300, 150, n)
        wave = np.sin(2 * np.pi * freq * t) * np.exp(-4 * t) * volume
        return pygame.mixer.Sound(buffer=(wave * 32767).astype(np.int16))
    elif sfx_type == "boost":
        dur = 0.2
        n = int(sr * dur)
        t = np.linspace(0, dur, n)
        noise = np.random.uniform(-1, 1, n)
        wave = noise * np.exp(-8 * t) * volume
        return pygame.mixer.Sound(buffer=(wave * 32767).astype(np.int16))
    elif sfx_type == "coin":
        dur = 0.25
        n = int(sr * dur)
        t = np.linspace(0, dur, n)
        wave = np.sin(2 * np.pi * 1200 * t) * np.exp(-5 * t) * volume
        return pygame.mixer.Sound(buffer=(wave * 32767).astype(np.int16))
    elif sfx_type == "upgrade":
        dur = 0.3
        n = int(sr * dur)
        t = np.linspace(0, dur, n)
        freqs = np.linspace(400, 880, n)
        wave = np.sin(2 * np.pi * freqs * t) * np.exp(-3 * t) * volume
        return pygame.mixer.Sound(buffer=(wave * 32767).astype(np.int16))

sfx_launch = create_sfx("launch", 0.4)
sfx_boost = create_sfx("boost", 0.3)
sfx_coin = create_sfx("coin", 0.4)
sfx_up = create_sfx("upgrade", 0.5)

# 初期化 (スマホ縦持ちサイズ)
pygame.init()
WIDTH, HEIGHT = 450, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Sky Hopper - Flight Idle")
clock = pygame.time.Clock()

font_s = pygame.font.Font(None, 20)
font_m = pygame.font.Font(None, 26)
font_l = pygame.font.Font(None, 36)

# ゲーム状態: "SHOP", "POWER_BAR", "FLYING", "RESULT"
game_state = "SHOP"

# プレイヤー資産・ステータス
coins = 100
total_distance = 0

# アップグレードレベル
lv_motor = 1     # 初期速度・ブースト力
lv_wing = 1      # 揚力（落ちにくさ）
lv_fuel = 1      # ブースト回数

# 費用
cost_motor = 50
cost_wing = 50
cost_fuel = 60

# フライト中の変数
distance_traveled = 0  # 飛行した総距離（ワールド座標）
plane_y = 600
plane_vx = 0
plane_vy = 0
fuel_left = 0
power_meter = 0
power_dir = 1

# 雲の生成（ワールド座標で管理）
clouds = [{"x": random.randint(50, WIDTH * 4), "y": random.randint(50, 450), "size": random.randint(20, 35)} for _ in range(20)]

def start_launch_sequence():
    global game_state, power_meter
    game_state = "POWER_BAR"
    power_meter = 0

# メインループ
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos

            if game_state == "SHOP":
                if 40 <= mx <= WIDTH - 40 and 420 <= my <= 480:
                    if coins >= cost_motor:
                        coins -= cost_motor
                        lv_motor += 1
                        cost_motor = int(cost_motor * 1.5)
                        sfx_up.play()
                elif 40 <= mx <= WIDTH - 40 and 500 <= my <= 560:
                    if coins >= cost_wing:
                        coins -= cost_wing
                        lv_wing += 1
                        cost_wing = int(cost_wing * 1.5)
                        sfx_up.play()
                elif 40 <= mx <= WIDTH - 40 and 580 <= my <= 640:
                    if coins >= cost_fuel:
                        coins -= cost_fuel
                        lv_fuel += 1
                        cost_fuel = int(cost_fuel * 1.5)
                        sfx_up.play()
                elif 40 <= mx <= WIDTH - 40 and 680 <= my <= 750:
                    start_launch_sequence()

            elif game_state == "POWER_BAR":
                distance_traveled = 0
                plane_y = 620
                launch_power = (power_meter / 100.0) * (5 + lv_motor * 1.5)
                plane_vx = 6 + launch_power
                plane_vy = -8 - launch_power * 0.8
                fuel_left = 2 + lv_fuel
                sfx_launch.play()
                game_state = "FLYING"

            elif game_state == "FLYING":
                if fuel_left > 0:
                    plane_vy -= 4.5 + (lv_motor * 0.3)
                    plane_vx += 1.5
                    fuel_left -= 1
                    sfx_boost.play()

            elif game_state == "RESULT":
                game_state = "SHOP"

    # --- 状態ごとの更新処理 ---
    if game_state == "POWER_BAR":
        power_meter += power_dir * 3
        if power_meter >= 100 or power_meter <= 0:
            power_dir *= -1

    elif game_state == "FLYING":
        gravity = 0.35 - (lv_wing * 0.02)
        lift = (plane_vx * 0.03) * (0.8 + lv_wing * 0.1)
        
        plane_vy += gravity - lift
        plane_vx = max(2.0, plane_vx - 0.02)

        # 距離を進める
        distance_traveled += plane_vx
        plane_y += plane_vy

        # 画面外（地面）に落ちたらゲームオーバー
        if plane_y >= 640:
            plane_y = 640
            earned_coins = int(distance_traveled / 10)
            coins += earned_coins
            total_distance = max(total_distance, int(distance_traveled))
            for _ in range(3):
                sfx_coin.play()
            game_state = "RESULT"

    # --- 描画処理 ---
    screen.fill((135, 206, 235))
    
    # 背景の空と地平線
    pygame.draw.rect(screen, (240, 200, 150), (0, 400, WIDTH, 400))
    pygame.draw.rect(screen, (60, 140, 60), (0, 650, WIDTH, 150))
    pygame.draw.line(screen, (40, 100, 40), (0, 650), (WIDTH, 650), 6)

    # 雲の描画（カメラ追従：飛行機が進むと雲が左へ流れる）
    for c in clouds:
        # 飛行機の現在位置を基準に画面上の座標を計算
        screen_cx = c["x"] - distance_traveled
        if screen_cx < -100:
            # 画面左端を通り過ぎたら右側の遠くへリサイクル
            c["x"] = distance_traveled + WIDTH + random.randint(100, 300)
            c["y"] = random.randint(50, 450)
            screen_cx = c["x"] - distance_traveled

        if -50 <= screen_cx <= WIDTH + 50:
            pygame.draw.circle(screen, (255, 255, 255), (int(screen_cx), int(c["y"])), c["size"])
            pygame.draw.circle(screen, (255, 255, 255), (int(screen_cx) + 15, int(c["y"]) - 10), c["size"] - 8)

    # 飛行機の描画（常に画面左寄りの X = 100 に固定！絶対に画面外に行きません）
    if game_state in ["FLYING", "RESULT"]:
        screen_plane_x = 100
        angle = math.atan2(plane_vy, plane_vx) * 180 / math.pi
        
        pygame.draw.polygon(screen, (240, 240, 245), [
            (screen_plane_x + 20, plane_y),
            (screen_plane_x - 15, plane_y - 8),
            (screen_plane_x - 10, plane_y + 8)
        ])
        pygame.draw.line(screen, (200, 50, 50), (screen_plane_x, plane_y), (screen_plane_x - 5, plane_y - 15), 4)

    # --- UI 描画 ---
    if game_state == "SHOP":
        pygame.draw.rect(screen, (30, 40, 60), (0, 0, WIDTH, HEIGHT))
        
        title = font_l.render("SKY HOPPER", True, (255, 255, 255))
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 50))

        txt_coins = font_m.render(f"COINS: {coins} G", True, (255, 222, 100))
        txt_best = font_s.render(f"SAIKOU KIKUROKU: {int(total_distance)} m", True, (200, 220, 250))
        screen.blit(txt_coins, (35, 110))
        screen.blit(txt_best, (35, 145))

        panel_y = 200
        pygame.draw.rect(screen, (45, 60, 85), (30, panel_y, WIDTH - 60, 190), border_radius=12)
        screen.blit(font_m.render("[ KITAI SUPECKU ]", True, (255, 200, 100)), (50, panel_y + 15))
        screen.blit(font_s.render(f"* MOUTA LV.{lv_motor} (BUSHUUTORYOKU)", True, (255, 255, 255)), (50, panel_y + 55))
        screen.blit(font_s.render(f"* WING LV.{lv_wing} (YOUCHOKU)", True, (255, 255, 255)), (50, panel_y + 90))
        screen.blit(font_s.render(f"* TANK LV.{lv_fuel} (NENRYOU)", True, (255, 255, 255)), (50, panel_y + 125))

        def draw_btn(y, text, cost):
            pygame.draw.rect(screen, (70, 130, 180), (40, y, WIDTH - 80, 50), border_radius=10)
            txt = font_m.render(f"{text} ({cost}G)", True, (255, 255, 255))
            screen.blit(txt, (WIDTH // 2 - txt.get_width() // 2, y + 14))

        draw_btn(420, "MOUTA WO KYOUKA", cost_motor)
        draw_btn(500, "WING WO KYOUKA", cost_wing)
        draw_btn(580, "TANK WO KYOUKA", cost_fuel)

        pygame.draw.rect(screen, (230, 100, 50), (40, 680, WIDTH - 80, 70), border_radius=15)
        txt_launch = font_l.render("HASSIN SURU!", True, (255, 255, 255))
        screen.blit(txt_launch, (WIDTH // 2 - txt_launch.get_width() // 2, 700))

    elif game_state == "POWER_BAR":
        pygame.draw.rect(screen, (20, 20, 30), (0, HEIGHT // 2 - 120, WIDTH, 240))
        txt_p = font_m.render("TAP DE PAWAA KETTEI!", True, (255, 255, 255))
        screen.blit(txt_p, (WIDTH // 2 - txt_p.get_width() // 2, HEIGHT // 2 - 80))

        pygame.draw.rect(screen, (60, 60, 80), (60, HEIGHT // 2 - 20, WIDTH - 120, 40), border_radius=10)
        fill_w = int((WIDTH - 120) * (power_meter / 100.0))
        pygame.draw.rect(screen, (255, 180, 50), (60, HEIGHT // 2 - 20, fill_w, 40), border_radius=10)

    elif game_state == "FLYING":
        txt_dist = font_l.render(f"{int(distance_traveled)} m", True, (255, 255, 255))
        txt_fuel = font_m.render(f"BOOST x {fuel_left}", True, (255, 220, 100))
        screen.blit(txt_dist, (35, 40))
        screen.blit(txt_fuel, (35, 85))
        
        if fuel_left > 0:
            txt_tap = font_s.render("TAP DE BUSHUUTO ACCEL!", True, (255, 255, 200))
            screen.blit(txt_tap, (WIDTH // 2 - txt_tap.get_width() // 2, 130))

    elif game_state == "RESULT":
        box_w, box_h = 360, 240
        box_surf = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
        pygame.draw.rect(box_surf, (20, 30, 50, 240), box_surf.get_rect(), border_radius=15)
        pygame.draw.rect(box_surf, (100, 180, 255), box_surf.get_rect(), 3, border_radius=10)
        
        bx = WIDTH // 2 - box_w // 2
        by = HEIGHT // 2 - box_h // 2
        screen.blit(box_surf, (bx, by))

        earned_coins = int(distance_traveled / 10)
        t1 = font_m.render("FLIGHT SYURRYOU!", True, (255, 220, 100))
        t2 = font_s.render(f"KYORI: {int(distance_traveled)} m", True, (255, 255, 255))
        t3 = font_s.render(f"GET COIN: +{earned_coins} G", True, (150, 255, 150))
        t4 = font_s.render("TAP DE SHOP E", True, (200, 200, 200))

        screen.blit(t1, (WIDTH // 2 - t1.get_width() // 2, by + 30))
        screen.blit(t2, (WIDTH // 2 - t2.get_width() // 2, by + 85))
        screen.blit(t3, (WIDTH // 2 - t3.get_width() // 2, by + 120))
        screen.blit(t4, (WIDTH // 2 - t4.get_width() // 2, by + 175))

    pygame.display.flip()
    clock.tick(60)
