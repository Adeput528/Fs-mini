from duckduckgo_search import DDGS

def search_web(query: str, max_results: int = 3) -> str:
    """Ищет информацию в сети и возвращает склеенные сниппеты."""
    try:
        results = DDGS().text(query, max_results=max_results)
        if not results:
            return "Поиск не дал результатов."
            
        context_lines = [f"- {res.get('body', '')}" for res in results]
        return "\n".join(context_lines)
    except Exception as e:
        return f"Ошибка веб-поиска: {e}"