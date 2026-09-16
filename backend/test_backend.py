import os
import sys
import yaml
from pathlib import Path

# Add backend directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.models import Profile, TailorRequest
from app.ai.heuristic import tailor_profile_heuristically
from app.latex.renderer import render_latex
from app.latex.compiler import compile_latex_to_pdf

def run_tests():
    data_dir = Path(__file__).resolve().parent / "data"
    output_dir = Path(__file__).resolve().parent.parent / "output"

    print("1. Loading sample_profile.yaml...")
    with open(data_dir / "sample_profile.yaml", "r", encoding="utf-8") as f:
        profile_data = yaml.safe_load(f)
    profile = Profile(**profile_data)
    print(f"   Candidate: {profile.contact.full_name} - {profile.contact.email}")

    print("2. Loading sample_job.txt...")
    with open(data_dir / "sample_job.txt", "r", encoding="utf-8") as f:
        job_text = f.read()

    print("3. Testing heuristic tailoring...")
    tailored = tailor_profile_heuristically(profile, job_text)
    print(f"   Target role: {tailored.target_role}")
    print(f"   Match score: {tailored.matching_score}%")
    print(f"   Adaptations: {len(tailored.key_adaptations)}")

    # Combine contact info with tailored data for rendering
    cv_render_data = tailored.model_dump()
    cv_render_data["contact"] = profile.contact.model_dump()

    templates = ["modern", "classic", "minimalist"]
    for tpl in templates:
        print(f"4. Testing template: {tpl}...")
        tex_code = render_latex(f"{tpl}.tex.j2", cv_render_data)
        assert "\\begin{document}" in tex_code, f"Template {tpl} failed to render document environment"
        print(f"   Template {tpl} rendered successfully ({len(tex_code)} chars).")

        print(f"   Compiling {tpl} to PDF...")
        success, pdf_path, err = compile_latex_to_pdf(tex_code, str(output_dir), file_stem=f"test_{tpl}")
        if not success:
            print(f"   FAILED to compile {tpl}: {err}")
            sys.exit(1)
        else:
            print(f"   SUCCESS! PDF generated at: {pdf_path}")
            assert os.path.exists(pdf_path), f"PDF file not found: {pdf_path}"

    print("\nALL BACKEND & LATEX TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    run_tests()
