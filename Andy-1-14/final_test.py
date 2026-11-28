"""Тест финального детекта."""
import cv2
import numpy as np
import subprocess
import time

subprocess.run(["scrot", "/tmp/final_test.png"], check=True)
time.sleep(0.3)

frame = cv2.imread('/tmp/final_test.png')
# Кроп окна игры
frame = frame[48:48+768, 262:262+1024]
h, w = frame.shape[:2]
print(f"Кадр: {w}x{h}")

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
    if cx < 100 and cy > h-280: continue
    if cx > w-220 and cy > h-220: continue
    if cy < 60: continue
    if cy > h-70: continue
    if cx < 200 and cy < 130: continue
    
    x1, y1 = max(0,cx-30), max(0,cy-30)
    x2, y2 = min(w,cx+30), min(h,cy+30)
    wn = cv2.countNonZero(white_mask[y1:y2, x1:x2])
    
    if wn < 2:
        continue
    
    found += 1
    print(f"  ✓ Поплавок ({cx},{cy}) area={area:.0f} white={wn}")
    cv2.rectangle(result, (cx-15,cy-15), (cx+15,cy+15), (0,255,0), 2)
    cv2.circle(result, (cx,cy), 3, (0,0,255), -1)

print(f"\nНайдено: {found}")
cv2.imwrite('/tmp/final_result.png', result)
print("💾 /tmp/final_result.png")
