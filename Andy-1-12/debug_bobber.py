"""
Диагностика детекта поплавка через scrot.
"""
import cv2
import numpy as np
import json
import subprocess
import os
import time

print("📸 Делаю скриншот через scrot...")
subprocess.run(["scrot", "/tmp/debug_frame.png"], check=True)
time.sleep(0.5)

if not os.path.exists('/tmp/debug_frame.png'):
    print("❌ Скриншот не создан!")
    exit(1)

frame = cv2.imread('/tmp/debug_frame.png')
h, w = frame.shape[:2]
print(f"✓ Кадр получен: {w}x{h}")

hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

# Пробуем разные диапазоны красного
ranges = [
    ("Текущий (H0-15, S150-255)", 0, 15, 150, 255, 100, 255),
    ("Широкий красный (H0-20, S100-255)", 0, 20, 100, 255, 80, 255),
    ("Очень широкий (H0-25, S80-255)", 0, 25, 80, 255, 60, 255),
    ("Только яркий (H0-10, S200-255)", 0, 10, 200, 255, 150, 255),
    ("Красный+розовый (H150-180)", 150, 180, 100, 255, 80, 255),
    ("Весь красный спектр (H0-10 + H160-180)", None, None, None, None, None, None),
]

for name, h1, h2, s1, s2, v1, v2 in ranges:
    if h1 is None:
        # Специальный случай: объединяем два диапазона
        mask1 = cv2.inRange(hsv, np.array([0, 100, 80]), np.array([10, 255, 255]))
        mask2 = cv2.inRange(hsv, np.array([160, 100, 80]), np.array([180, 255, 255]))
        mask = cv2.bitwise_or(mask1, mask2)
    else:
        mask = cv2.inRange(hsv, np.array([h1, s1, v1]), np.array([h2, s2, v2]))
    
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    valid = []
    for c in contours:
        area = cv2.contourArea(c)
        if 20 < area < 3000:
            M = cv2.moments(c)
            if M["m00"] > 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                valid.append((cx, cy, area))
    
    print(f"\n{name}: найдено {len(valid)} объектов")
    for cx, cy, area in valid[:8]:
        print(f"  ({cx}, {cy}) площадь={area:.0f}")

# Проверяем белый
white_mask = cv2.inRange(hsv, np.array([0, 0, 200]), np.array([180, 30, 255]))
white_count = cv2.countNonZero(white_mask)
print(f"\nБелых пикселей (S<30, V>200): {white_count}")

# Сохраняем маски
cv2.imwrite('/tmp/debug_red_mask.png', cv2.inRange(hsv, np.array([0, 150, 100]), np.array([15, 255, 255])))
cv2.imwrite('/tmp/debug_white_mask.png', white_mask)

# Рисуем результат
result = frame.copy()
mask = cv2.inRange(hsv, np.array([0, 150, 100]), np.array([15, 255, 255]))
for c in cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]:
    area = cv2.contourArea(c)
    if 20 < area < 3000:
        cv2.drawContours(result, [c], -1, (0, 255, 0), 2)
        M = cv2.moments(c)
        if M["m00"] > 0:
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
            cv2.circle(result, (cx, cy), 3, (255, 0, 0), -1)
cv2.imwrite('/tmp/debug_result.png', result)

print("\n💾 Файлы сохранены:")
print("  /tmp/debug_frame.png     - оригинал")
print("  /tmp/debug_red_mask.png  - маска красного")
print("  /tmp/debug_white_mask.png- маска белого")
print("  /tmp/debug_result.png    - результат детекта (зелёные контуры)")
