#!/bin/bash

# Script para verificar que la aplicación está lista para despliegue en Render
# Uso: bash pre-deploy-check.sh

echo "🔍 PRE-DEPLOYMENT CHECK - ARM CUENTAS"
echo "======================================"
echo ""

ERRORS=0
WARNINGS=0

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Función para imprimir resultado
check() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅${NC} $1"
    else
        echo -e "${RED}❌${NC} $1"
        ((ERRORS++))
    fi
}

check_warn() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅${NC} $1"
    else
        echo -e "${YELLOW}⚠️${NC} $1"
        ((WARNINGS++))
    fi
}

echo "📋 Verificando archivos..."
echo ""

# Archivos críticos
[ -f render.yaml ]
check "render.yaml existe en raíz"

[ -f backend/requirements.txt ]
check "backend/requirements.txt existe"

[ -f backend/app/main.py ]
check "backend/app/main.py existe"

[ -f backend/init_db.py ]
check "backend/init_db.py existe"

[ -f backend/create_admin.py ]
check "backend/create_admin.py existe"

[ -f frontend/package.json ]
check "frontend/package.json existe"

[ -f frontend/vite.config.js ]
check "frontend/vite.config.js existe"

[ -d backend/app/models ] && [ -n "$(ls -A backend/app/models/*.py 2>/dev/null)" ]
check "backend/app/models/ tiene archivos .py"

[ -d backend/app/routes ] && [ -n "$(ls -A backend/app/routes/*.py 2>/dev/null)" ]
check "backend/app/routes/ tiene archivos .py"

[ -d frontend/src/pages ] && [ -n "$(ls -A frontend/src/pages/*.jsx 2>/dev/null)" ]
check "frontend/src/pages/ tiene archivos .jsx"

echo ""
echo "🔐 Verificando configuración..."
echo ""

# Verificar que .env no está en git
if [ -f .env ]; then
    grep "^.env$" .gitignore > /dev/null 2>&1
    check_warn ".env existe pero está en .gitignore"
else
    echo -e "${GREEN}✅${NC} .env no existe (correcto)"
fi

# Verificar que render.yaml tiene servicio api
grep "arm-cuentas-api" render.yaml > /dev/null 2>&1
check "render.yaml contiene servicio arm-cuentas-api"

grep "arm-cuentas-db" render.yaml > /dev/null 2>&1
check "render.yaml contiene base de datos arm-cuentas-db"

grep "arm-cuentas-storage" render.yaml > /dev/null 2>&1
check "render.yaml contiene disco persistente"

# Validar YAML
if command -v python &> /dev/null; then
    python -c "import yaml; yaml.safe_load(open('render.yaml'))" 2>/dev/null
    check "render.yaml válido (YAML sintaxis correcta)"
fi

echo ""
echo "📦 Verificando dependencias Python..."
echo ""

# Contar líneas en requirements.txt
REQ_COUNT=$(wc -l < backend/requirements.txt)
if [ "$REQ_COUNT" -gt 10 ]; then
    echo -e "${GREEN}✅${NC} requirements.txt tiene $REQ_COUNT dependencias"
else
    echo -e "${RED}❌${NC} requirements.txt tiene muy pocas dependencias ($REQ_COUNT)"
    ((ERRORS++))
fi

# Verificar dependencias críticas
CRITICAL_DEPS=("fastapi" "sqlalchemy" "psycopg2-binary" "pydantic" "python-jose" "uvicorn")
for dep in "${CRITICAL_DEPS[@]}"; do
    grep "^$dep" backend/requirements.txt > /dev/null 2>&1
    check "requirements.txt contiene $dep"
done

echo ""
echo "📦 Verificando dependencias Node..."
echo ""

# Contar líneas en package.json
if [ -f frontend/package.json ]; then
    grep "react" frontend/package.json > /dev/null 2>&1
    check "package.json contiene react"
    
    grep "axios" frontend/package.json > /dev/null 2>&1
    check "package.json contiene axios"
fi

echo ""
echo "🐳 Verificando configuración Docker..."
echo ""

[ -f backend/Dockerfile ]
check "backend/Dockerfile existe"

[ -f frontend/Dockerfile ]
check "frontend/Dockerfile existe"

[ -f docker-compose.yml ]
check "docker-compose.yml existe"

[ -f .gitignore ]
check ".gitignore existe"

grep "__pycache__" .gitignore > /dev/null 2>&1
check ".gitignore excluye __pycache__"

grep "uploads/" .gitignore > /dev/null 2>&1
check ".gitignore excluye uploads/"

grep "node_modules/" .gitignore > /dev/null 2>&1
check ".gitignore excluye node_modules/"

echo ""
echo "📄 Verificando documentación..."
echo ""

[ -f README.md ]
check "README.md existe"

[ -f GETTING_STARTED.md ]
check "GETTING_STARTED.md existe"

[ -f DEPLOYMENT.md ]
check "DEPLOYMENT.md existe"

[ -f RENDER_BLUEPRINT.md ]
check "RENDER_BLUEPRINT.md existe (Blueprint docs)"

[ -f PRE_DEPLOYMENT_CHECKLIST.md ]
check "PRE_DEPLOYMENT_CHECKLIST.md existe"

echo ""
echo "🔒 Verificando seguridad..."
echo ""

# Verificar que no hay credenciales en git
if git rev-parse --git-dir > /dev/null 2>&1; then
    # Buscar passwords o keys en git (primeros commits)
    git log --all -S "password" --oneline 2>/dev/null | wc -l | grep -E "^0$" > /dev/null 2>&1
    check_warn "No hay 'password' en historial de commits"
    
    git log --all -S "SECRET_KEY =" --oneline 2>/dev/null | wc -l | grep -E "^0$" > /dev/null 2>&1
    check_warn "No hay SECRET_KEY hardcodeada en commits"
else
    echo -e "${YELLOW}⚠️${NC} No es un repositorio git"
    ((WARNINGS++))
fi

echo ""
echo "✨ Verificando archivos específicos..."
echo ""

# Verificar que app/config.py lee de variables de entorno
grep "os.getenv" backend/app/config.py > /dev/null 2>&1
check "app/config.py usa os.getenv()"

grep "UPLOAD_DIR" backend/app/main.py > /dev/null 2>&1
check "app/main.py crea UPLOAD_DIR"

grep "health" backend/app/main.py > /dev/null 2>&1
check "app/main.py tiene health check endpoint"

# Verificar que init_db.py existe
grep "init_database\|create_admin" backend/init_db.py > /dev/null 2>&1
check "init_db.py tiene funciones de inicialización"

echo ""
echo "========================================"
echo ""

if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}✅ TODO ESTÁ LISTO PARA DESPLIEGUE${NC}"
    echo ""
    echo "Próximos pasos:"
    echo "1. git add ."
    echo "2. git commit -m 'Ready for Render deployment'"
    echo "3. git push origin main"
    echo "4. Ir a render.com y crear Blueprint"
    echo ""
    exit 0
else
    echo -e "${RED}❌ HAY $ERRORS ERRORES${NC}"
    if [ $WARNINGS -gt 0 ]; then
        echo -e "${YELLOW}⚠️ TAMBIÉN HAY $WARNINGS ADVERTENCIAS${NC}"
    fi
    echo ""
    echo "Soluciona los errores antes de desplegar"
    echo ""
    exit 1
fi
