from ..models import TailorRequest, TailoredCV
from .heuristic import tailor_profile_heuristically
from .gemini_client import tailor_with_gemini
from .openai_client import tailor_with_openai
from .ollama_client import tailor_with_ollama


def tailor_cv(request: TailorRequest) -> TailoredCV:
    provider = (request.provider or "heuristic").lower()

    if provider == "gemini":
        if not request.api_key:
            raise ValueError("Une clé API Gemini est requise pour utiliser le fournisseur Gemini.")
        return tailor_with_gemini(request.profile, request.job_text, request.api_key, request.model_name)

    elif provider in ("openai", "groq", "deepseek"):
        if not request.api_key:
            raise ValueError(f"Une clé API est requise pour le fournisseur {provider}.")
        base_url = None
        if provider == "groq":
            base_url = "https://api.groq.com/openai/v1"
        elif provider == "deepseek":
            base_url = "https://api.deepseek.com"
        return tailor_with_openai(request.profile, request.job_text, request.api_key, request.model_name, base_url)

    elif provider == "ollama":
        return tailor_with_ollama(request.profile, request.job_text, request.ollama_url, request.model_name)

    else:
        # Fallback to intelligent local heuristic
        return tailor_profile_heuristically(request.profile, request.job_text)
