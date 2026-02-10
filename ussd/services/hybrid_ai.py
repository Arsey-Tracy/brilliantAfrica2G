from django.core.cache import cache
from .ai_service import AIService

def hybrid_ai_response(message: str):
    cache_key = f"ai_cache_{message.lower().strip()}"
    cached_response = cache.get(cache_key)
    if cached_response:
        return cached_response
    
    # Phase 1: simple rules (expand later)
    if message.upper() == "HELP":
        msg = "Commands: QUIZME topic, GUIDE topic, NEXT for long replies."
        return msg
    # Phase 2: (future) retrieval layer can be added here 
    # Phase 3: AI response LLM fallback
    ai_service = AIService()
    prompt = ai_service.build_ai_prompt(message)
    result = ai_service.query_ai_model(prompt)
    cache.set(cache_key, result, timeout=86400)  # Cache for 1 day
    return result