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


def tailor_with_gemini(profile: Profile, job_text: str, api_key: str, model_name: Optional[str] = None) -> TailoredCV:
    model = model_name or "gemini-2.5-flash"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"

    user_payload = {
        "candidate_profile": profile.model_dump(),
        "job_offer_text": job_text,
    }

    full_prompt = f"{CV_TAILORING_PROMPT}\n\nDonnées d'entrée (JSON) :\n{json.dumps(user_payload, ensure_ascii=False)}"

    body = {
        "contents": [
            {
                "parts": [
                    {"text": full_prompt}
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.2,
            "responseMimeType": "application/json"
        }
    }

    resp = requests.post(url, json=body, timeout=60)
    if resp.status_code != 200:
        raise RuntimeError(f"Erreur API Gemini ({resp.status_code}): {resp.text}")

    data = resp.json()
    try:
        raw_text = data["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError):
        raise RuntimeError(f"Format de réponse Gemini inattendu : {data}")

    parsed_json = json.loads(clean_json_response(raw_text))
    return TailoredCV(**parsed_json)
