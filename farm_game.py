import pygame
import sys
import random

# 初期化
pygame.init()
WIDTH, HEIGHT = 1000, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("リアル牧場・農園経営シミュレーション")
clock = pygame.time.Clock()

# フォント設定（日本語表示のためシステムフォントを使用）
def get_font(size):
    for name in ["meiryo", "hiragino sans", "ms gothic", "arial"]:
        try:
            return pygame.font.SysFont(name, size)
        except:
            continue
    return pygame.font.Font(None, size)

font_s = get_font(16)
font_m = get_font(20)
font_l = get_font(28)

# 色の定義
COLOR_BG = (34, 139, 34)      # 牧場の緑
COLOR_DIRT = (120, 80, 40)    # 耕された土
COLOR_DRY = (90, 60, 30)     # 乾いた土
COLOR_WATERED = (70, 45, 20)  # 水をあげた土
COLOR_UI_BG = (50, 50, 50)
COLOR_WHITE = (255, 255, 255)
COLOR_BLACK = (0, 0, 0)

# ゲーム状態
money = 1000
day = 1
time_counter = 0

# プレイヤー
player_x = 400
player_y = 300
player_speed = 4
player_tool = "hoe"  # 'hoe'(クワ), 'water'(じょうろ), 'seeds'(種まき), 'harvest'(収穫)
selected_crop_type = "carrot"

# 作物データ
CROP_TYPES = {
    "carrot": {"name": "ニンジン", "cost": 30, "price": 80, "growth_time": 300, "color": (255, 140, 0)},
    "wheat": {"name": "小麦", "cost": 50, "price": 130, "growth_time": 500, "color": (218, 165, 32)},
    "tomato": {"name": "トマト", "cost": 80, "price": 220, "growth_time": 700, "color": (220, 20, 60)},
}

# 畑のマス目データ (Grid)
GRID_COLS = 8
GRID_ROWS = 6
GRID_SIZE = 60
GRID_START_X = 50
GRID_START_Y = 150

# 畑の初期化 (state: 0=草地, 1=耕した土, 2=作物成長中, 3=収穫期, 4=枯れ)
farms = []
for r in range(GRID_ROWS):
    for c in range(GRID_COLS):
        farms.append({
            "col": c, "row": r,
            "x": GRID_START_X + c * GRID_SIZE,
            "y": GRID_START_Y + r * GRID_SIZE,
            "state": 0,  # 0:通常, 1:耕作地(水なし), 2:耕作地(水あり), 3:成長中, 4:収穫可能
            "crop": None,
            "growth": 0,
            "max_growth": 100,
            "watered": False
        })

# 動物データ
animals = [
    {"type": "chicken", "name": "ニワトリ1号", "x": 650, "y": 200, "product": "たまご", "timer": 0, "ready": False},
    {"type": "chicken", "name": "ニワトリ2号", "x": 750, "y": 250, "product": "たまご", "timer": 0, "ready": False},
    {"type": "cow", "name": "ウシ1号", "x": 680, "y": 420, "product": "ミルク", "timer": 0, "ready": False},
]

# インベントリ（収穫した作物や畜産物）
inventory = {
    "carrot": 0, "wheat": 0, "tomato": 0,
    "egg": 0, "milk": 0
}

# メインループ
while True:
    # --- 1. イベント処理 ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        elif event.type == pygame.KEYDOWN:
            # ツール切り替えキー
            if event.key == pygame.K_1: player_tool = "hoe"
            elif event.key == pygame.K_2: player_tool = "water"
            elif event.key == pygame.K_3: player_tool = "seeds"
            elif event.key == pygame.K_4: player_tool = "harvest"
            # 作物切り替えキー
            elif event.key == pygame.K_z: selected_crop_type = "carrot"
            elif event.key == pygame.K_x: selected_crop_type = "wheat"
            elif event.key == pygame.K_c: selected_crop_type = "tomato"

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1: # 左クリック
                mx, my = event.mouse_pos if hasattr(event, 'mouse_pos') else pygame.mouse.get_pos()
                
                # 畑のクリック判定
                for farm in farms:
                    if farm["x"] <= mx <= farm["x"] + GRID_SIZE and farm["y"] <= my <= farm["y"] + GRID_SIZE:
                        # クワで耕す
                        if player_tool == "hoe" and farm["state"] == 0:
                            farm["state"] = 1
                        # じょうろで水やり
                        elif player_tool == "water" and farm["state"] in [1, 2]:
                            farm["watered"] = True
                        # 種まき
                        elif player_tool == "seeds" and farm["state"] in [1, 2] and farm["crop"] is None:
                            if money >= CROP_TYPES[selected_crop_type]["cost"]:
                                money -= CROP_TYPES[selected_crop_type]["cost"]
                                farm["crop"] = selected_crop_type
                                farm["growth"] = 0
                                farm["max_growth"] = CROP_TYPES[selected_crop_type]["growth_time"]
                                farm["state"] = 2
                        # 収穫
                        elif player_tool == "harvest" and farm["state"] == 4:
                            inventory[farm["crop"]] += 1
                            farm["crop"] = None
                            farm["state"] = 1
                            farm["watered"] = False

                # 動物をクリックしてお世話・収穫
                for anim in animals:
                    if abs(anim["x"] - mx) < 30 and abs(anim["y"] - my) < 30:
                        if anim["ready"]:
                            if anim["type"] == "chicken": inventory["egg"] += 1
                            elif anim["type"] == "cow": inventory["milk"] += 1
                            anim["ready"] = False
                            anim["timer"] = 0

                # ショップ（右下の売却ボタン）の判定
                # ニンジン売却
                if 550 <= mx <= 670 and 550 <= my <= 590:
                    if inventory["carrot"] > 0:
                        money += inventory["carrot"] * CROP_TYPES["carrot"]["price"]
                        inventory["carrot"] = 0
                # 小麦売却
                if 680 <= mx <= 800 and 550 <= my <= 590:
                    if inventory["wheat"] > 0:
                        money += inventory["wheat"] * CROP_TYPES["wheat"]["price"]
                        inventory["wheat"] = 0
                # トマト売却
                if 810 <= mx <= 930 and 550 <= my <= 590:
                    if inventory["tomato"] > 0:
                        money += inventory["tomato"] * CROP_TYPES["tomato"]["price"]
                        inventory["tomato"] = 0
                # 卵売却
                if 550 <= mx <= 670 and 600 <= my <= 640:
                    if inventory["egg"] > 0:
                        money += inventory["egg"] * 50
                        inventory["egg"] = 0
                # 牛乳売却
                if 680 <= mx <= 800 and 600 <= my <= 640:
                    if inventory["milk"] > 0:
                        money += inventory["milk"] * 120
                        inventory["milk"] = 0

    # --- 2. キーボード入力によるプレイヤー移動 ---
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w] or keys[pygame.K_UP]: player_y -= player_speed
    if keys[pygame.K_s] or keys[pygame.K_DOWN]: player_y += player_speed
    if keys[pygame.K_a] or keys[pygame.K_LEFT]: player_x -= player_speed
    if keys[pygame.K_d] or keys[pygame.K_RIGHT]: player_x += player_speed

    # 画面外に出ないように制限
    player_x = max(20, min(WIDTH - 20, player_x))
    player_y = max(130, min(HEIGHT - 20, player_y))

    # --- 3. 時間経過・作物成長・動物タイマーの更新 ---
    time_counter += 1
    if time_counter >= 600:  # 一定時間で日数が進む
        time_counter = 0
        day += 1

    for farm in farms:
        # 作物が植えられていて、水やりされている場合に成長
        if farm["crop"] is not None and farm["watered"]:
            farm["growth"] += 1
            if farm["growth"] >= farm["max_growth"]:
                farm["state"] = 4  # 収穫可能

    for anim in animals:
        if not anim["ready"]:
            anim["timer"] += 1
            if anim["timer"] > 400:  # 一定時間で生産物ができる
                anim["ready"] = True

    # --- 4. 描画処理 ---
    screen.fill(COLOR_BG)

    # 牧場の柵や装飾エリア
    pygame.draw.rect(screen, (160, 110, 60), (530, 130, 430, 530), 4)
    
    # 畑の描画
    for farm in farms:
        # 状態に応じた色
        if farm["state"] == 0:
            color = (100, 170, 100) # 草地
        elif farm["state"] == 1:
            color = COLOR_DRY       # 乾いた土
        elif farm["state"] == 2:
            color = COLOR_WATERED   # 水をあげた土
        elif farm["state"] == 3 or farm["state"] == 4:
            color = COLOR_WATERED

        pygame.draw.rect(screen, color, (farm["x"], farm["y"], GRID_SIZE - 2, GRID_SIZE - 2), border_radius=4)

        # 作物の描画
        if farm["crop"] is not None:
            c_info = CROP_TYPES[farm["crop"]]
            if farm["state"] == 4:
                # 収穫期（大きく表示）
                pygame.draw.circle(screen, c_info["color"], (farm["x"] + GRID_SIZE//2, farm["y"] + GRID_SIZE//2), 16)
            else:
                # 成長中（小さく表示）
                size = int(6 + 10 * (farm["growth"] / farm["max_growth"]))
                pygame.draw.circle(screen, c_info["color"], (farm["x"] + GRID_SIZE//2, farm["y"] + GRID_SIZE//2), size)

    # 動物の描画
    for anim in animals:
        if anim["type"] == "chicken":
            # ニワトリ（白丸にトサカ）
            pygame.draw.circle(screen, COLOR_WHITE, (anim["x"], anim["y"]), 18)
            pygame.draw.polygon(screen, (255, 69, 0), [(anim["x"]+10, anim["y"]-10), (anim["x"]+15, anim["y"]-5), (anim["x"]+10, anim["y"])])
        elif anim["type"] == "cow":
            # ウシ（大きめの四角っぽい体）
            pygame.draw.rect(screen, (240, 240, 240), (anim["x"]-25, anim["y"]-20, 50, 35), border_radius=8)
            pygame.draw.circle(screen, (50, 50, 50), (anim["x"]-10, anim["y"]-5), 6)
            pygame.draw.circle(screen, (50, 50, 50), (anim["x"]+10, anim["y"]+5), 6)

        # 生産物ができると頭上にアイコンを表示
        if anim["ready"]:
            pygame.draw.circle(screen, (255, 215, 0), (anim["x"], anim["y"] - 30), 10)
            txt_p = font_s.render("!", True, COLOR_BLACK)
            screen.blit(txt_p, (anim["x"]-3, anim["y"]-39))

    # プレイヤーの描画（青い丸）
    pygame.draw.circle(screen, (30, 144, 255), (int(player_x), int(player_y)), 14)
    pygame.draw.circle(screen, COLOR_WHITE, (int(player_x), int(player_y)), 14, 2)

    # --- 5. UI（上部ステータス・下部ショップパネル）の描画 ---
    # 上部情報バー
    pygame.draw.rect(screen, COLOR_UI_BG, (0, 0, WIDTH, 100))
    
    txt_money = font_l.render(f"所持金: {money:,} 円", True, (255, 215, 0))
    txt_day = font_m.render(f"経過日: {day}日目", True, COLOR_WHITE)
    screen.blit(txt_money, (20, 15))
    screen.blit(txt_day, (20, 55))

    # 現在のツール・選択作物の表示
    tool_names = {"hoe": "1: クワ（耕す）", "water": "2: じょうろ（水やり）", "seeds": "3: 種まき", "harvest": "4: 収穫"}
    txt_tool = font_m.render(f"選択ツール: [{tool_names[player_tool]}]  (切替: 1~4)", True, (135, 206, 250))
    screen.blit(txt_tool, (250, 15))

    if player_tool == "seeds":
        crop_names = {"carrot": "ニンジン (Z)", "wheat": "小麦 (X)", "tomato": "トマト (C)"}
        txt_crop_select = font_s.render(f"まく種: {crop_names[selected_crop_type]}  ※Z/X/Cキーで変更", True, COLOR_WHITE)
        screen.blit(txt_crop_select, (250, 55))

    # 右側：インベントリ＆出荷ショップパネル
    pygame.draw.rect(screen, (60, 60, 60), (530, 10, 450, 110), border_radius=6)
    inv_text = f"所持品 -> ニンジン:{inventory['carrot']} 小麦:{inventory['wheat']} トマト:{inventory['tomato']} 卵:{inventory['egg']} 牛乳:{inventory['milk']}"
    txt_inv = font_s.render(inv_text, True, COLOR_WHITE)
    screen.blit(txt_inv, (540, 20))

    # 出荷ボタンの描画
    buttons = [
        ("ニンジン売却", 550, 550, 120, 35),
        ("小麦売却", 680, 550, 120, 35),
        ("トマト売却", 810, 550, 120, 35),
        ("卵売却", 550, 600, 120, 35),
        ("牛乳売却", 680, 600, 120, 35),
    ]
    for b_text, bx, by, bw, bh in buttons:
        pygame.draw.rect(screen, (70, 130, 180), (bx, by, bw, bh), border_radius=4)
        t_surf = font_s.render(b_text, True, COLOR_WHITE)
        screen.blit(t_surf, (bx + 10, by + 8))

    pygame.display.flip()
    clock.tick(60)