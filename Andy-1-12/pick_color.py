"""
Кликни на поплавок — покажет точный HSV.
"""
import cv2
import numpy as np
import subprocess
import time

subprocess.run(["scrot", "/tmp/pick.png"], check=True)
time.sleep(0.3)

frame = cv2.imread('/tmp/pick.png')
# Кроп окна игры
frame = frame[48:48+768, 262:262+1024]

def click(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        # Берём область 3x3 вокруг клика
        region = frame[max(0,y-1):y+2, max(0,x-1):x+2]
        if region.size > 0:
            avg = region.mean(axis=(0,1))
            hsv = cv2.cvtColor(np.uint8([[avg]]), cv2.COLOR_BGR2HSV)[0][0]
            print(f"Клик ({x},{y}): BGR=({avg[0]:.0f},{avg[1]:.0f},{avg[2]:.0f}) HSV=({hsv[0]},{hsv[1]},{hsv[2]})")
            
            cv2.circle(frame, (x,y), 3, (0,255,0), -1)
            cv2.imshow('Кликни на поплавок (q=выход)', frame)

cv2.imshow('Кликни на поплавок (q=выход)', frame)
cv2.setMouseCallback('Кликни на поплавок (q=выход)', click)
print("Кликай на поплавок. Нажми 'q' для выхода.")

while True:
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
