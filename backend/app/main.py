import os
import re
import uuid
import tempfile
import yaml
from pathlib import Path
from typing import Dict, Any, List

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse

from .models import (
    Profile,
    TailorRequest,
    TailoredCV,
    GenerateRequest,
    JobOffer,
)
from .latex.renderer import render_latex
from .latex.compiler import compile_latex_to_pdf
from .ai.tailor import tailor_cv
from .ai.heuristic import extract_keywords_from_text, extract_job_title_from_text
from .extractor import parse_latex_cv, extract_text_from_pdf, parse_pdf_text_to_profile

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR.parent / "output"
TEMPLATES_DIR = BASE_DIR / "app" / "templates"

app = FastAPI(title="CV-Maker API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health_check():
    return {"status": "ok", "service": "CV-Maker API"}


@app.get("/api/templates")
def list_templates():
    return [
        {"id": "modern", "name": "Moderne & Épuré", "description": "Design sobre, touches de bleu roi, hiérarchie visuelle claire et optimisé ATS."},
        {"id": "classic", "name": "Classique Corporate", "description": "Style intemporel serif, parfait pour les secteurs traditionnels ou académiques."},
        {"id": "minimalist", "name": "Minimaliste 1-Page", "description": "Mise en page compacte et dense conçue pour tenir sur une seule page."},
    ]


@app.get("/api/profile", response_model=Profile)
def get_profile():
    current_path = DATA_DIR / "current_profile.yaml"
    sample_path = DATA_DIR / "sample_profile.yaml"

    target_file = current_path if current_path.exists() else sample_path
    if not target_file.exists():
        raise HTTPException(status_code=404, detail="Aucun profil trouvé.")

    try:
        with open(target_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return Profile(**data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors du chargement du profil: {str(e)}")


@app.post("/api/profile")
def save_profile(profile: Profile):
    try:
        current_path = DATA_DIR / "current_profile.yaml"
        with open(current_path, "w", encoding="utf-8") as f:
            yaml.dump(profile.model_dump(), f, allow_unicode=True, sort_keys=False)
        return {"status": "saved", "message": "Profil sauvegardé avec succès"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la sauvegarde: {str(e)}")


@app.get("/api/sample-job")
def get_sample_job():
    job_path = DATA_DIR / "sample_job.txt"
    if not job_path.exists():
        return {"job_text": ""}
    with open(job_path, "r", encoding="utf-8") as f:
        return {"job_text": f.read()}


@app.post("/api/analyze-job")
def analyze_job(payload: Dict[str, str]):
    job_text = payload.get("job_text", "")
    if not job_text.strip():
        raise HTTPException(status_code=400, detail="Le texte de l'offre ne peut pas être vide.")

    keywords = list(extract_keywords_from_text(job_text))
    title = extract_job_title_from_text(job_text)
    return {
        "title": title,
        "keywords": sorted(keywords),
        "count": len(keywords),
    }


@app.post("/api/tailor", response_model=TailoredCV)
def tailor_resume(request: TailorRequest):
    try:
        tailored = tailor_cv(request)
        return tailored
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur d'adaptation du CV: {str(e)}")


@app.post("/api/render-latex")
def render_latex_code(payload: Dict[str, Any]):
    template_name = payload.get("template", "modern")
    template_file = f"{template_name}.tex.j2"
    cv_data = payload.get("cv_data", {})

    try:
        tex_code = render_latex(template_file, cv_data)
        return {"latex_code": tex_code}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur de rendu LaTeX: {str(e)}")


@app.post("/api/compile-pdf")
def compile_pdf(payload: Dict[str, Any]):
    tex_code = payload.get("latex_code")
    template_name = payload.get("template", "modern")
    cv_data = payload.get("cv_data")

    # If raw latex is provided directly, use it; otherwise render from cv_data
    if not tex_code and cv_data:
        template_file = f"{template_name}.tex.j2"
        try:
            tex_code = render_latex(template_file, cv_data)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Erreur de templating LaTeX: {str(e)}")

    if not tex_code:
        raise HTTPException(status_code=400, detail="Le code LaTeX ou les données de CV sont obligatoires.")

    # Generate a unique stem based on candidate name or uuid
    candidate_name = ""
    if isinstance(cv_data, dict) and "contact" in cv_data and isinstance(cv_data["contact"], dict):
        candidate_name = cv_data["contact"].get("full_name", "")
    
    clean_name = re.sub(r"[^\w\-]", "_", candidate_name).strip("_") if candidate_name else "cv"
    file_stem = f"{clean_name}_{uuid.uuid4().hex[:6]}"

    success, pdf_path, error_msg = compile_latex_to_pdf(tex_code, str(OUTPUT_DIR), file_stem=file_stem)

    if not success:
        return JSONResponse(
            status_code=400,
            content={"success": False, "error": error_msg}
        )

    filename = os.path.basename(pdf_path)
    return {
        "success": True,
        "filename": filename,
        "download_url": f"/api/pdf/{filename}",
        "latex_code": tex_code
    }


@app.get("/api/pdf/{filename}")
def download_pdf(filename: str):
    # Prevent path traversal
    safe_name = os.path.basename(filename)
    file_path = OUTPUT_DIR / safe_name

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Fichier PDF introuvable.")

    return FileResponse(
        path=str(file_path),
        media_type="application/pdf",
        filename=safe_name,
        headers={"Content-Disposition": f'inline; filename="{safe_name}"'}
    )


@app.post("/api/extract-latex")
def extract_from_latex(payload: Dict[str, str]):
    latex_code = payload.get("latex_code", "")
    if not latex_code.strip():
        raise HTTPException(status_code=400, detail="Le code LaTeX ne peut pas être vide.")

    try:
        profile_data = parse_latex_cv(latex_code)
        return profile_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'extraction du LaTeX: {str(e)}")


@app.post("/api/extract-pdf")
async def extract_from_pdf(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Seuls les fichiers PDF sont acceptés.")

    try:
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name

        raw_text = extract_text_from_pdf(tmp_path)
        profile_data = parse_pdf_text_to_profile(raw_text)
        profile_data["_raw_text"] = raw_text[:3000]
        return profile_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'extraction du PDF: {str(e)}")
    finally:
        try:
            os.unlink(tmp_path)
        except Exception:
            pass

