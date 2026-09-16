export const DEFAULT_PROFILE = {
  contact: {
    full_name: "Ramzi Moulahi",
    title: "Cybersecurity Software Engineer",
    email: "ramzimoulahi.x@gmail.com",
    phone: "+33 6 12 34 56 78",
    location: "Paris, France",
    linkedin: "linkedin.com/in/ramzi-moulahi",
    github: "github.com/Ramzi-su",
    website: "https://portofolio-gold-nu.vercel.app/",
  },
  summary: "Ingénieur logiciel passionné par l'architecture logicielle, le développement full-stack moderne et l'intégration de solutions d'IA. Rigoureux et orienté impact, doté d'une forte expérience en Python, React, conteneurisation Docker et automatisation CI/CD.",
  experiences: [
    {
      id: "exp-1",
      role: "Ingénieur Logiciel & IA Full-Stack",
      company: "TechNova Solutions",
      location: "Paris, France",
      start_date: "Janv. 2024",
      end_date: "Présent",
      highlights: [
        "Conception et déploiement d'architectures microservices résilientes avec FastAPI, React et PostgreSQL.",
        "Intégration d'agents LLM autonomes et de pipelines RAG réduisant le temps de traitement documentaire de 40%.",
        "Mise en place de pipelines CI/CD automatisés sous GitLab CI et Docker, assurant des déploiements sans interruption.",
      ],
      technologies: ["Python", "FastAPI", "React", "Docker", "PostgreSQL", "GitLab CI"],
    },
    {
      id: "exp-2",
      role: "Développeur Backend Python",
      company: "CloudData Labs",
      location: "Lyon, France",
      start_date: "Sept. 2022",
      end_date: "Déc. 2023",
      highlights: [
        "Développement d'APIs REST haute performance et optimisation de requêtes SQL complexes traitant plus de 500k requêtes/jour.",
        "Mise en place de tests unitaires et d'intégration atteignant une couverture de code supérieure à 90%.",
        "Automatisation de tâches d'extraction et d'analyse de données avec Celery et Redis.",
      ],
      technologies: ["Python", "Django", "Redis", "PostgreSQL", "Docker", "Linux"],
    },
  ],
  projects: [
    {
      id: "proj-1",
      name: "CV-Maker Intelligent",
      description: "Application d'adaptation automatique de CV en LaTeX/PDF ciblant les critères ATS des offres d'emploi.",
      highlights: [
        "Interface intuitive en React JS et moteur d'analyse sémantique sous FastAPI.",
        "Compilation dynamique et sécurisée en LaTeX sans erreur de syntaxe.",
      ],
      technologies: ["React", "FastAPI", "LaTeX", "Python", "TailwindCSS"],
      link: "https://github.com/Ramzi-su/cv-maker",
    },
    {
      id: "proj-2",
      name: "AI Code Security Scanner",
      description: "Outil d'audit automatique de code source détectant les vulnérabilités OWASP Top 10.",
      highlights: [
        "Analyse statique AST et détection assistée par LLM avec reporting automatisé.",
      ],
      technologies: ["Python", "Cybersecurity", "Docker", "AST"],
      link: "https://github.com/Ramzi-su/ai-security",
    },
  ],
  skill_categories: [
    {
      category: "Langages",
      skills: ["Python", "JavaScript", "TypeScript", "SQL", "Bash", "C++"],
    },
    {
      category: "Frameworks & Frontend",
      skills: ["React.js", "FastAPI", "Django", "Node.js", "Tailwind CSS", "HTML5/CSS3"],
    },
    {
      category: "DevOps & Cloud",
      skills: ["Docker", "Kubernetes", "CI/CD", "Git / GitHub", "Linux (Ubuntu, Debian)", "LaTeX"],
    },
    {
      category: "Données & IA",
      skills: ["PostgreSQL", "Redis", "MongoDB", "LLMs & RAG", "RESTful APIs"],
    },
  ],
  education: [
    {
      id: "edu-1",
      degree: "Master en Informatique & Génie Logiciel",
      institution: "Université de Technologie",
      location: "Paris, France",
      year: "2022 - 2024",
      details: "Mention Très Bien -- Spécialisation Architectures Distribuées et Systèmes Intelligents",
    },
    {
      id: "edu-2",
      degree: "Licence en Informatique Fondamentale",
      institution: "Faculté des Sciences",
      location: "France",
      year: "2019 - 2022",
      details: "Algorithmique, Structures de Données, Systèmes d'Exploitation et Réseaux",
    },
  ],
  languages: [
    { name: "Français", level: "Natif / Bilingue" },
    { name: "Anglais", level: "Professionnel courant (C1)" },
    { name: "Arabe", level: "Langue maternelle" },
  ],
  certifications: [
    "HashiCorp Certified: Terraform Associate",
    "Docker Certified Associate (DCA)",
  ],
};

export const DEFAULT_JOB_TEXT = `Offre d'emploi : Ingénieur Full-Stack Python & React.js (H/F)
Entreprise : ScaleTech Innovations
Localisation : Paris (Hybride) / Télétravail partiel
Contrat : CDI

À propos du poste :
ScaleTech Innovations est une entreprise en forte croissance développant une plateforme SaaS d'automatisation intelligente pour les entreprises européennes. Nous renforçons notre équipe d'ingénierie et recherchons un(e) Ingénieur(e) Full-Stack passionné(e) pour concevoir et faire évoluer nos applications critiques.

Vos missions :
- Concevoir et implémenter des APIs REST robustes et hautement performantes avec Python et FastAPI.
- Développer des interfaces utilisateurs modernes, réactives et ergonomiques avec React.js et TypeScript.
- Participer à l'architecture technique, aux choix technologiques et aux revues de code rigoureuses.
- Assurer l'intégration continue et le déploiement conteneurisé avec Docker, Kubernetes et GitLab CI.
- Intégrer de nouvelles fonctionnalités basées sur l'intelligence artificielle générative (LLM, agents intelligents) pour booster la productivité de nos clients.
- Collaborer en méthodologie Agile / Scrum avec l'équipe produit.

Profil recherché :
- Titulaire d'un Bac+5 (Diplôme d'Ingénieur ou Master en Informatique).
- Solide maîtrise de Python (FastAPI ou Django) et des architectures microservices.
- Expérience confirmée sur React.js et les outils frontend modernes.
- Bonne pratique de bases de données relationnelles (PostgreSQL) et de cache (Redis).
- Sensibilité forte aux bonnes pratiques DevOps : Docker, CI/CD, environnement Linux.
- Rigueur, esprit d'équipe, curiosité technique et souci de la qualité de code.
- Anglais technique courant requis.`;

export const DEFAULT_TEMPLATES = [
  { id: "modern", name: "Moderne & Épuré", description: "Design sobre, touches de bleu roi, hiérarchie visuelle claire et optimisé ATS." },
  { id: "classic", name: "Classique Corporate", description: "Style intemporel serif, parfait pour les secteurs traditionnels ou académiques." },
  { id: "minimalist", name: "Minimaliste 1-Page", description: "Mise en page compacte et dense conçue pour tenir sur une seule page." },
];
