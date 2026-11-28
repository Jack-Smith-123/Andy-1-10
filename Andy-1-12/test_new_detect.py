"""Тест нового детекта на скриншоте."""
import cv2
import numpy as np
import json
import subprocess

with open('settings.dat', 'r', encoding='utf-8') as f:
    config = json.load(f)

subprocess.run(["scrot", "/tmp/test_frame.png"], check=True)
import time; time.sleep(0.3)
frame = cv2.imread('/tmp/test_frame.png')

# Кроп окна игры (координаты из логов)
frame = frame[48:48+768, 262:262+1024]
h, w = frame.shape[:2]
print(f"Кадр окна: {w}x{h}")

hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

# Два диапазона красного
mask1 = cv2.inRange(hsv, np.array([0, 100, 80]), np.array([15, 255, 255]))
mask2 = cv2.inRange(hsv, np.array([160, 100, 80]), np.array([180, 255, 255]))
red_mask = cv2.bitwise_or(mask1, mask2)

white_mask = cv2.inRange(hsv, np.array([0, 0, 180]), np.array([180, 40, 255]))

kernel = np.ones((2,2), np.uint8)
red_mask = cv2.morphologyEx(red_mask, cv2.MORPH_OPEN, kernel)
red_mask = cv2.morphologyEx(red_mask, cv2.MORPH_CLOSE, kernel)

contours, _ = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

result = frame.copy()
found = 0
for c in contours:
    area = cv2.contourArea(c)
    if not (15 < area < 800):
        continue
    M = cv2.moments(c)
    if M["m00"] <= 0:
        continue
    cx = int(M["m10"]/M["m00"])
    cy = int(M["m01"]/M["m00"])

    # UI фильтр
    if cx < 80 and cy > h-250: continue
    if cx > w-200 and cy > h-200: continue
    if cy < 50: continue
    if cy > h-60: continue
    if cx < 180 and cy < 120: continue

    x1, y1 = max(0,cx-25), max(0,cy-25)
    x2, y2 = min(w,cx+25), min(h,cy+25)
    wn = cv2.countNonZero(white_mask[y1:y2, x1:x2])
    if wn < 3:
        continue

    per = cv2.arcLength(c, True)
    circ = 4*np.pi*area/(per*per) if per>0 else 0
    if circ < 0.15:
        continue

    found += 1
    print(f"  ✓ ({cx},{cy}) area={area:.0f} white={wn} circ={circ:.2f}")
    cv2.rectangle(result, (cx-20,cy-20), (cx+20,cy+20), (0,255,0), 2)

print(f"\nНайдено кандидатов: {found}")
cv2.imwrite('/tmp/test_result.png', result)
print("💾 /tmp/test_result.png")
