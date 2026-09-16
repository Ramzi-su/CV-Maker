import json
import re
from typing import Optional
import requests
from ..models import Profile, TailoredCV
from .prompts import CV_TAILORING_PROMPT, CV_EXTRACTION_PROMPT


def clean_json_response(text: str) -> str:
    cleaned = text.strip()
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", cleaned)
    if match:
        return match.group(1).strip()
    return cleaned


def tailor_with_openai(
    profile: Profile,
    job_text: str,
    api_key: str,
    model_name: Optional[str] = None,
    base_url: Optional[str] = None
) -> TailoredCV:
    model = model_name or "gpt-4o-mini"
    url = f"{base_url.rstrip('/')}/chat/completions" if base_url else "https://api.openai.com/v1/chat/completions"

    user_payload = {
        "candidate_profile": profile.model_dump(),
        "job_offer_text": job_text,
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    body = {
        "model": model,
        "messages": [
            {"role": "system", "content": CV_TAILORING_PROMPT},
            {"role": "user", "content": json.dumps(user_payload, ensure_ascii=False)}
        ],
        "temperature": 0.2,
        "response_format": {"type": "json_object"},
    }

    resp = requests.post(url, headers=headers, json=body, timeout=60)
    if resp.status_code != 200:
        raise RuntimeError(f"Erreur API ({resp.status_code}): {resp.text}")

    data = resp.json()
    try:
        raw_text = data["choices"][0]["message"]["content"]
    except (KeyError, IndexError):
        raise RuntimeError(f"Format de réponse inattendu : {data}")

    parsed_json = json.loads(clean_json_response(raw_text))
    return TailoredCV(**parsed_json)


def extract_with_openai(
    raw_text: str,
    api_key: str,
    model_name: Optional[str] = None,
    base_url: Optional[str] = None
) -> Profile:
    model = model_name or "gpt-4o-mini"
    url = f"{base_url.rstrip('/')}/chat/completions" if base_url else "https://api.openai.com/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    body = {
        "model": model,
        "messages": [
            {"role": "system", "content": CV_EXTRACTION_PROMPT},
            {"role": "user", "content": f"Texte brut du CV à extraire :\n{raw_text}"}
        ],
        "temperature": 0.1,
        "response_format": {"type": "json_object"},
    }

    resp = requests.post(url, headers=headers, json=body, timeout=60)
    if resp.status_code != 200:
        raise RuntimeError(f"Erreur API ({resp.status_code}): {resp.text}")

    data = resp.json()
    try:
        raw_output = data["choices"][0]["message"]["content"]
    except (KeyError, IndexError):
        raise RuntimeError(f"Format de réponse inattendu : {data}")

    parsed_json = json.loads(clean_json_response(raw_output))
    return Profile(**parsed_json)
