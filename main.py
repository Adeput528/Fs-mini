import keyboard
import ctypes
import os
import signal
import config
from ui import FsMiniUI

def main():
    # Говорим Windows не искажать координаты при масштабе 125-150%
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass
        
    # Жесткий перехват нажатия Ctrl+C в консоли
    signal.signal(signal.SIGINT, lambda sig, frame: os._exit(0))

    app = FsMiniUI()
    
    # "Будильник" для tkinter. Без него mainloop() полностью игнорирует сигналы Ctrl+C
    def check_signals():
        app.root.after(500, check_signals)
    app.root.after(500, check_signals)
    
    # Назначаем глобальные сочетания клавиш
    keyboard.add_hotkey(config.HOTKEY_ASK, app.toggle_window)
    keyboard.add_hotkey(config.HOTKEY_OCR, app.trigger_ocr_screenshot)
    
    app.root.mainloop()

if __name__ == "__main__":
    main()