import tkinter as tk
import keyboard
import requests
import threading
import sys

# Настройки Ollama API
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "fs"

class FsMiniUI:
    def __init__(self):
        self.root = tk.Tk()
        # Убираем рамки окна и делаем его полупрозрачным
        self.root.overrideredirect(True)
        self.root.attributes("-alpha", 0.95)
        self.root.attributes("-topmost", True) # Поверх всех окон
        self.root.configure(bg="#2b2b2b")
        
        # Размещаем окно по центру
        window_width, window_height = 700, 300
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x_cordinate = int((screen_width/2) - (window_width/2))
        y_cordinate = int((screen_height/3) - (window_height/2))
        self.root.geometry(f"{window_width}x{window_height}+{x_cordinate}+{y_cordinate}")

        # Поле ввода
        self.entry = tk.Entry(self.root, font=("Consolas", 14), bg="#3c3c3c", fg="#ffffff", insertbackground="white", relief="flat")
        self.entry.pack(pady=10, padx=10, fill=tk.X)
        self.entry.bind("<Return>", self.send_request)
        self.entry.bind("<Escape>", self.hide_window)

        # Поле вывода
        self.output = tk.Text(self.root, font=("Consolas", 12), bg="#2b2b2b", fg="#cccccc", wrap=tk.WORD, relief="flat", state=tk.DISABLED)
        self.output.pack(pady=5, padx=10, fill=tk.BOTH, expand=True)

        # Умная проверка потери фокуса (чтобы не закрывалось при открытии)
        self.root.bind("<FocusOut>", self.on_focus_out)

        # Изначально окно скрыто (флаг self.is_visible удален)
        self.root.withdraw()

    def send_request(self, event=None):
        prompt = self.entry.get().strip()
        if not prompt:
            return
        
        # Системная команда для закрытия программы
        if prompt.lower() in ['/quit', '/exit']:
            self.root.quit()
            sys.exit()
            
        self.update_output("Fs-mini думает...\n")
        self.entry.delete(0, tk.END)
        
        # Запускаем в отдельном потоке
        threading.Thread(target=self.fetch_response, args=(prompt,), daemon=True).start()

    def fetch_response(self, prompt):
        payload = {"model": MODEL_NAME, "prompt": prompt, "stream": False}
        try:
            response = requests.post(OLLAMA_URL, json=payload)
            response.raise_for_status()
            reply = response.json().get("response", "Пустой ответ.")
            self.update_output(f"> {prompt}\n\n{reply}\n")
        except Exception as e:
            self.update_output(f"Ошибка связи с Ollama: {e}\n")

    def update_output(self, text):
        self.output.config(state=tk.NORMAL)
        self.output.delete(1.0, tk.END)
        self.output.insert(tk.END, text)
        self.output.config(state=tk.DISABLED)

    def toggle_window(self):
        # Робастная проверка: используем внутреннее состояние viewable() от tkinter
        if self.root.winfo_viewable():
            # Если окно видно — скрываем его
            self.hide_window()
        else:
            # Если окно скрыто — показываем и фокусируемся
            self.root.deiconify()
            self.root.focus_force() # Принудительный захват фокуса ОС
            self.entry.focus_set()  # Фокус на строку ввода

    def on_focus_out(self, event):
        # Даем системе 100мс на то, чтобы "успокоиться" с фокусом при открытии
        self.root.after(100, self.check_real_focus_loss)

    def check_real_focus_loss(self):
        # Скрываем окно, только если фокус ушел из всего приложения
        if self.root.focus_get() is None:
            self.hide_window()

    def hide_window(self, event=None):
        self.root.withdraw()
        # self.is_visible = False удалено, так как не используется

def start_app():
    app = FsMiniUI()
    # Горячая клавиша Shift + Space (требует прав администратора)
    keyboard.add_hotkey('shift+space', app.toggle_window)
    app.root.mainloop()

if __name__ == "__main__":
    start_app()