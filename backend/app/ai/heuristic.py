import re
from typing import Dict, List, Set, Tuple
from ..models import Profile, TailoredCV, Experience, Project, SkillCategory


COMMON_TECH_PATTERNS = [
    r"\bpython\b", r"\bjavascript\b", r"\btypescript\b", r"\breact(?:\.js)?\b", r"\bvue(?:\.js)?\b",
    r"\bangular\b", r"\bnode(?:\.js)?\b", r"\bfastapi\b", r"\bdjango\b", r"\bflask\b",
    r"\bdocker\b", r"\bkubernetes\b", r"\bk8s\b", r"\baws\b", r"\bazure\b", r"\bgcp\b",
    r"\bci/cd\b", r"\bgit\b", r"\bgithub\b", r"\bsql\b", r"\bpostgresql\b", r"\bmongodb\b",
    r"\bredis\b", r"\blinux\b", r"\bterraform\b", r"\bansible\b", r"\bkafka\b", r"\brabbitmq\b",
    r"\bgraphql\b", r"\brest\b", r"\batex\b", r"\bjava\b", r"\bc\+\+\b", r"\bc#\b",
    r"\bdevops\b", r"\bmachine learning\b", r"\bdeep learning\b", r"\bpentest\b", r"\bcyber\b"
]


def extract_keywords_from_text(text: str) -> Set[str]:
    text_lower = text.lower()
    found = set()
    for pattern in COMMON_TECH_PATTERNS:
        match = re.search(pattern, text_lower)
        if match:
            clean_word = match.group(0).replace(r"\b", "").strip()
            found.add(clean_word)

    # Also extract capitalized tech words and acronyms
    words = re.findall(r"\b[A-Z][a-zA-Z0-9+#\.\-]{2,}\b", text)
    for w in words:
        if len(w) > 2 and w.lower() not in {"pour", "avec", "dans", "nous", "vous", "notre", "votre", "les", "des"}:
            found.add(w.lower())

    return found


def extract_job_title_from_text(text: str) -> str:
    lines = [line.strip() for line in text.strip().splitlines() if line.strip()]
    if not lines:
        return "Ingénieur Développeur"

    first_line = lines[0]
    # Check if first line contains role words
    role_indicators = ["ingénieur", "développeur", "developer", "engineer", "lead", "architecte", "consultant", "stage", "alternance"]
    for ind in role_indicators:
        if ind in first_line.lower():
            return first_line[:60].strip()

    # Look for "poste :", "intitulé :", "titre :"
    for line in lines[:5]:
        m = re.search(r"(?:poste|intitulé|titre|recherche)\s*:\s*(.+)", line, re.IGNORECASE)
        if m:
            return m.group(1).strip()[:60]

    return lines[0][:60]


def tailor_profile_heuristically(profile: Profile, job_text: str) -> TailoredCV:
    job_keywords = extract_keywords_from_text(job_text)
    target_title = extract_job_title_from_text(job_text)

    # 1. Adapt and reorder skills
    tailored_skill_categories: List[SkillCategory] = []
    matched_skills_count = 0
    total_skills_count = 0

    for cat in profile.skill_categories:
        matched = []
        unmatched = []
        for s in cat.skills:
            total_skills_count += 1
            s_clean = s.lower().strip()
            if any(k in s_clean or s_clean in k for k in job_keywords):
                matched.append(s)
                matched_skills_count += 1
            else:
                unmatched.append(s)
        # Prioritize matching skills first in each category
        tailored_skill_categories.append(
            SkillCategory(category=cat.category, skills=matched + unmatched)
        )

    # 2. Adapt experiences and highlight relevant bullet points
    tailored_experiences: List[Experience] = []
    for exp in profile.experiences:
        scored_highlights: List[Tuple[int, str]] = []
        for hl in exp.highlights:
            hl_lower = hl.lower()
            score = sum(1 for kw in job_keywords if kw in hl_lower)
            scored_highlights.append((score, hl))

        # Sort highlights with highest keyword matches first
        scored_highlights.sort(key=lambda x: x[0], reverse=True)
        reordered_highlights = [hl for _, hl in scored_highlights]

        # Prioritize technologies matching the job
        matched_tech = [t for t in exp.technologies if any(k in t.lower() for k in job_keywords)]
        other_tech = [t for t in exp.technologies if t not in matched_tech]

        tailored_experiences.append(
            Experience(
                id=exp.id,
                role=exp.role,
                company=exp.company,
                location=exp.location,
                start_date=exp.start_date,
                end_date=exp.end_date,
                highlights=reordered_highlights,
                technologies=matched_tech + other_tech,
            )
        )

    # 3. Adapt projects
    tailored_projects: List[Project] = []
    for proj in profile.projects:
        matched_tech = [t for t in proj.technologies if any(k in t.lower() for k in job_keywords)]
        other_tech = [t for t in proj.technologies if t not in matched_tech]
        tailored_projects.append(
            Project(
                id=proj.id,
                name=proj.name,
                description=proj.description,
                highlights=proj.highlights,
                technologies=matched_tech + other_tech,
                link=proj.link,
            )
        )

    # 4. Craft tailored summary
    key_matches_str = ", ".join(list(job_keywords)[:5]) if job_keywords else "développement et ingénierie"
    tailored_summary = (
        f"Professionnel passionné ciblant le rôle de {target_title}. "
        f"Fort d'une solide expertise technique ({key_matches_str}) et d'une rigueur démontrée "
        f"dans la conception de solutions performantes, fiables et orientées résultats."
    )
    if profile.summary:
        tailored_summary = f"{profile.summary} Particulièrement aligné avec les exigences du poste de {target_title} ({key_matches_str})."

    # 5. Calculate match score
    score = min(98, max(70, 70 + int((matched_skills_count / max(total_skills_count, 1)) * 30)))

    key_adaptations = [
        f"Alignement du titre professionnel vers : '{target_title}'",
        f"Priorisation des compétences clés correspondant à l'offre ({len(job_keywords)} mots-clés détectés)",
        "Réorganisation des réalisations et des technologies les plus pertinentes en tête de liste",
        "Formulation d'un résumé professionnel ciblant précisément les besoins exprimés dans l'offre",
    ]

    return TailoredCV(
        target_role=target_title,
        summary=tailored_summary,
        experiences=tailored_experiences,
        projects=tailored_projects,
        skill_categories=tailored_skill_categories,
        education=profile.education,
        languages=profile.languages,
        certifications=profile.certifications,
        matching_score=score,
        key_adaptations=key_adaptations,
    )
