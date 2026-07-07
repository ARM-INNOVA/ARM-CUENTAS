# QUICKSTART.md - Guía Rápida de Inicio

## 🚀 Inicio en 5 minutos

### Opción 1: Con Docker Compose (Recomendado)

```bash
# 1. Clonar el repositorio (si aún no lo has hecho)
git clone https://github.com/tu-usuario/arm-cuentas.git
cd arm-cuentas

# 2. Iniciar la aplicación
docker-compose up

# 3. Crear usuario administrador
docker-compose exec backend python create_admin.py

# 4. Acceder a la aplicación
# Backend: http://localhost:8000
# Frontend: http://localhost:5173
# Docs API: http://localhost:8000/docs
```

### Opción 2: Sin Docker (Local)

#### Requisitos previos:
- Python 3.9+
- Node.js 18+
- PostgreSQL 12+ corriendo en localhost

#### Backend:

```bash
cd backend

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar base de datos
cp .env.example .env
# Editar .env y configurar DATABASE_URL

# Crear usuario admin
python create_admin.py

# Iniciar servidor
python -m uvicorn app.main:app --reload
```

Backend en: http://localhost:8000

#### Frontend:

```bash
# En otra terminal
cd frontend

# Instalar dependencias
npm install

# Iniciar servidor
npm run dev
```

Frontend en: http://localhost:5173

## 📝 Acceso Inicial

**Usuario**: `admin`
**Contraseña**: `Admin123!`

⚠️ **IMPORTANTE**: Cambia la contraseña en tu primer login

## 🧪 Primeros Pasos

1. **Crea una obra**:
   - Menú: Obras → Nueva Obra
   - Nombre: "Reforma Pelayo 5"
   - Cliente: "Cliente Test"
   - Estado: Activa

2. **Sube una factura**:
   - Menú: Subir Factura
   - Arrastra un PDF o selecciona uno
   - Revisa los datos extraídos
   - Selecciona la obra y categoría
   - Guarda

3. **Ver dashboard**:
   - Dashboard muestra resumen del mes
   - Ingresos, gastos y beneficio

## 🛠️ Desarrolladores

### Estructura del proyecto

```
├── backend/              # API FastAPI
│   ├── app/
│   │   ├── models/       # Modelos BD
│   │   ├── routes/       # Endpoints API
│   │   ├── schemas/      # Validación
│   │   ├── services/     # Lógica negocio
│   │   └── utils/        # Utilidades
│   ├── requirements.txt
│   └── create_admin.py
├── frontend/             # React + Vite
│   ├── src/
│   │   ├── pages/        # Páginas
│   │   ├── components/   # Componentes
│   │   ├── services/     # API client
│   │   └── hooks/        # Custom hooks
│   ├── package.json
│   └── vite.config.js
└── docker-compose.yml
```

### Comandos útiles

```bash
# Backend
python -m uvicorn app.main:app --reload        # Desarrollo
python create_admin.py                          # Crear admin
python -m pytest tests/                         # Tests

# Frontend
npm run dev                                     # Desarrollo
npm run build                                   # Build producción
npm run lint                                    # Lint

# Docker
docker-compose up                               # Iniciar todo
docker-compose down                             # Parar
docker-compose logs -f backend                 # Ver logs backend
```

### Variables de entorno (backend)

```bash
cp backend/.env.example backend/.env
```

Edita `backend/.env` con tus valores:
- `DATABASE_URL`: Conexión a PostgreSQL
- `SECRET_KEY`: Clave para JWT
- `DEBUG`: True para desarrollo
- `UPLOAD_DIR`: Directorio de uploads

## 📚 Documentación

- **API Swagger**: http://localhost:8000/docs
- **Despliegue**: Ver [DEPLOYMENT.md](./DEPLOYMENT.md)
- **Arquitectura**: Ver [README.md](./README.md)

## 🐛 Problemas Comunes

### "Connection refused" a la base de datos
- Asegúrate que PostgreSQL está corriendo
- Verifica DATABASE_URL en .env
- Con Docker: `docker-compose ps` debe mostrar postgres corriendo

### "Port already in use"
- Backend usa puerto 8000
- Frontend usa puerto 5173
- Cambia los puertos en docker-compose.yml o en los comandos

### "Module not found"
```bash
# Backend
pip install -r requirements.txt

# Frontend
npm install
```

### "npm: command not found"
- Instala Node.js desde https://nodejs.org

### "python: command not found"
- Asegúrate de usar `python3` en sistemas Linux/Mac
- O instala Python desde https://python.org

## 📞 Soporte

¿Problemas? Abre un issue en GitHub o contacta con el equipo.

---

¡Listo! Ya puedes empezar a usar **ARM CUENTAS** 🎉
