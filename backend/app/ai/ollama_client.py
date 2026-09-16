import json
import re
from typing import Optional
import requests
from ..models import Profile, TailoredCV
from .prompts import CV_TAILORING_PROMPT


def clean_json_response(text: str) -> str:
    cleaned = text.strip()
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", cleaned)
    if match:
        return match.group(1).strip()
    return cleaned


def tailor_with_ollama(
    profile: Profile,
    job_text: str,
    ollama_url: Optional[str] = "http://localhost:11434",
    model_name: Optional[str] = None
) -> TailoredCV:
    model = model_name or "llama3"
    endpoint = f"{ollama_url.rstrip('/')}/api/generate"

    user_payload = {
        "candidate_profile": profile.model_dump(),
        "job_offer_text": job_text,
    }

    full_prompt = f"{CV_TAILORING_PROMPT}\n\nDonnées d'entrée (JSON) :\n{json.dumps(user_payload, ensure_ascii=False)}"

    body = {
        "model": model,
        "prompt": full_prompt,
        "stream": False,
        "format": "json",
    }

    try:
        resp = requests.post(endpoint, json=body, timeout=120)
    except requests.exceptions.ConnectionError:
        raise RuntimeError(f"Impossible de se connecter à Ollama sur {ollama_url}. Assurez-vous qu'Ollama est démarré (`ollama serve`).")

    if resp.status_code != 200:
        raise RuntimeError(f"Erreur Ollama ({resp.status_code}): {resp.text}")

    data = resp.json()
    raw_text = data.get("response", "")
    parsed_json = json.loads(clean_json_response(raw_text))
    return TailoredCV(**parsed_json)
