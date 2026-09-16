import os
import shutil
import subprocess
import tempfile
from typing import Tuple


def extract_latex_error(log_content: str) -> str:
    lines = log_content.splitlines()
    error_lines = []
    capture = False
    for line in lines:
        if line.startswith("!"):
            capture = True
            error_lines.append(line)
        elif capture:
            error_lines.append(line)
            if len(error_lines) > 8 or line.strip() == "":
                break
    if error_lines:
        return "\n".join(error_lines)
    return "Erreur inconnue lors de la compilation pdflatex."


def compile_latex_to_pdf(tex_content: str, output_dir: str, file_stem: str = "cv") -> Tuple[bool, str, str]:
    os.makedirs(output_dir, exist_ok=True)
    with tempfile.TemporaryDirectory() as build_dir:
        tex_filename = f"{file_stem}.tex"
        pdf_filename = f"{file_stem}.pdf"
        tex_path = os.path.join(build_dir, tex_filename)

        with open(tex_path, "w", encoding="utf-8") as f:
            f.write(tex_content)

        # pdflatex run (run twice to resolve any references/geometry if needed)
        cmd = [
            "pdflatex",
            "-interaction=nonstopmode",
            "-halt-on-error",
            f"-output-directory={build_dir}",
            tex_path,
        ]

        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        log_path = os.path.join(build_dir, f"{file_stem}.log")
        log_content = ""
        if os.path.exists(log_path):
            try:
                with open(log_path, "r", encoding="utf-8", errors="replace") as f:
                    log_content = f.read()
            except Exception:
                pass

        if result.returncode != 0:
            error_msg = extract_latex_error(log_content)
            return False, "", f"Échec de compilation LaTeX:\n{error_msg}"

        # Success - copy tex and pdf to output_dir
        dest_pdf = os.path.join(output_dir, pdf_filename)
        dest_tex = os.path.join(output_dir, tex_filename)

        built_pdf = os.path.join(build_dir, pdf_filename)
        if not os.path.exists(built_pdf):
            return False, "", "Fichier PDF non trouvé après compilation réussie."

        shutil.copy2(built_pdf, dest_pdf)
        shutil.copy2(tex_path, dest_tex)

        return True, dest_pdf, ""
