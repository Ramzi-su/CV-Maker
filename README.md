# CV-Maker 📄🤖

> **Générateur de CV LaTeX & PDF sur-mesure pour offres d'emploi**, doté d'une interface web moderne en **React JS** et d'un moteur d'analyse et de compilation en **Python (FastAPI + pdflatex)**.

---

## ✨ Fonctionnalités Principales

- 🎯 **Ciblage & Pertinence ATS :** Analyse sémantique de l'offre d'emploi cible pour extraire l'intitulé exact, les mots-clés ATS et les compétences prioritaires.
- 🛡️ **Règle d'or Zéro Hallucination :** Valorisation, réordonnancement et reformulation des réalisations du candidat sans jamais inventer d'expériences ou de diplômes inexistants.
- 📐 **Templates LaTeX Professionnels :**
  - `modern` : Moderne, élégant, touches de bleu roi, hiérarchisé et optimisé pour le scanning ATS.
  - `classic` : Style corpo/académique intemporel avec police avec empattement (serif).
  - `minimalist` : Gabarit compact et dense spécialement calibré pour tenir sur 1 seule page.
- ⚡ **Compilateur LaTeX Sécurisé :** Échappement rigoureux des caractères spéciaux (`&`, `%`, `$`, `#`, `_`, `~`, `^`, `C++`, `C#`) garantissant 100% de succès de compilation avec `pdflatex`.
- 🧠 **Flexibilité d'IA :**
  - **Mode Heuristique Local** : 100% Hors-ligne, instantané, sans clé API.
  - **Google Gemini** : `gemini-2.5-flash` haute fidélité.
  - **OpenAI / ChatGPT** : `gpt-4o-mini` ou modèles personnalisés.
  - **Ollama** : Modèles locaux 100% privés et gratuits (`llama3`, `mistral`, `qwen2.5`).
- 💻 **Double Interface :**
  - Interface Web interactive en **React JS**.
  - Script en ligne de commande **CLI** pour les générations rapides ou automatisées.

---

## 🚀 Démarrage Rapide

### Option A : Lancement de l'Application Web Complète (React + FastAPI)

Exécutez simplement le script de démarrage :

```bash
./start.sh
```

Le script s'occupe de tout :
1. Active l'environnement virtuel Python (`.venv`) et installe les dépendances requises.
2. Installe les dépendances npm dans `frontend/` si nécessaire.
3. Démarre le backend FastAPI sur **http://localhost:8000** (Documentation Swagger sur `/docs`).
4. Démarre l'interface React sur **http://localhost:5173**.

---

### Option B : Utilisation en Ligne de Commande (CLI)

Vous pouvez aussi générer un CV directement depuis votre terminal sans ouvrir de navigateur :

```bash
# Avec le profil et l'offre d'exemple (template moderne) :
backend/.venv/bin/python cv_maker_cli.py --template modern

# Avec vos propres fichiers et le template minimaliste 1-page :
backend/.venv/bin/python cv_maker_cli.py \
  --profile mon_profil.yaml \
  --job offre_poste.txt \
  --template minimalist \
  --output-dir output/
```

Options disponibles :
- `--profile`, `-p` : Chemin vers le fichier YAML de profil maître (défaut: `backend/data/sample_profile.yaml`).
- `--job`, `-j` : Fichier texte de la description du poste (défaut: `backend/data/sample_job.txt`).
- `--template`, `-t` : `modern`, `classic`, ou `minimalist` (défaut: `modern`).
- `--provider` : `heuristic`, `gemini`, `openai`, `ollama` (défaut: `heuristic`).
- `--api-key` : Clé API si utilisation d'un provider cloud.
- `--output-dir`, `-o` : Dossier où enregistrer le PDF et le source `.tex` (défaut: `output/`).

---

## 📁 Architecture du Projet

```
CV-Maker/
├── backend/                    # Serveur FastAPI & Moteur de génération LaTeX
│   ├── app/
│   │   ├── main.py             # API REST (FastAPI)
│   │   ├── models.py           # Schémas Pydantic (Profile, JobOffer, TailoredCV)
│   │   ├── latex/
│   │   │   ├── sanitizer.py    # Échappement strict des caractères spéciaux LaTeX
│   │   │   ├── renderer.py     # Rendu Jinja2 avec syntaxe \VAR{} et \BLOCK{}
│   │   │   └── compiler.py     # Pipeline pdflatex & extraction des erreurs
│   │   ├── templates/          # Gabarits LaTeX Jinja2
│   │   │   ├── modern.tex.j2
│   │   │   ├── classic.tex.j2
│   │   │   └── minimalist.tex.j2
│   │   └── ai/                 # Fournisseurs d'adaptation
│   │       ├── heuristic.py    # Mode hors-ligne par matching de compétences
│   │       ├── gemini_client.py# Client Google Gemini
│   │       ├── openai_client.py# Client OpenAI / Groq
│   │       └── ollama_client.py# Client Ollama local
│   ├── data/
│   │   ├── sample_profile.yaml # Profil candidat complet prêt à l'emploi
│   │   └── sample_job.txt      # Fiche de poste d'exemple
│   ├── requirements.txt        # Dépendances Python
│   └── test_backend.py         # Suite de tests automatisés
├── frontend/                   # Interface Utilisateur React JS
│   ├── src/
│   │   ├── components/
│   │   │   ├── ProfileEditor.jsx   # Éditeur du profil maître
│   │   │   ├── JobAnalyzer.jsx     # Analyse de l'offre & déclencheur d'adaptation
│   │   │   ├── ResumePreview.jsx   # Visualiseur PDF & éditeur LaTeX
│   │   │   └── AISettingsModal.jsx # Configuration des modèles d'IA
│   │   ├── services/api.js         # Client API
│   │   ├── App.jsx                 # Application principale
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
├── output/                     # Répertoire où sont enregistrés les PDFs finaux
├── start.sh                    # Script de lancement en 1 clic
├── cv_maker_cli.py             # Outil en ligne de commande
└── README.md
```

---

## 🧪 Exécution des Tests de Compilation

Pour vérifier la validité de la chaîne de compilation pdflatex sur tous les templates :

```bash
backend/.venv/bin/python backend/test_backend.py
```
