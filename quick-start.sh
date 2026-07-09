#!/usr/bin/env bash
set -euo pipefail

# Quick Start — AI Workstation Environment
# Este script verifica y opcionalmente inicia todos los servicios

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROXY_SCRIPT="$SCRIPT_DIR/components/ai-proxy/start.sh"

echo "╔══════════════════════════════════════════════════════════╗"
echo "║       AI Workstation Environment — Quick Start         ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

check_service() {
    local name=$1
    local port=$2
    if curl -s "http://localhost:$port" > /dev/null 2>&1 || \
       curl -s "http://localhost:$port/health" > /dev/null 2>&1; then
        echo -e "  ${GREEN}✓${NC} $name (puerto $port)"
        return 0
    else
        echo -e "  ${RED}✗${NC} $name (puerto $port)"
        return 1
    fi
}

echo "📊 Estado de Servicios:"
echo ""

# Check Docker containers
echo "Docker Containers:"
docker ps --format "  {{.Names}}: {{.Status}}" 2>/dev/null | grep "awe-" || echo "  No hay contenedores running"
echo ""

# Check main services
echo "Servicios Principales:"
check_service "AI Proxy" 8090
check_service "LiteLLM" 4000
check_service "Ollama" 11434
check_service "n8n" 5678
check_service "Redis" 6380
echo ""

# Check CLIs
echo "Herramientas CLI:"
if command -v mimo &> /dev/null; then
    echo -e "  ${GREEN}✓${NC} MiMo $(mimo --version 2>/dev/null || echo 'instalado')"
else
    echo -e "  ${RED}✗${NC} MiMo no encontrado"
fi

if command -v claude &> /dev/null; then
    echo -e "  ${GREEN}✓${NC} Claude $(claude --version 2>/dev/null || echo 'instalado')"
else
    echo -e "  ${RED}✗${NC} Claude no encontrado"
fi
echo ""

# Ask to start proxy if not running
if ! lsof -ti:8090 > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠${NC} AI Proxy no está corriendo"
    read -p "¿Deseas iniciarlo? (s/n): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Ss]$ ]]; then
        echo "Iniciando AI Proxy..."
        bash "$PROXY_SCRIPT" start
    fi
else
    echo -e "${GREEN}✓${NC} AI Proxy está corriendo"
fi

echo ""
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "🚀 ¿Qué deseas hacer?"
echo ""
echo "  1. Usar Terax como terminal AI"
echo "  2. Usar MiMo directamente"
echo "  3. Usar Claude Code"
echo "  4. Hacer una prueba HTTP"
echo "  5. Ver guía completa"
echo "  6. Salir"
echo ""
read -p "Selecciona una opción (1-6): " choice

case $choice in
    1)
        echo ""
        echo "📌 Para usar Terax con el proxy:"
        echo "   1. Abre Terax"
        echo "   2. Presiona Ctrl+, para Settings"
        echo "   3. Agrega un provider:"
        echo "      - Name: AI Proxy"
        echo "      - URL: http://localhost:8090"
        echo "      - API Key: (dejar vacío)"
        echo "   4. Selecciona el provider y escribe tu prompt"
        echo ""
        echo "¿Deseas abrir Terax? (s/n)"
        read -p "> " -n 1 -r
        if [[ $REPLY =~ ^[Ss]$ ]]; then
            terax &
        fi
        ;;
    2)
        echo ""
        echo "📌 Para usar MiMo:"
        echo "   Ejecuta: mimo"
        echo ""
        echo "¿Deseas iniciar MiMo? (s/n)"
        read -p "> " -n 1 -r
        if [[ $REPLY =~ ^[Ss]$ ]]; then
            mimo
        fi
        ;;
    3)
        echo ""
        echo "📌 Para usar Claude:"
        echo "   1. Asegúrate de estar logueado: claude login"
        echo "   2. Ejecuta: claude"
        echo ""
        echo "¿Deseas iniciar Claude? (s/n)"
        read -p "> " -n 1 -r
        if [[ $REPLY =~ ^[Ss]$ ]]; then
            claude
        fi
        ;;
    4)
        echo ""
        echo "📌 Probando AI Proxy..."
        echo ""
        echo "Con MiMo:"
        curl -s -X POST http://localhost:8090/v1/chat/completions \
          -H "Content-Type: application/json" \
          -d '{"model":"mimo-auto","messages":[{"role":"user","content":"di hola"}],"max_tokens":50}' | \
          python3 -c "import json,sys; d=json.load(sys.stdin); print(f'Respuesta: {d[\"choices\"][0][\"message\"][\"content\"]}')"
        echo ""
        echo "Con Claude:"
        curl -s -X POST http://localhost:8090/v1/chat/completions \
          -H "Content-Type: application/json" \
          -d '{"model":"claude","messages":[{"role":"user","content":"di hola"}],"max_tokens":50}' | \
          python3 -c "import json,sys; d=json.load(sys.stdin); print(f'Respuesta: {d[\"choices\"][0][\"message\"][\"content\"]}')"
        ;;
    5)
        echo ""
        echo "📖 Abriendo guía completa..."
        if command -v xdg-open &> /dev/null; then
            xdg-open "$SCRIPT_DIR/docs/WORKFLOW-GUIDE.md"
        elif command -v open &> /dev/null; then
            open "$SCRIPT_DIR/docs/WORKFLOW-GUIDE.md"
        else
            cat "$SCRIPT_DIR/docs/WORKFLOW-GUIDE.md"
        fi
        ;;
    6)
        echo ""
        echo "👋 ¡Hasta luego!"
        exit 0
        ;;
    *)
        echo ""
        echo "❌ Opción no válida"
        ;;
esac
