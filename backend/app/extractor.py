import re
import os
import subprocess
import tempfile
from typing import Dict, List, Optional, Any


def parse_latex_cv(latex_code: str) -> Dict[str, Any]:
    """Parse a LaTeX CV source code and extract structured profile information."""
    result = {
        "contact": {
            "full_name": "",
            "title": "",
            "email": "",
            "phone": "",
            "location": "",
            "linkedin": "",
            "github": "",
            "website": "",
        },
        "summary": "",
        "experiences": [],
        "education": [],
        "projects": [],
        "skill_categories": [],
        "languages": [],
        "certifications": [],
    }

    # Strip LaTeX comments
    cleaned = re.sub(r'(?<!\\)%.*', '', latex_code)

    # --- Contact Information ---
    # Name: look for \Huge, \LARGE, or the first bold text near the top
    name_patterns = [
        r'\\(?:Huge|LARGE|Large)\s*(?:\\(?:textbf|bfseries)\s*)?(?:\\(?:scshape|textsc)\s*)?[{]?\s*([^}\\]+?)\s*[}]?\\',
        r'\\(?:textbf|bfseries)\s*\{\\(?:Huge|LARGE|Large)\s+([^}]+)\}',
        r'\\name\s*\{([^}]+)\}',
        r'\\cvname\s*\{([^}]+)\}',
    ]
    for pat in name_patterns:
        m = re.search(pat, cleaned)
        if m:
            name = m.group(1).strip()
            name = re.sub(r'\\[a-zA-Z]+\{?', '', name).strip().rstrip('}')
            if len(name) > 2:
                result["contact"]["full_name"] = name
                break

    # Email
    email_patterns = [
        r'\\href\{mailto:([^}]+)\}',
        r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
    ]
    for pat in email_patterns:
        m = re.search(pat, cleaned)
        if m:
            result["contact"]["email"] = m.group(1) if '(' in pat or '{' in pat else m.group(0)
            break

    # Phone
    phone_m = re.search(r'(?:\+\d{1,3}[\s\-]?)?(?:\(?\d{1,4}\)?[\s\-]?)?[\d\s\-]{6,15}', cleaned)
    if phone_m:
        phone_candidate = phone_m.group(0).strip()
        if re.search(r'\d{6,}', phone_candidate.replace(' ', '').replace('-', '')):
            result["contact"]["phone"] = phone_candidate

    # LinkedIn
    linkedin_m = re.search(r'(?:linkedin\.com/in/|linkedin\.com/)[^\s},\\]+', cleaned, re.IGNORECASE)
    if linkedin_m:
        result["contact"]["linkedin"] = linkedin_m.group(0).strip()

    # GitHub
    github_m = re.search(r'(?:github\.com/)[^\s},\\]+', cleaned, re.IGNORECASE)
    if github_m:
        result["contact"]["github"] = github_m.group(0).strip()

    # Location (common patterns near contact info)
    loc_patterns = [
        r'(?:Paris|Lyon|Marseille|Toulouse|Bordeaux|Lille|Strasbourg|Nantes|Nice|Montpellier|Rennes)[^\\}\n]{0,30}(?:France|FR)?',
        r'\b(?:France|Algérie|Maroc|Tunisie|Belgique|Suisse|Canada)\b',
    ]
    for pat in loc_patterns:
        loc_m = re.search(pat, cleaned, re.IGNORECASE)
        if loc_m:
            result["contact"]["location"] = loc_m.group(0).strip().rstrip(',').strip()
            break

    # --- Sections extraction ---
    # Find all \section or \section* blocks
    section_pattern = r'\\section\*?\{([^}]+)\}'
    sections = list(re.finditer(section_pattern, cleaned))

    def get_section_content(idx: int) -> str:
        start = sections[idx].end()
        end = sections[idx + 1].start() if idx + 1 < len(sections) else len(cleaned)
        return cleaned[start:end]

    for i, sec in enumerate(sections):
        sec_name = sec.group(1).lower().strip()
        content = get_section_content(i)

        # --- Summary / Profile ---
        if any(kw in sec_name for kw in ['profil', 'résumé', 'summary', 'objectif', 'about', 'accroche']):
            summary = re.sub(r'\\[a-zA-Z]+\s*(?:\{[^}]*\})?', '', content)
            summary = re.sub(r'[{}]', '', summary).strip()
            lines = [l.strip() for l in summary.splitlines() if l.strip()]
            result["summary"] = ' '.join(lines)

        # --- Experiences ---
        elif any(kw in sec_name for kw in ['expérience', 'experience', 'emploi', 'parcours']):
            result["experiences"] = _extract_experiences(content)

        # --- Education ---
        elif any(kw in sec_name for kw in ['formation', 'education', 'études', 'diplôme', 'académique']):
            result["education"] = _extract_education(content)

        # --- Skills ---
        elif any(kw in sec_name for kw in ['compétence', 'skill', 'technique', 'technologie']):
            result["skill_categories"] = _extract_skills(content)

        # --- Projects ---
        elif any(kw in sec_name for kw in ['projet', 'project', 'réalisation']):
            result["projects"] = _extract_projects(content)

        # --- Languages & Certifications ---
        elif any(kw in sec_name for kw in ['langue', 'language', 'certification', 'autre', 'divers']):
            langs, certs = _extract_languages_certs(content)
            if langs:
                result["languages"] = langs
            if certs:
                result["certifications"] = certs

    # Fallback title from first experience role
    if not result["contact"]["title"] and result["experiences"]:
        result["contact"]["title"] = result["experiences"][0].get("role", "")

    return result


def _clean_latex(text: str) -> str:
    """Remove common LaTeX commands from text, keeping content."""
    text = re.sub(r'\\textbf\{([^}]*)\}', r'\1', text)
    text = re.sub(r'\\textit\{([^}]*)\}', r'\1', text)
    text = re.sub(r'\\texttt\{([^}]*)\}', r'\1', text)
    text = re.sub(r'\\emph\{([^}]*)\}', r'\1', text)
    text = re.sub(r'\\(?:small|footnotesize|large|Large|LARGE|Huge|huge|normalsize|tiny|scriptsize)\b\s*', '', text)
    text = re.sub(r'\\(?:bfseries|itshape|scshape|mdseries|upshape)\b\s*', '', text)
    text = re.sub(r'\\(?:noindent|vspace|hspace|hfill|quad|qquad)\s*(?:\{[^}]*\})?\s*', ' ', text)
    text = re.sub(r'\\color\{[^}]*\}', '', text)
    text = re.sub(r'\\href\{[^}]*\}\{([^}]*)\}', r'\1', text)
    text = re.sub(r'\\\\', ' ', text)
    text = re.sub(r'\\item\s*', '', text)
    text = re.sub(r'\\begin\{[^}]*\}', '', text)
    text = re.sub(r'\\end\{[^}]*\}', '', text)
    text = re.sub(r'\\[a-zA-Z]+\*?\s*(?:\[[^\]]*\])?\s*', '', text)
    text = re.sub(r'[{}]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def _extract_experiences(content: str) -> List[Dict]:
    experiences = []
    # Split by \textbf patterns (typically role or company headers)
    blocks = re.split(r'(?=\\(?:textbf|noindent)\s*\{)', content)

    current_exp = None
    for block in blocks:
        block = block.strip()
        if not block:
            continue

        # Try to extract role and company
        role_match = re.search(r'\\textbf\{([^}]+)\}', block)
        if not role_match:
            continue

        first_bold = _clean_latex(role_match.group(1)).strip()

        # Find dates
        date_match = re.search(
            r'((?:Jan|Fév|Mar|Avr|Mai|Juin|Juil|Août|Sep|Oct|Nov|Déc|Janv|Sept)[a-zéû.]*\s*\d{4}|'
            r'\d{4})\s*(?:--?|–|à)\s*((?:Jan|Fév|Mar|Avr|Mai|Juin|Juil|Août|Sep|Oct|Nov|Déc|Janv|Sept)[a-zéû.]*\s*\d{4}|'
            r'\d{4}|Présent|présent|Aujourd|Present)',
            block
        )
        start_date = date_match.group(1).strip() if date_match else ""
        end_date = date_match.group(2).strip() if date_match else "Présent"

        # Find second bold (company) or italic
        all_bolds = re.findall(r'\\textbf\{([^}]+)\}', block)
        company_match = re.search(r'\\textit\{([^}]+)\}', block)

        role = first_bold
        company = ""
        if len(all_bolds) > 1:
            company = _clean_latex(all_bolds[1])
        elif company_match:
            company = _clean_latex(company_match.group(1))

        # Extract bullet points (highlights)
        highlights = []
        items = re.findall(r'\\item\s+(.*?)(?=\\item|\\end|$)', block, re.DOTALL)
        for item in items:
            cleaned = _clean_latex(item).strip()
            if cleaned and len(cleaned) > 5:
                highlights.append(cleaned)

        # Extract technologies
        tech_match = re.search(r'(?:Technologies?|Tech|Stack|Outils)\s*:?\s*(.+?)(?:\n|$)', block, re.IGNORECASE)
        technologies = []
        if tech_match:
            tech_str = _clean_latex(tech_match.group(1))
            technologies = [t.strip() for t in re.split(r'[,·•|]', tech_str) if t.strip()]

        if role or company:
            experiences.append({
                "id": f"exp-import-{len(experiences)}",
                "role": role,
                "company": company,
                "location": "",
                "start_date": start_date,
                "end_date": end_date,
                "highlights": highlights,
                "technologies": technologies,
            })

    return experiences


def _extract_education(content: str) -> List[Dict]:
    education = []
    blocks = re.split(r'(?=\\(?:textbf|noindent)\s*\{)', content)

    for block in blocks:
        block = block.strip()
        if not block:
            continue

        bold_match = re.search(r'\\textbf\{([^}]+)\}', block)
        if not bold_match:
            continue

        degree = _clean_latex(bold_match.group(1)).strip()
        italic_match = re.search(r'\\textit\{([^}]+)\}', block)
        institution = _clean_latex(italic_match.group(1)).strip() if italic_match else ""

        year_match = re.search(r'(\d{4})\s*(?:--?|–)?\s*(\d{4})?', block)
        year = ""
        if year_match:
            year = year_match.group(0).strip()

        details_items = re.findall(r'\\item\s+(.*?)(?=\\item|\\end|$)', block, re.DOTALL)
        details = _clean_latex(' '.join(details_items)).strip() if details_items else ""

        if degree:
            education.append({
                "id": f"edu-import-{len(education)}",
                "degree": degree,
                "institution": institution,
                "location": "",
                "year": year,
                "details": details,
            })

    return education


def _extract_skills(content: str) -> List[Dict]:
    skill_categories = []

    # Pattern: \item \textbf{Category :} skill1, skill2
    items = re.findall(r'\\item\s+(.*?)(?=\\item|\\end|$)', content, re.DOTALL)
    for item in items:
        cat_match = re.search(r'\\textbf\{([^}]+?)\s*:?\s*\}', item)
        if cat_match:
            cat_name = _clean_latex(cat_match.group(1)).strip().rstrip(':').strip()
            rest = item[cat_match.end():]
            rest_clean = _clean_latex(rest)
            skills = [s.strip() for s in re.split(r'[,·•|$]', rest_clean) if s.strip() and len(s.strip()) > 1]
            if cat_name and skills:
                skill_categories.append({"category": cat_name, "skills": skills})

    # Fallback: if no items found, try to extract from plain text
    if not skill_categories:
        lines = content.strip().splitlines()
        for line in lines:
            clean = _clean_latex(line).strip()
            if ':' in clean:
                parts = clean.split(':', 1)
                cat_name = parts[0].strip()
                skills = [s.strip() for s in re.split(r'[,·•|]', parts[1]) if s.strip() and len(s.strip()) > 1]
                if cat_name and skills:
                    skill_categories.append({"category": cat_name, "skills": skills})

    return skill_categories


def _extract_projects(content: str) -> List[Dict]:
    projects = []
    blocks = re.split(r'(?=\\(?:textbf|noindent)\s*\{)', content)

    for block in blocks:
        block = block.strip()
        if not block:
            continue

        bold_match = re.search(r'\\textbf\{([^}]+)\}', block)
        if not bold_match:
            continue

        name = _clean_latex(bold_match.group(1)).strip()

        link_match = re.search(r'\\href\{([^}]+)\}', block)
        link = link_match.group(1) if link_match else ""

        desc_match = re.search(r'\\textit\{([^}]+)\}', block)
        description = _clean_latex(desc_match.group(1)).strip() if desc_match else ""

        highlights = []
        items = re.findall(r'\\item\s+(.*?)(?=\\item|\\end|$)', block, re.DOTALL)
        for item in items:
            cleaned = _clean_latex(item).strip()
            if cleaned and len(cleaned) > 5:
                highlights.append(cleaned)

        tech_match = re.search(r'(?:Technologies?|Tech|Stack)\s*:?\s*(.+?)(?:\n|$)', block, re.IGNORECASE)
        technologies = []
        if tech_match:
            tech_str = _clean_latex(tech_match.group(1))
            technologies = [t.strip() for t in re.split(r'[,·•|]', tech_str) if t.strip()]

        if name:
            projects.append({
                "id": f"proj-import-{len(projects)}",
                "name": name,
                "description": description,
                "highlights": highlights,
                "technologies": technologies,
                "link": link,
            })

    return projects


def _extract_languages_certs(content: str) -> tuple:
    languages = []
    certifications = []
    clean = _clean_latex(content)

    # Languages
    lang_match = re.search(r'Langues?\s*:?\s*(.+?)(?:Certification|$)', clean, re.IGNORECASE | re.DOTALL)
    if lang_match:
        lang_str = lang_match.group(1).strip()
        # Pattern: "Français (Natif), Anglais (C1)"
        lang_items = re.findall(r'([A-ZÀ-Ö][a-zà-ö]+)\s*\(([^)]+)\)', lang_str)
        for name, level in lang_items:
            languages.append({"name": name.strip(), "level": level.strip()})

    # Certifications
    cert_match = re.search(r'Certifications?\s*:?\s*(.+)', clean, re.IGNORECASE | re.DOTALL)
    if cert_match:
        cert_str = cert_match.group(1).strip()
        certifications = [c.strip() for c in re.split(r'[,\n]', cert_str) if c.strip() and len(c.strip()) > 3]

    return languages, certifications


def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text from a PDF file using pdftotext."""
    try:
        result = subprocess.run(
            ["pdftotext", "-layout", pdf_path, "-"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0:
            raise RuntimeError(f"pdftotext failed: {result.stderr}")
        return result.stdout
    except FileNotFoundError:
        raise RuntimeError("pdftotext is not installed. Install poppler-utils: sudo apt install poppler-utils")


def parse_pdf_text_to_profile(text: str) -> Dict[str, Any]:
    """Parse raw PDF text into a structured profile. Best-effort heuristic."""
    result = {
        "contact": {
            "full_name": "",
            "title": "",
            "email": "",
            "phone": "",
            "location": "",
            "linkedin": "",
            "github": "",
            "website": "",
        },
        "summary": "",
        "experiences": [],
        "education": [],
        "projects": [],
        "skill_categories": [],
        "languages": [],
        "certifications": [],
    }

    lines = [l.strip() for l in text.splitlines() if l.strip()]
    if not lines:
        return result

    # Name is typically the first significant line
    for line in lines[:5]:
        if len(line) > 3 and not re.match(r'^[\d\s+@.()/\-]+$', line) and '@' not in line:
            result["contact"]["full_name"] = line.strip()
            break

    # Email
    email_m = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
    if email_m:
        result["contact"]["email"] = email_m.group(0)

    # Phone
    phone_m = re.search(r'(?:\+\d{1,3}[\s\-]?)?(?:\(?\d{1,4}\)?[\s\-]?)?[\d\s\-]{7,15}', text)
    if phone_m:
        candidate = phone_m.group(0).strip()
        digits_only = re.sub(r'\D', '', candidate)
        if 7 <= len(digits_only) <= 15:
            result["contact"]["phone"] = candidate

    # LinkedIn
    li_m = re.search(r'linkedin\.com/in/[^\s,]+', text, re.IGNORECASE)
    if li_m:
        result["contact"]["linkedin"] = li_m.group(0)

    # GitHub
    gh_m = re.search(r'github\.com/[^\s,]+', text, re.IGNORECASE)
    if gh_m:
        result["contact"]["github"] = gh_m.group(0)

    # Location
    loc_patterns = [
        r'(Paris|Lyon|Marseille|Toulouse|Bordeaux|Lille|Strasbourg|Nantes|Nice|Montpellier|Rennes)[^,\n]{0,20}(?:France)?',
    ]
    for pat in loc_patterns:
        loc_m = re.search(pat, text, re.IGNORECASE)
        if loc_m:
            result["contact"]["location"] = loc_m.group(0).strip().rstrip(',').strip()
            break

    # Section-based extraction via common headings
    section_keywords = {
        "summary": ["profil", "résumé", "objectif", "about", "accroche", "summary"],
        "experiences": ["expérience", "experience", "parcours professionnel", "emploi"],
        "education": ["formation", "education", "études", "diplôme"],
        "skills": ["compétence", "skill", "technique", "technologie"],
        "projects": ["projet", "project", "réalisation"],
        "languages": ["langue", "language", "certification", "divers", "autre"],
    }

    # Find section boundaries
    section_starts = []
    full_text_lower = text.lower()
    for line_idx, line in enumerate(lines):
        line_lower = line.lower().strip()
        for sec_type, keywords in section_keywords.items():
            if any(kw in line_lower for kw in keywords) and len(line) < 60:
                section_starts.append((line_idx, sec_type, line))
                break

    for s_idx, (line_idx, sec_type, sec_title) in enumerate(section_starts):
        end_idx = section_starts[s_idx + 1][0] if s_idx + 1 < len(section_starts) else len(lines)
        sec_lines = lines[line_idx + 1:end_idx]
        sec_content = '\n'.join(sec_lines)

        if sec_type == "summary":
            result["summary"] = ' '.join(sec_lines).strip()

        elif sec_type == "skills":
            for sl in sec_lines:
                if ':' in sl:
                    parts = sl.split(':', 1)
                    cat_name = parts[0].strip()
                    skills_list = [s.strip() for s in re.split(r'[,·•|]', parts[1]) if s.strip() and len(s.strip()) > 1]
                    if cat_name and skills_list:
                        result["skill_categories"].append({"category": cat_name, "skills": skills_list})

        elif sec_type == "languages":
            lang_items = re.findall(r'([A-ZÀ-Ö][a-zà-ö]+)\s*[\(:]?\s*([^),\n]+)', sec_content)
            for name, level in lang_items:
                if name.lower() not in ['certification', 'certifications', 'autre']:
                    result["languages"].append({"name": name.strip(), "level": level.strip().rstrip(')')})

    # If we only extracted name and email, add raw text as summary for manual editing
    if not result["summary"] and not result["experiences"] and not result["skill_categories"]:
        result["summary"] = "Profil importé depuis un PDF. Veuillez compléter les sections manuellement.\n\n" + text[:500]

    return result
