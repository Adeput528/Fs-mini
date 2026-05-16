import requests
import config

def generate_response(prompt: str) -> str:
    """Отправляет запрос в Ollama и возвращает финальный ответ модели."""
    payload = {
        "model": config.MODEL_NAME,
        "prompt": prompt,
        "stream": False # Отключаем стриминг для упрощения локальной сборки UI
    }
    try:
        response = requests.post(config.OLLAMA_URL, json=payload)
        response.raise_for_status()
        return response.json().get("response", "Ошибка: пустой ответ от модели.")
    except Exception as e:
        return f"Ошибка связи с Ollama: {e}"