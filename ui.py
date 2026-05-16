import tkinter as tk
import os
import threading
import config
import llm_engine
import web_tools
import screen_tools

class ScreenSnipper:
    def __init__(self, parent, callback):
        self.top = tk.Toplevel(parent)
        self.top.attributes("-fullscreen", True)
        self.top.attributes("-alpha", 0.3)
        self.top.configure(bg="black", cursor="cross")
        self.callback = callback
        
        self.canvas = tk.Canvas(self.top, bg="black", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        
        self.start_x = self.start_y = self.rect = None
        
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.top.bind("<Escape>", lambda e: self.top.destroy())

    def on_press(self, event):
        self.start_x, self.start_y = event.x, event.y
        self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, 1, 1, outline='red', width=2)

    def on_drag(self, event):
        self.canvas.coords(self.rect, self.start_x, self.start_y, event.x, event.y)

    def on_release(self, event):
        x1, y1 = min(self.start_x, event.x), min(self.start_y, event.y)
        x2, y2 = max(self.start_x, event.x), max(self.start_y, event.y)
        self.top.destroy()
        if (x2 - x1) > 10 and (y2 - y1) > 10:
            self.callback((x1, y1, x2, y2))


class FsMiniUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.overrideredirect(True)
        self.root.attributes("-alpha", config.UI_ALPHA)
        self.root.attributes("-topmost", True)
        self.root.configure(bg=config.UI_BG)
        
        w, h = 700, 300
        x = int((self.root.winfo_screenwidth()/2) - (w/2))
        y = int((self.root.winfo_screenheight()/3) - (h/2))
        self.root.geometry(f"{w}x{h}+{x}+{y}")

        self.entry = tk.Entry(self.root, font=("Consolas", 14), bg=config.UI_ENTRY_BG, fg=config.UI_TEXT_FG, insertbackground="white", relief="flat")
        self.entry.pack(pady=10, padx=10, fill=tk.X)
        self.entry.bind("<Return>", self.on_submit)
        self.entry.bind("<Escape>", self.hide_window)

        self.output = tk.Text(self.root, font=("Consolas", 12), bg=config.UI_BG, fg=config.UI_OUTPUT_FG, wrap=tk.WORD, relief="flat", state=tk.DISABLED)
        self.output.pack(pady=5, padx=10, fill=tk.BOTH, expand=True)

        self.root.bind("<FocusOut>", self.on_focus_out)
        self.root.withdraw()

    def on_submit(self, event=None):
        prompt = self.entry.get().strip()
        if not prompt: return
        
        if prompt.lower() in ['/quit', '/exit']:
            os._exit(0)
            
        self.entry.delete(0, tk.END)
        # Очищаем окно вывода перед стартом цепочки
        self.update_output("")
        
        threading.Thread(target=self.route_request, args=(prompt,), daemon=True).start()

    def route_request(self, prompt):
        if "/s " in prompt:
            parts = prompt.split("/s ", 1)
            standard_query = parts[0].strip()
            web_query = parts[1].strip()
            
            if web_query:
                self.append_output(f"[Сеть] Ищу в DuckDuckGo: {web_query}...\n")
                web_data = web_tools.search_web(web_query)
                self.append_output("[Сеть] Данные получены. Анализирую...\n\n")
                
                if standard_query:
                    final_prompt = (
                        f"Пользователь задал два вопроса. Отвечай максимально КРАТКО и по существу.\n\n"
                        f"1. Базовый вопрос: {standard_query}\n\n"
                        f"2. Опираясь на этот контекст из интернета:\n{web_data}\n"
                        f"Ответь на второй вопрос: {web_query}"
                    )
                else:
                    final_prompt = f"Контекст из интернета:\n{web_data}\n\nКратко ответь на вопрос: {web_query}"
            else:
                self.append_output("[ИИ] Пустой поисковый запрос. Обрабатываю базовую часть...\n\n")
                final_prompt = standard_query
        else:
            self.append_output("[ИИ] Fs-mini думает...\n\n")
            final_prompt = prompt

        reply = llm_engine.generate_response(final_prompt)
        self.append_output(reply)

    def update_output(self, text):
        self.output.config(state=tk.NORMAL)
        self.output.delete(1.0, tk.END)
        self.output.insert(tk.END, text)
        self.output.config(state=tk.DISABLED)

    def append_output(self, text):
        self.output.config(state=tk.NORMAL)
        self.output.insert(tk.END, text)
        self.output.see(tk.END)
        self.output.config(state=tk.DISABLED)

    def toggle_window(self):
        if self.root.winfo_viewable():
            self.hide_window()
        else:
            self.root.deiconify()
            self.root.focus_force()
            self.entry.focus_set()

    def hide_window(self, event=None):
        self.root.withdraw()

    def on_focus_out(self, event):
        self.root.after(100, self.check_real_focus_loss)

    def check_real_focus_loss(self):
        if self.root.focus_get() is None:
            self.hide_window()

    def trigger_ocr_screenshot(self):
        self.hide_window()
        ScreenSnipper(self.root, self.process_ocr_area)

    def process_ocr_area(self, bbox):
        self.toggle_window()
        self.update_output("[OCR] Сканирую выделенную область...\n")
        
        def task():
            text = screen_tools.extract_text_from_area(bbox)
            if not text:
                self.append_output("Текст не обнаружен. Попробуй выделить крупнее.\n")
                return
            
            self.append_output(f"Оригинал: {text}\n\n[ИИ] Перевожу...\n\n")
            prompt = f"Ты — профессиональный переводчик. Переведи следующий текст на русский язык. Ответь ТОЛЬКО переводом:\n\n{text}"
            
            reply = llm_engine.generate_response(prompt)
            self.append_output(reply)
            
        threading.Thread(target=task, daemon=True).start()