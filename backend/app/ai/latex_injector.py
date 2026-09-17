import json
import requests
from .prompts import LATEX_INJECTION_PROMPT

def inject_profile_into_latex(latex_template: str, cv_data: dict, provider: str, api_key: str = None, model_name: str = None, ollama_url: str = None) -> str:
    prompt = LATEX_INJECTION_PROMPT.format(
        latex_template=latex_template,
        cv_data=json.dumps(cv_data, ensure_ascii=False, indent=2)
    )

    provider = provider.lower()
    response_text = ""

    try:
        if provider == "gemini":
            model = model_name or "gemini-2.5-flash"
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
            body = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"temperature": 0.2}
            }
            resp = requests.post(url, json=body, timeout=60)
            resp.raise_for_status()
            response_text = resp.json()["candidates"][0]["content"]["parts"][0]["text"]

        elif provider in ["openai", "groq", "deepseek"]:
            if provider == "openai":
                model = model_name or "gpt-4o-mini"
                url = "https://api.openai.com/v1/chat/completions"
            elif provider == "groq":
                model = model_name or "llama-3.1-70b-versatile"
                url = "https://api.groq.com/openai/v1/chat/completions"
            elif provider == "deepseek":
                model = model_name or "deepseek-chat"
                url = "https://api.deepseek.com/chat/completions"

            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            }
            body = {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.2,
            }
            resp = requests.post(url, headers=headers, json=body, timeout=60)
            resp.raise_for_status()
            response_text = resp.json()["choices"][0]["message"]["content"]

        elif provider == "ollama":
            model = model_name or "llama3"
            base_url = (ollama_url or "http://localhost:11434").rstrip('/')
            url = f"{base_url}/api/chat"
            body = {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "stream": False,
                "options": {"temperature": 0.2}
            }
            resp = requests.post(url, json=body, timeout=120)
            resp.raise_for_status()
            response_text = resp.json()["message"]["content"]

        else:
            raise ValueError(f"Provider non supporté pour l'injection LaTeX : {provider}")
            
    except Exception as e:
        raise Exception(f"Erreur avec le provider {provider}: {str(e)}")

    # Nettoyage de la réponse (suppression des balises markdown si présentes)
    response_text = response_text.strip()
    if response_text.startswith("```latex"):
        response_text = response_text[8:]
    elif response_text.startswith("```tex"):
        response_text = response_text[6:]
    elif response_text.startswith("```"):
        response_text = response_text[3:]
    
    if response_text.endswith("```"):
        response_text = response_text[:-3]

    return response_text.strip()
