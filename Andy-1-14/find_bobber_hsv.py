"""
Интерактивный подбор HSV поплавка.
Кликай на поплавок — показывает его HSV значения.
"""
import cv2
import numpy as np
import pyautogui

print("📸 Делаю скриншот...")
img = pyautogui.screenshot()
img.save('/tmp/bobber_pick.png')
frame = cv2.imread('/tmp/bobber_pick.png')

def click_event(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        # Берём область 5x5 вокруг клика
        region = frame[max(0,y-2):y+3, max(0,x-2):x+3]
        if region.size > 0:
            avg_color = region.mean(axis=(0,1))
            b, g, r = avg_color
            hsv = cv2.cvtColor(np.uint8([[avg_color]]), cv2.COLOR_BGR2HSV)[0][0]
            h, s, v = hsv
            print(f"Клик ({x},{y}): RGB=({r:.0f},{g:.0f},{b:.0f}) HSV=({h},{s},{v})")
            
            # Рисуем точку
            cv2.circle(frame, (x, y), 5, (0, 255, 0), -1)
            cv2.imshow('Кликни на поплавок', frame)

cv2.imshow('Кликни на поплавок', frame)
cv2.setMouseCallback('Кликни на поплавок', click_event)
print("Кликай на поплавок. Нажми 'q' для выхода.")

while True:
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
