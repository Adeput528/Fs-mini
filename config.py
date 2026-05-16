import os

# Автоматически определяем директорию, где лежит этот config.py
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Настройки ядра Ollama
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "fs"

# Динамический путь к Tesseract (теперь он всегда ищет его в подпапке tesseract)
TESSERACT_PATH = os.path.join(BASE_DIR, 'tesseract', 'tesseract.exe')
# Настройки горячих клавиш
HOTKEY_ASK = 'shift+space'          # Открыть/закрыть окно ввода
HOTKEY_OCR = 'alt+shift+space'      # Перевод текста с экрана (Ножницы)

# Настройки UI
UI_BG = "#2b2b2b"
UI_ENTRY_BG = "#3c3c3c"
UI_TEXT_FG = "#ffffff"
UI_OUTPUT_FG = "#cccccc"
UI_ALPHA = 0.95