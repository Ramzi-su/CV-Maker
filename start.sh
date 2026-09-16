#!/usr/bin/env bash
set -e

# Couleurs pour le terminal
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo -e "${BLUE}======================================================${NC}"
echo -e "${BLUE}        Démarrage de CV-Maker (React + LaTeX)        ${NC}"
echo -e "${BLUE}======================================================${NC}"

# 1. Vérification & Préparation Backend
echo -e "\n${YELLOW}[1/3] Vérification du backend Python...${NC}"
cd "$ROOT_DIR/backend"

if [ ! -d ".venv" ]; then
    echo "Création de l'environnement virtuel Python..."
    python3 -m venv .venv
fi

source .venv/bin/activate
pip install -q -r requirements.txt

# 2. Vérification & Préparation Frontend
echo -e "\n${YELLOW}[2/3] Vérification du frontend React...${NC}"
cd "$ROOT_DIR/frontend"

if [ ! -d "node_modules" ]; then
    echo "Installation des dépendances npm..."
    npm install
fi

# 3. Lancement des serveurs
echo -e "\n${YELLOW}[3/3] Lancement des services...${NC}"

# Gestion de l'arrêt propre des sous-processus
cleanup() {
    echo -e "\n${YELLOW}Arrêt des serveurs CV-Maker...${NC}"
    kill $(jobs -p) 2>/dev/null || true
    exit 0
}
trap cleanup SIGINT SIGTERM EXIT

# Démarrage Backend
cd "$ROOT_DIR/backend"
.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000 &
BACKEND_PID=$!

# Démarrage Frontend
cd "$ROOT_DIR/frontend"
npm run dev -- --host 127.0.0.1 --port 5173 &
FRONTEND_PID=$!

sleep 2

echo -e "\n${GREEN}======================================================${NC}"
echo -e "${GREEN} CV-Maker est prêt !${NC}"
echo -e "${GREEN} - Application Web React : ${BLUE}http://localhost:5173${NC}"
echo -e "${GREEN} - Documentation API     : ${BLUE}http://localhost:8000/docs${NC}"
echo -e "${GREEN}======================================================${NC}"
echo -e "Appuyez sur Ctrl+C pour arrêter les serveurs.\n"

wait
