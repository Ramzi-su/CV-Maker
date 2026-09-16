from typing import List, Optional
from pydantic import BaseModel, Field


class ContactInfo(BaseModel):
    full_name: str = Field(..., description="Nom et prénom")
    title: str = Field(default="", description="Titre professionnel")
    email: str = Field(..., description="Adresse email")
    phone: Optional[str] = Field(default="", description="Numéro de téléphone")
    location: Optional[str] = Field(default="", description="Ville, Pays")
    linkedin: Optional[str] = Field(default="", description="URL ou pseudo LinkedIn")
    github: Optional[str] = Field(default="", description="URL ou pseudo GitHub")
    website: Optional[str] = Field(default="", description="Site personnel ou portfolio")


class Experience(BaseModel):
    id: Optional[str] = None
    role: str = Field(..., description="Intitulé du poste")
    company: str = Field(..., description="Nom de l'entreprise")
    location: Optional[str] = Field(default="", description="Lieu")
    start_date: str = Field(..., description="Date de début (ex: Jan 2023)")
    end_date: str = Field(default="Présent", description="Date de fin ou Présent")
    highlights: List[str] = Field(default_factory=list, description="Points clés et réalisations")
    technologies: List[str] = Field(default_factory=list, description="Technologies utilisées")


class Education(BaseModel):
    id: Optional[str] = None
    degree: str = Field(..., description="Diplôme ou titre de formation")
    institution: str = Field(..., description="Établissement")
    location: Optional[str] = Field(default="", description="Lieu")
    year: str = Field(..., description="Année ou période (ex: 2021 - 2024)")
    details: Optional[str] = Field(default="", description="Mention, spécialité ou détails")


class Project(BaseModel):
    id: Optional[str] = None
    name: str = Field(..., description="Nom du projet")
    description: str = Field(default="", description="Brève description")
    highlights: List[str] = Field(default_factory=list, description="Fonctionnalités ou résultats")
    technologies: List[str] = Field(default_factory=list, description="Technologies")
    link: Optional[str] = Field(default="", description="Lien (URL)")


class SkillCategory(BaseModel):
    category: str = Field(..., description="Nom de la catégorie (ex: Langages, Outils)")
    skills: List[str] = Field(default_factory=list, description="Liste des compétences")


class Language(BaseModel):
    name: str = Field(..., description="Langue")
    level: str = Field(default="Courant", description="Niveau (ex: Natif, B2, C1)")


class Profile(BaseModel):
    contact: ContactInfo
    summary: str = Field(default="", description="Résumé professionnel global")
    experiences: List[Experience] = Field(default_factory=list)
    education: List[Education] = Field(default_factory=list)
    projects: List[Project] = Field(default_factory=list)
    skill_categories: List[SkillCategory] = Field(default_factory=list)
    languages: List[Language] = Field(default_factory=list)
    certifications: List[str] = Field(default_factory=list)


class JobOffer(BaseModel):
    title: str = Field(default="Poste Cible", description="Titre du poste ciblé")
    company: Optional[str] = Field(default="", description="Entreprise")
    raw_text: str = Field(..., description="Texte brut de l'annonce")
    extracted_keywords: List[str] = Field(default_factory=list)
    extracted_skills: List[str] = Field(default_factory=list)


class TailoredCV(BaseModel):
    target_role: str = Field(..., description="Titre adapté au poste")
    summary: str = Field(..., description="Accroche personnalisée")
    experiences: List[Experience] = Field(default_factory=list)
    projects: List[Project] = Field(default_factory=list)
    skill_categories: List[SkillCategory] = Field(default_factory=list)
    education: List[Education] = Field(default_factory=list)
    languages: List[Language] = Field(default_factory=list)
    certifications: List[str] = Field(default_factory=list)
    matching_score: Optional[int] = Field(default=85, description="Score de pertinence estimé (%)")
    key_adaptations: List[str] = Field(default_factory=list, description="Résumé des optimisations apportées")


class TailorRequest(BaseModel):
    profile: Profile
    job_text: str
    provider: str = Field(default="heuristic", description="gemini | openai | ollama | heuristic")
    api_key: Optional[str] = None
    model_name: Optional[str] = None
    ollama_url: Optional[str] = "http://localhost:11434"


class ExtractLatexRequest(BaseModel):
    latex_code: str
    provider: str = Field(default="heuristic", description="gemini | openai | ollama | heuristic")
    api_key: Optional[str] = None
    model_name: Optional[str] = None
    ollama_url: Optional[str] = "http://localhost:11434"


class GenerateRequest(BaseModel):
    profile: Optional[Profile] = None
    tailored_cv: Optional[TailoredCV] = None
    template: str = Field(default="modern", description="modern | classic | minimalist")
