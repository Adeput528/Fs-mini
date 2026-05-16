import pytesseract
from PIL import ImageGrab, ImageEnhance
import config

pytesseract.pytesseract.tesseract_cmd = config.TESSERACT_PATH

def extract_text_from_area(bbox) -> str:
    try:
        img = ImageGrab.grab(bbox)
        
        # --- Блок улучшения зрения ИИ ---
        # 1. Переводим скриншот в оттенки серого (убираем цветовой шум)
        img = img.convert('L')
        # 2. Искусственно выкручиваем контрастность в 2 раза
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(2.0)
        # --------------------------------
        
        text = pytesseract.image_to_string(img, lang='rus+eng', config='--psm 6')
        return text.strip()
    except Exception as e:
        return f"Ошибка OCR: {e}"