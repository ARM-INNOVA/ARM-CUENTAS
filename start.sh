#!/bin/bash

# Script para iniciar la aplicación en desarrollo local

echo "🚀 Iniciando ARM CUENTAS en desarrollo..."
echo ""

# Verificar si Docker está disponible
if command -v docker &> /dev/null; then
    echo "✅ Docker encontrado"
    
    # Mostrar opciones
    echo ""
    echo "Opciones:"
    echo "1. Iniciar con Docker Compose (recomendado)"
    echo "2. Iniciar solo backend"
    echo "3. Iniciar solo frontend"
    echo "4. Iniciar ambos sin Docker"
    echo ""
    read -p "Selecciona una opción (1-4): " option
    
    case $option in
        1)
            echo "Iniciando con Docker Compose..."
            docker-compose up
            ;;
        2)
            echo "Iniciando backend..."
            cd backend
            python -m uvicorn app.main:app --reload
            ;;
        3)
            echo "Iniciando frontend..."
            cd frontend
            npm run dev
            ;;
        4)
            echo "Iniciando ambos sin Docker..."
            # Backend en background
            cd backend
            python -m uvicorn app.main:app --reload &
            BACKEND_PID=$!
            
            # Frontend
            cd ../frontend
            npm run dev
            
            # Cleanup
            kill $BACKEND_PID 2>/dev/null
            ;;
        *)
            echo "Opción inválida"
            exit 1
            ;;
    esac
else
    echo "❌ Docker no encontrado"
    echo ""
    echo "Iniciando sin Docker..."
    echo ""
    
    # Backend
    echo "Iniciando backend..."
    cd backend
    python -m uvicorn app.main:app --reload &
    BACKEND_PID=$!
    
    # Esperar a que inicie
    sleep 3
    
    # Frontend
    cd ../frontend
    echo "Iniciando frontend..."
    npm run dev
    
    # Cleanup
    kill $BACKEND_PID 2>/dev/null
fi
