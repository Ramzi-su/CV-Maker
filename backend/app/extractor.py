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
    all_lines = [l.strip() for l in text.splitlines()]  # preserve blank lines for block splitting
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
        r'(Paris|Lyon|Marseille|Toulouse|Bordeaux|Lille|Strasbourg|Nantes|Nice|Montpellier|Rennes|'
        r'Grenoble|Toulon|Dijon|Angers|Brest|Limoges|Tours|Clermont|Rouen|Metz|Besançon|Orléans|'
        r'Mulhouse|Caen|Perpignan|Amiens|Reims|Poitiers|Béziers|Saint-Étienne|Avignon|'
        r'Casablanca|Rabat|Tunis|Alger|Bruxelles|Genève|Lausanne|Zurich|Montréal|Québec|Toronto|'
        r'London|Berlin|Amsterdam|Dubai|Riyadh)[^,\n]{0,30}(?:,?\s*(?:France|Algérie|Maroc|Tunisie|'
        r'Belgique|Suisse|Canada|UK|Germany|Netherlands|UAE|KSA))?',
        r'\b(?:France|Algérie|Maroc|Tunisie|Belgique|Suisse|Canada)\b',
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
        "education": ["formation", "education", "études", "diplôme", "académique", "cursus", "scolarité"],
        "skills": ["compétence", "competence", "skill", "compétences techniques"],
        "projects": ["projet", "project", "réalisation", "portfolio"],
        "languages": ["langues", "languages"],
        "certifications": ["certification", "certif", "accréditation"],
        "divers": ["divers", "autre", "intérêt", "loisir", "hobby"],
    }

    # Build a mapping from stripped-line index to all_lines index
    stripped_to_all = []
    for all_idx, al in enumerate(all_lines):
        if al.strip():
            stripped_to_all.append(all_idx)

    # Find section boundaries (using stripped lines for detection)
    section_starts = []
    for line_idx, line in enumerate(lines):
        line_lower = line.lower().strip()
        if len(line) > 80 or len(line) < 3:
            continue
        is_likely_header = (
            len(line) < 60
            and not re.match(r'^\s*[-•–◦▪✓►➤→]', line)
            and '@' not in line
            and not re.match(r'^\d{4}', line)
            and not re.match(r'^.+:\s+\S+.*\S', line)
            and '|' not in line
            and not re.search(r'\([^)]{3,}\)', line)
        )
        if not is_likely_header:
            continue
        for sec_type, keywords in section_keywords.items():
            if any(kw in line_lower for kw in keywords):
                section_starts.append((line_idx, sec_type, line))
                break

    for s_idx, (line_idx, sec_type, sec_title) in enumerate(section_starts):
        end_idx = section_starts[s_idx + 1][0] if s_idx + 1 < len(section_starts) else len(lines)
        # Map stripped indices back to all_lines to preserve blank line separators
        all_start = stripped_to_all[line_idx] + 1 if line_idx < len(stripped_to_all) else 0
        all_end = stripped_to_all[end_idx] if end_idx < len(stripped_to_all) else len(all_lines)
        sec_lines = all_lines[all_start:all_end]
        sec_content = '\n'.join(sec_lines)

        if sec_type == "summary":
            result["summary"] = ' '.join(l for l in sec_lines if l.strip()).strip()

        elif sec_type == "experiences":
            result["experiences"] = _parse_pdf_experiences(sec_lines)

        elif sec_type == "education":
            result["education"] = _parse_pdf_education(sec_lines)

        elif sec_type == "projects":
            result["projects"] = _parse_pdf_projects(sec_lines)

        elif sec_type == "skills":
            for sl in sec_lines:
                if ':' in sl:
                    parts = sl.split(':', 1)
                    cat_name = parts[0].strip()
                    skills_list = [s.strip() for s in re.split(r'[,·•|/]', parts[1]) if s.strip() and len(s.strip()) > 1]
                    if cat_name and skills_list:
                        result["skill_categories"].append({"category": cat_name, "skills": skills_list})
                elif re.match(r'^[-•–◦▪]\s*', sl):
                    skill_text = re.sub(r'^[-•–◦▪]\s*', '', sl).strip()
                    if skill_text:
                        if result["skill_categories"]:
                            result["skill_categories"][-1]["skills"].append(skill_text)
                        else:
                            result["skill_categories"].append({"category": "Compétences", "skills": [skill_text]})

        elif sec_type == "languages":
            lang_items = re.findall(r'([A-ZÀ-Öa-zà-ö]+)\s*[\(:\-–]?\s*([^),\n]+)', sec_content)
            for name, level in lang_items:
                name_clean = name.strip()
                level_clean = level.strip().rstrip(')').strip()
                if name_clean.lower() not in ['certification', 'certifications', 'autre', 'divers', ''] and len(name_clean) > 1:
                    result["languages"].append({"name": name_clean, "level": level_clean})

        elif sec_type == "certifications":
            for sl in sec_lines:
                cleaned = re.sub(r'^[-•–◦▪]\s*', '', sl).strip()
                if cleaned and len(cleaned) > 3:
                    result["certifications"].append(cleaned)

    # Website
    web_m = re.search(r'https?://(?!linkedin|github)[^\s,}]+', text, re.IGNORECASE)
    if web_m:
        result["contact"]["website"] = web_m.group(0).rstrip('.')

    # Title: try the line right after the name in the first few lines
    if not result["contact"]["title"]:
        name = result["contact"]["full_name"]
        for idx, line in enumerate(lines[:8]):
            if line.strip() == name:
                for next_line in lines[idx + 1:idx + 3]:
                    next_clean = next_line.strip()
                    if next_clean and '@' not in next_clean and not re.match(r'^[\d\s+\-()/]+$', next_clean) and len(next_clean) < 80:
                        if not re.search(r'linkedin|github|http', next_clean, re.IGNORECASE):
                            result["contact"]["title"] = next_clean
                            break
                break

    # Fallback title from first experience role
    if not result["contact"]["title"] and result["experiences"]:
        result["contact"]["title"] = result["experiences"][0].get("role", "")

    # If we only extracted name and email, add raw text as summary for manual editing
    if not result["summary"] and not result["experiences"] and not result["skill_categories"]:
        result["summary"] = "Profil importé depuis un PDF. Veuillez compléter les sections manuellement.\n\n" + text[:500]

    return result


# --- Date pattern constant for reuse ---
_DATE_PATTERN = (
    r'(?:(?:Janv?\.?|Févr?\.?|Mars?|Avr\.?|Mai|Juin|Juil\.?|Août|Sept?\.?|Oct\.?|Nov\.?|Déc\.?|'
    r'January?|February?|March?|April?|May|June?|July?|August?|Septemb(?:er|re)?|Octob(?:er|re)?|'
    r'Novemb(?:er|re)?|Decemb(?:er|re)?|Décemb(?:er|re)?)\s*\.?\s*\d{4}|\d{4})'
)
_DATE_RANGE_PATTERN = (
    _DATE_PATTERN + r'\s*(?:[-–—]|à)\s*(?:' + _DATE_PATTERN + r'|[Pp]résent|[Pp]resent|[Aa]ujourd)'
)


def _split_into_blocks(lines: List[str]) -> List[List[str]]:
    """Split lines into logical blocks separated by blank lines, then merge orphan headers."""
    raw_blocks = []
    current_block = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            if current_block:
                raw_blocks.append(current_block)
                current_block = []
            continue
        current_block.append(stripped)
    if current_block:
        raw_blocks.append(current_block)

    # Merge: if a block has only 1-2 lines with no bullets and the next block starts with a date,
    # merge them into one entry
    merged = []
    i = 0
    while i < len(raw_blocks):
        block = raw_blocks[i]
        has_bullets = any(re.match(r'^[-•–◦▪✓►➤→]', l) for l in block)
        has_date = any(re.search(_DATE_RANGE_PATTERN, l, re.IGNORECASE) for l in block)

        # Short header block (no date, no bullets) followed by another block
        if not has_bullets and not has_date and len(block) <= 2 and i + 1 < len(raw_blocks):
            next_block = raw_blocks[i + 1]
            next_has_date = any(re.search(_DATE_RANGE_PATTERN, l, re.IGNORECASE) for l in next_block)
            if next_has_date:
                merged.append(block + next_block)
                i += 2
                continue

        merged.append(block)
        i += 1

    return merged


def _extract_date_range(text: str):
    """Extract start_date and end_date from a text string."""
    m = re.search(_DATE_RANGE_PATTERN, text, re.IGNORECASE)
    if m:
        full_match = m.group(0)
        parts = re.split(r'\s*(?:[-–—]|à)\s*', full_match, maxsplit=1)
        start = parts[0].strip() if len(parts) > 0 else ""
        end = parts[1].strip() if len(parts) > 1 else "Présent"
        return start, end, m.start(), m.end()
    # Try single year
    m2 = re.search(r'\b(\d{4})\b', text)
    if m2:
        return m2.group(1), "", m2.start(), m2.end()
    return "", "", -1, -1


def _extract_bullets(lines: List[str]) -> List[str]:
    """Extract bullet points from lines."""
    bullets = []
    for line in lines:
        stripped = line.strip()
        bullet_m = re.match(r'^[-•–◦▪✓►➤→]\s*(.+)', stripped)
        if bullet_m:
            text = bullet_m.group(1).strip()
            if text and len(text) > 5:
                bullets.append(text)
    return bullets


def _extract_technologies_from_text(text: str) -> List[str]:
    """Extract technology keywords from a text block."""
    tech_m = re.search(r'(?:Technologies?|Tech|Stack|Outils|Environnement)\s*:\s*(.+?)(?:\n|$)', text, re.IGNORECASE)
    if tech_m:
        tech_str = tech_m.group(1)
        return [t.strip() for t in re.split(r'[,·•|/]', tech_str) if t.strip() and len(t.strip()) > 1]
    return []


def _parse_pdf_experiences(sec_lines: List[str]) -> List[Dict]:
    """Parse experience entries from plain text lines."""
    experiences = []
    blocks = _split_into_blocks(sec_lines)

    for block in blocks:
        if not block:
            continue
        block_text = '\n'.join(block)

        start_date, end_date, d_start, d_end = _extract_date_range(block_text)

        # The first line (or first two lines) typically contain role and company
        header_lines = []
        bullet_lines = []
        for line in block:
            # Bullet points
            if re.match(r'^[-•–◦▪✓►➤→]\s*', line):
                bullet_lines.append(line)
            # Date-only lines (just a date range on its own line)
            elif re.match(_DATE_RANGE_PATTERN + r'\s*$', line.strip(), re.IGNORECASE):
                continue  # skip, date already extracted from block_text
            # "Technologies : ..." lines go to bullet_lines for tech extraction
            elif re.match(r'^(?:Technologies?|Tech|Stack|Outils|Environnement)\s*:', line, re.IGNORECASE):
                bullet_lines.append(line)
            else:
                if not bullet_lines:
                    header_lines.append(line)
                else:
                    bullet_lines.append(line)

        if not header_lines:
            continue

        # Try to identify role and company from header lines
        role = ""
        company = ""
        location = ""

        # Remove date ranges from header text for cleaner parsing
        header_text = ' | '.join(header_lines)
        header_clean = re.sub(_DATE_RANGE_PATTERN, '', header_text, flags=re.IGNORECASE).strip()
        header_clean = re.sub(r'\s*[|–—-]\s*$', '', header_clean).strip()
        header_clean = re.sub(r'^\s*[|–—-]\s*', '', header_clean).strip()

        # Split by common delimiters: |, –, —, -, comma
        header_parts = re.split(r'\s*[|–—]\s*', header_clean)
        header_parts = [p.strip().strip(',').strip() for p in header_parts if p.strip()]

        if len(header_parts) >= 3:
            role = header_parts[0]
            company = header_parts[1]
            location = header_parts[2]
        elif len(header_parts) == 2:
            role = header_parts[0]
            company = header_parts[1]
        elif len(header_parts) == 1 and header_parts[0]:
            # Single header: might be "Role, Company" or "Role - Company" separated by comma
            comma_parts = [p.strip() for p in header_parts[0].split(',') if p.strip()]
            if len(comma_parts) >= 2:
                role = comma_parts[0]
                company = comma_parts[1]
                if len(comma_parts) >= 3:
                    location = comma_parts[2]
            else:
                role = header_parts[0]

        highlights = _extract_bullets(bullet_lines)
        technologies = _extract_technologies_from_text(block_text)

        if role or company:
            experiences.append({
                "id": f"exp-import-{len(experiences)}",
                "role": role,
                "company": company,
                "location": location,
                "start_date": start_date,
                "end_date": end_date if end_date else "Présent",
                "highlights": highlights,
                "technologies": technologies,
            })

    return experiences


def _parse_pdf_education(sec_lines: List[str]) -> List[Dict]:
    """Parse education entries from plain text lines."""
    education = []
    blocks = _split_into_blocks(sec_lines)

    for block in blocks:
        if not block:
            continue
        block_text = '\n'.join(block)

        start_date, end_date, _, _ = _extract_date_range(block_text)
        year = ""
        if start_date and end_date:
            year = f"{start_date} - {end_date}"
        elif start_date:
            year = start_date

        header_lines = []
        detail_lines = []
        for line in block:
            if re.match(r'^[-•–◦▪✓►➤→]\s*', line):
                detail_lines.append(re.sub(r'^[-•–◦▪✓►➤→]\s*', '', line).strip())
            elif re.match(_DATE_RANGE_PATTERN + r'\s*$', line.strip(), re.IGNORECASE):
                continue
            elif re.match(r'^\d{4}\s*$', line.strip()):
                continue
            elif not detail_lines:
                header_lines.append(line)
            else:
                detail_lines.append(line)

        if not header_lines:
            continue

        header_text = ' | '.join(header_lines)
        header_clean = re.sub(_DATE_RANGE_PATTERN, '', header_text, flags=re.IGNORECASE).strip()
        header_clean = re.sub(r'\b\d{4}\b', '', header_clean).strip()
        header_clean = re.sub(r'\s*[|–—-]\s*$', '', header_clean).strip()
        header_clean = re.sub(r'^\s*[|–—-]\s*', '', header_clean).strip()

        header_parts = re.split(r'\s*[|–—]\s*', header_clean)
        header_parts = [p.strip().strip(',').strip() for p in header_parts if p.strip()]

        degree = ""
        institution = ""
        location = ""

        if len(header_parts) >= 3:
            degree = header_parts[0]
            institution = header_parts[1]
            location = header_parts[2]
        elif len(header_parts) == 2:
            degree = header_parts[0]
            institution = header_parts[1]
        elif len(header_parts) == 1 and header_parts[0]:
            comma_parts = [p.strip() for p in header_parts[0].split(',') if p.strip()]
            if len(comma_parts) >= 2:
                degree = comma_parts[0]
                institution = comma_parts[1]
                if len(comma_parts) >= 3:
                    location = comma_parts[2]
            else:
                degree = header_parts[0]

        details = ' '.join(detail_lines).strip() if detail_lines else ""

        if degree or institution:
            education.append({
                "id": f"edu-import-{len(education)}",
                "degree": degree,
                "institution": institution,
                "location": location,
                "year": year,
                "details": details,
            })

    return education


def _parse_pdf_projects(sec_lines: List[str]) -> List[Dict]:
    """Parse project entries from plain text lines."""
    projects = []
    blocks = _split_into_blocks(sec_lines)

    for block in blocks:
        if not block:
            continue
        block_text = '\n'.join(block)

        header_lines = []
        bullet_lines = []
        for line in block:
            if re.match(r'^[-•–◦▪✓►➤→]\s*', line):
                bullet_lines.append(line)
            elif not bullet_lines:
                header_lines.append(line)
            else:
                bullet_lines.append(line)

        if not header_lines:
            continue

        name = header_lines[0].strip()
        # Remove date from name if present
        name = re.sub(_DATE_RANGE_PATTERN, '', name, flags=re.IGNORECASE).strip()
        name = name.strip('|–—- ,')

        # Description from remaining header lines
        description = ' '.join(header_lines[1:]).strip() if len(header_lines) > 1 else ""

        # Link
        link_m = re.search(r'(https?://[^\s,)]+)', block_text)
        link = link_m.group(1).rstrip('.') if link_m else ""

        highlights = _extract_bullets(bullet_lines)
        technologies = _extract_technologies_from_text(block_text)

        if name and len(name) > 2:
            projects.append({
                "id": f"proj-import-{len(projects)}",
                "name": name,
                "description": description,
                "highlights": highlights,
                "technologies": technologies,
                "link": link,
            })

    return projects
