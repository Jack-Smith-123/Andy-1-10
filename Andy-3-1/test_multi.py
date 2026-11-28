# test_multi.py - проверка мульти-шаблонов
import time, cv2
from config import WINDOW_TITLE, TARGET_FPS
from window_manager import WindowManager
from capture import ScreenCapture
from detector import BobberDetector

def main():
    wm = WindowManager(WINDOW_TITLE); wm.update_geometry()
    cap = ScreenCapture(wm)
    det = BobberDetector()
    ft = 1.0 / TARGET_FPS
    print("✅ Тест мульти-шаблонов. Нажми 'q' для выхода.")
    
    while True:
        t0 = time.time()
        frame = cap.get_frame(); m = cap.get_mouse_rel()
        
        if frame is not None and m is not None:
            state, pos, conf = det.find_state(frame, m)
            
            if pos:
                color = (0, 255, 0) if state == 'idle' else (0, 0, 255)
                cv2.circle(frame, pos, 10, color, 3)
                label = f"{state} {conf:.2f}"
                cv2.putText(frame, label, (pos[0]-50, pos[1]-20),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
                
                if state == 'dive':
                    cv2.putText(frame, ">>> BITE! <<<", (10, 40),
                                cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0,0,255), 3)
                    print(f"🔥 КЛЕВ! ({pos[0]}, {pos[1]}) conf={conf:.2f}")
            
            cv2.imshow("Andy-3", frame)
        
        st = ft - (time.time() - t0)
        if st > 0: time.sleep(st)
        if cv2.waitKey(1) & 0xFF == ord('q'): break
    
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
