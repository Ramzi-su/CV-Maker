#!/usr/bin/env python3
import argparse
import os
import sys
import yaml
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT_DIR / "backend"))

from backend.app.models import Profile, TailorRequest
from backend.app.ai.tailor import tailor_cv
from backend.app.latex.renderer import render_latex
from backend.app.latex.compiler import compile_latex_to_pdf


def main():
    parser = argparse.ArgumentParser(
        description="CV-Maker : Générateur de CV LaTeX & PDF sur-mesure pour offres d'emploi"
    )
    parser.add_argument(
        "--profile",
        "-p",
        default="backend/data/sample_profile.yaml",
        help="Chemin vers le fichier YAML du profil maître",
    )
    parser.add_argument(
        "--job",
        "-j",
        default="backend/data/sample_job.txt",
        help="Chemin vers le fichier texte de l'offre d'emploi",
    )
    parser.add_argument(
        "--template",
        "-t",
        default="modern",
        choices=["modern", "classic", "minimalist"],
        help="Gabarit LaTeX à utiliser (modern, classic, minimalist)",
    )
    parser.add_argument(
        "--provider",
        default="heuristic",
        choices=["heuristic", "gemini", "openai", "ollama"],
        help="Fournisseur d'IA pour le ciblage (défaut: heuristic)",
    )
    parser.add_argument(
        "--api-key",
        default=os.environ.get("AI_API_KEY", None),
        help="Clé API si provider gemini ou openai (ou via variable AI_API_KEY)",
    )
    parser.add_argument(
        "--output-dir",
        "-o",
        default="output",
        help="Dossier de destination pour le PDF et le .tex",
    )

    args = parser.parse_args()

    profile_path = Path(args.profile)
    if not profile_path.exists():
        print(f"Erreur : Le fichier de profil {profile_path} est introuvable.", file=sys.stderr)
        sys.exit(1)

    job_path = Path(args.job)
    if not job_path.exists():
        print(f"Erreur : Le fichier d'offre {job_path} est introuvable.", file=sys.stderr)
        sys.exit(1)

    print(f"[*] Chargement du profil : {profile_path}")
    with open(profile_path, "r", encoding="utf-8") as f:
        profile_data = yaml.safe_load(f)
    profile = Profile(**profile_data)

    print(f"[*] Chargement de l'offre : {job_path}")
    with open(job_path, "r", encoding="utf-8") as f:
        job_text = f.read()

    print(f"[*] Adaptation du profil avec le moteur : {args.provider}...")
    tailor_req = TailorRequest(
        profile=profile,
        job_text=job_text,
        provider=args.provider,
        api_key=args.api_key,
    )
    tailored_cv = tailor_cv(tailor_req)

    print(f"[+] Profil adapté pour : {tailored_cv.target_role}")
    print(f"[+] Score de correspondance estimé : {tailored_cv.matching_score}%")
    if tailored_cv.key_adaptations:
        print("[+] Adaptations clés :")
        for ad in tailored_cv.key_adaptations:
            print(f"    - {ad}")

    # Render template
    cv_render_data = tailored_cv.model_dump()
    cv_render_data["contact"] = profile.contact.model_dump()

    template_file = f"{args.template}.tex.j2"
    print(f"[*] Rendu du gabarit LaTeX ({template_file})...")
    tex_code = render_latex(template_file, cv_render_data)

    # Compile with pdflatex
    output_dir = Path(args.output_dir)
    clean_role = "".join(c if c.isalnum() else "_" for c in tailored_cv.target_role[:30]).strip("_")
    stem = f"cv_{clean_role}"

    print(f"[*] Compilation pdflatex vers {output_dir}...")
    success, pdf_path, err = compile_latex_to_pdf(tex_code, str(output_dir), file_stem=stem)

    if not success:
        print(f"[!] Échec de compilation LaTeX :\n{err}", file=sys.stderr)
        sys.exit(1)

    print("\n[SUCCÈS] Le CV a été généré et compilé avec succès !")
    print(f"   -> Fichier PDF  : {pdf_path}")
    print(f"   -> Fichier TeX  : {output_dir / (stem + '.tex')}")


if __name__ == "__main__":
    main()
