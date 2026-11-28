"""
Диагностика детекта в боте.
Показывает, что видит бот на кропнутом кадре.
"""
import cv2
import numpy as np
import json
import subprocess
import time

with open('settings.dat', 'r', encoding='utf-8') as f:
    config = json.load(f)

# Захватываем кадр через scrot
subprocess.run(["scrot", "/tmp/debug_bot.png"], check=True)
time.sleep(0.3)

full_frame = cv2.imread('/tmp/debug_bot.png')
print(f"Полный кадр: {full_frame.shape[1]}x{full_frame.shape[0]}")

# Кропаем окно игры (как делает DisplayReader)
frame = full_frame[48:48+768, 262:262+1024].copy()
h, w = frame.shape[:2]
print(f"Кроп окна: {w}x{h}")

hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

# Розово-красный диапазон
red_mask = cv2.inRange(hsv, np.array([150, 80, 60]), np.array([180, 255, 255]))
white_mask = cv2.inRange(hsv, np.array([0, 0, 160]), np.array([180, 50, 255]))

kernel = np.ones((2,2), np.uint8)
red_mask = cv2.morphologyEx(red_mask, cv2.MORPH_OPEN, kernel)
red_mask = cv2.morphologyEx(red_mask, cv2.MORPH_CLOSE, kernel)

contours, _ = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

result = frame.copy()
found = 0

print("\n=== Поиск поплавка ===")
for c in contours:
    area = cv2.contourArea(c)
    if not (5 < area < 500):
        continue
    
    M = cv2.moments(c)
    if M["m00"] <= 0:
        continue
    
    cx = int(M["m10"]/M["m00"])
    cy = int(M["m01"]/M["m00"])
    
    # UI фильтр
    if cx < 100 and cy > h-280:
        print(f"  ✗ ({cx},{cy}) area={area:.0f} - UI (чат)")
        continue
    if cx > w-220 and cy > h-220:
        print(f"  ✗ ({cx},{cy}) area={area:.0f} - UI (мини-карта)")
        continue
    if cy < 60:
        print(f"  ✗ ({cx},{cy}) area={area:.0f} - UI (верх)")
        continue
    if cy > h-70:
        print(f"  ✗ ({cx},{cy}) area={area:.0f} - UI (низ)")
        continue
    if cx < 200 and cy < 130:
        print(f"  ✗ ({cx},{cy}) area={area:.0f} - UI (портрет)")
        continue
    
    x1, y1 = max(0,cx-30), max(0,cy-30)
    x2, y2 = min(w,cx+30), min(h,cy+30)
    wn = cv2.countNonZero(white_mask[y1:y2, x1:x2])
    
    if wn < 2:
        print(f"  ✗ ({cx},{cy}) area={area:.0f} white={wn} - мало белых")
        continue
    
    found += 1
    print(f"  ✓ Поплавок ({cx},{cy}) area={area:.0f} white={wn}")
    cv2.rectangle(result, (cx-15,cy-15), (cx+15,cy+15), (0,255,0), 2)
    cv2.circle(result, (cx,cy), 3, (0,0,255), -1)

print(f"\nНайдено поплавков: {found}")

# Рисуем зоны поиска (как в боте)
pointer_pos = (w//2, h//2)  # Центр окна (курсор по умолчанию)
center = (w//2, h//2)
zone_count = config.get("zone_count", 5)
zone_spacing = config.get("zone_spacing", 80)
zone_size = config.get("zone_size", 100)

print(f"\n=== Зоны поиска (курсор в центре) ===")
for i in range(zone_count):
    cx = center[0] + zone_spacing * i
    cy = center[1]
    half = zone_size // 2
    cv2.rectangle(result, (cx-half, cy-half), (cx+half, cy+half), (127, 0, 127), 2)
    print(f"  Зона {i+1}: ({cx},{cy}) размер={zone_size}")

cv2.imwrite('/tmp/debug_bot_result.png', result)
print(f"\n💾 /tmp/debug_bot_result.png")
