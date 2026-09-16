from typing import Optional
from ..models import Profile
from .gemini_client import extract_with_gemini
from .openai_client import extract_with_openai
from .ollama_client import extract_with_ollama

def extract_profile_with_ai(
    raw_text: str,
    provider: str,
    api_key: Optional[str] = None,
    model_name: Optional[str] = None,
    ollama_url: Optional[str] = "http://localhost:11434"
) -> Profile:
    provider = provider.lower()
    
    if provider == "gemini":
        if not api_key:
            raise ValueError("Une clé API Gemini est requise pour utiliser ce fournisseur lors de l'extraction.")
        return extract_with_gemini(raw_text, api_key, model_name)
        
    elif provider in ("openai", "groq", "deepseek"):
        if not api_key:
            raise ValueError(f"Une clé API est requise pour le fournisseur {provider} lors de l'extraction.")
        base_url = None
        if provider == "groq":
            base_url = "https://api.groq.com/openai/v1"
        elif provider == "deepseek":
            base_url = "https://api.deepseek.com"
        return extract_with_openai(raw_text, api_key, model_name, base_url)
        
    elif provider == "ollama":
        return extract_with_ollama(raw_text, ollama_url, model_name)
        
    raise ValueError(f"Fournisseur IA non supporté pour l'extraction: {provider}")
