# ✅ PRE-DEPLOYMENT CHECKLIST - ARM CUENTAS

Esta lista de verificación asegura que tu aplicación está lista para despliegue en Render con Blueprint.

## 📋 CHECKLIST DE ARCHIVOS

### Backend - Estructura

- [ ] `backend/app/main.py` existe
- [ ] `backend/app/config.py` existe
- [ ] `backend/app/database.py` existe
- [ ] `backend/app/models/` contiene 7+ archivos
- [ ] `backend/app/routes/` contiene 7+ archivos
- [ ] `backend/app/services/` contiene 5+ archivos
- [ ] `backend/app/schemas/` contiene 6+ archivos
- [ ] `backend/app/utils/` contiene 3+ archivos
- [ ] `backend/app/middleware/auth.py` existe

### Backend - Configuración

- [ ] `backend/requirements.txt` existe con 18+ dependencias
- [ ] `backend/.env.example` existe
- [ ] `backend/.env.production.example` existe
- [ ] `backend/Dockerfile` existe
- [ ] `backend/init_db.py` existe
- [ ] `backend/create_admin.py` existe

### Frontend - Estructura

- [ ] `frontend/src/pages/` contiene 5+ archivos .jsx
- [ ] `frontend/src/components/` contiene 2+ archivos .jsx
- [ ] `frontend/src/hooks/` contiene 2+ archivos .js
- [ ] `frontend/src/services/api.js` existe
- [ ] `frontend/src/styles/globals.css` existe

### Frontend - Configuración

- [ ] `frontend/package.json` existe
- [ ] `frontend/vite.config.js` existe
- [ ] `frontend/Dockerfile` existe
- [ ] `frontend/index.html` existe
- [ ] `frontend/public/manifest.json` existe (PWA)

### DevOps

- [ ] `render.yaml` existe en la **raíz**
- [ ] `docker-compose.yml` existe
- [ ] `.gitignore` existe
- [ ] `Procfile` existe (backup)

### Documentación

- [ ] `README.md` existe
- [ ] `GETTING_STARTED.md` existe
- [ ] `DEPLOYMENT.md` existe
- [ ] `RENDER_BLUEPRINT.md` existe (NUEVA)
- [ ] `00_START_HERE.md` existe

---

## 🔍 CHECKLIST DE VALIDACIÓN - render.yaml

### Estructura del archivo

```yaml
- [ ] render.yaml está en la RAÍZ (no en subcarpeta)
- [ ] Empieza con: services:
- [ ] Tiene 2 servicios web: arm-cuentas-api, arm-cuentas-web
- [ ] Tiene 1 base de datos: arm-cuentas-db
- [ ] Tiene 1 disco persistente: arm-cuentas-storage
```

### Servicio Backend (arm-cuentas-api)

```yaml
Ubicación: services[0]
- [ ] type: web
- [ ] env: python
- [ ] plan: starter
- [ ] pythonVersion: 3.9
- [ ] buildCommand: cd backend && pip install -r requirements.txt
- [ ] startCommand: contiene uvicorn + init_db.py
- [ ] healthCheckPath: /health
- [ ] disk: name, mountPath, sizeGB configurados
```

### Servicio Frontend (arm-cuentas-web)

```yaml
Ubicación: services[1]
- [ ] type: web
- [ ] env: node
- [ ] plan: starter
- [ ] nodeVersion: 18
- [ ] buildCommand: cd frontend && npm install && npm run build
- [ ] startCommand: cd frontend && npm install && npx serve -s dist -l $PORT
```

### Base de Datos (arm-cuentas-db)

```yaml
Ubicación: databases[0]
- [ ] name: arm-cuentas-db
- [ ] databaseName: arm_cuentas
- [ ] user: armcuentas
- [ ] plan: starter (o free)
- [ ] region: frankfurt (o tu preferencia)
```

### Disco Persistente (arm-cuentas-storage)

```yaml
Ubicación: services[0].disk
- [ ] name: arm-cuentas-storage
- [ ] mountPath: /var/data
- [ ] sizeGB: 5 (mínimo recomendado)
```

### Variables de Entorno

```yaml
Backend envVars debe tener:
- [ ] DATABASE_URL con fromDatabase
- [ ] SECRET_KEY con generateValue
- [ ] UPLOAD_DIR: /var/data/uploads
- [ ] DEBUG: False
- [ ] PYTHONUNBUFFERED: 1
- [ ] ENVIRONMENT: production
- [ ] ALLOWED_ORIGINS (con tu dominio)
- [ ] USE_OCR: True
- [ ] USE_S3: False
```

---

## 🐍 CHECKLIST - Backend Python

### Dependencies (requirements.txt)

- [ ] fastapi >= 0.104.0
- [ ] uvicorn >= 0.24.0
- [ ] sqlalchemy >= 2.0.0
- [ ] psycopg2-binary >= 2.9.0
- [ ] pydantic >= 2.0.0
- [ ] python-jose >= 3.3.0
- [ ] passlib >= 1.7.0
- [ ] python-dotenv >= 1.0.0
- [ ] PyPDF2 >= 3.0.0
- [ ] pdfplumber >= 0.10.0
- [ ] pytesseract >= 0.3.0
- [ ] pillow >= 10.0.0
- [ ] aiofiles >= 23.0.0
- [ ] python-multipart >= 0.0.0
- [ ] openpyxl >= 3.0.0 (Excel)
- [ ] boto3 >= 1.26.0 (AWS S3)
- [ ] alembic >= 1.12.0 (Migraciones)

### Config (app/config.py)

- [ ] Lee DATABASE_URL de variable de entorno
- [ ] Lee SECRET_KEY de variable de entorno
- [ ] Lee UPLOAD_DIR de variable de entorno
- [ ] Lee ENVIRONMENT de variable de entorno
- [ ] Valida SECRET_KEY en producción (error si es default)
- [ ] CORS configurado con ALLOWED_ORIGINS
- [ ] Logging configurado (logger importable desde config)

### Main (app/main.py)

- [ ] Importa logger desde config
- [ ] Crea UPLOAD_DIR si no existe
- [ ] Inicializa base de datos con try/except
- [ ] Logs de inicialización (INFO level)
- [ ] CORS configurado según ENVIRONMENT
- [ ] Health check endpoint /health con validación BD
- [ ] Health check endpoint /api/health
- [ ] Root endpoint / con info
- [ ] Error handlers configurados
- [ ] Startup events si es necesario

### Database (app/database.py)

- [ ] Importa settings desde config
- [ ] Crea engine con DATABASE_URL
- [ ] SessionLocal factory configurada
- [ ] get_db generator para FastAPI depends
- [ ] init_db() llama a Base.metadata.create_all()

### Init Script (init_db.py)

- [ ] Lee DATABASE_URL de config
- [ ] Crea todas las tablas si no existen
- [ ] Crea categorías por defecto si BD está vacía
- [ ] Logging de progreso
- [ ] Manejo de excepciones
- [ ] Cierra conexión correctamente

### Admin Script (create_admin.py)

- [ ] Lee DATABASE_URL de config
- [ ] Crea usuario "admin" si no existe
- [ ] Contraseña: "Admin123!" (cambiar después!)
- [ ] Role: "admin"
- [ ] Logging de éxito/error
- [ ] No falla si admin ya existe

---

## ⚛️ CHECKLIST - Frontend React

### Environment

- [ ] .env.example existe
- [ ] VITE_API_URL = http://localhost:8000/api (desarrollo)
- [ ] En producción se sobrescribe en render.yaml

### API Client (src/services/api.js)

- [ ] Importa axios
- [ ] Crea instance con baseURL
- [ ] Interceptor de request agrega JWT
- [ ] Interceptor de response maneja 401
- [ ] Endpoints declarados como objetos/funciones
- [ ] Manejo de errores

### Auth (src/hooks/useAuth.js, src/hooks/useStore.js)

- [ ] useAuthStore con Zustand
- [ ] login() function hace POST /auth/login
- [ ] logout() limpia token y usuario
- [ ] Persistencia en localStorage
- [ ] hydration al cargar página

### Pages - LoginPage

- [ ] Form con username y password
- [ ] Validación básica
- [ ] Mostrar errores
- [ ] Loading state
- [ ] Submit hace login() de useAuthStore
- [ ] Redirige a /dashboard si login exitoso
- [ ] Almacena JWT en localStorage

### Pages - DashboardPage

- [ ] Usa useDashboardStore
- [ ] Fetch data desde /api/movements/dashboard/summary
- [ ] Muestra 6 tarjetas de resumen
- [ ] Calcula ingresos/gastos/beneficio
- [ ] Responsive design
- [ ] Loading/error states

### Pages - MovementsPage

- [ ] Usa useMovementsStore
- [ ] Fetch data desde /api/movements
- [ ] Tabla con datos
- [ ] Filtros básicos (tipo, estado)
- [ ] Responsive design
- [ ] Paginación (si aplica)

### Pages - ObrasPage

- [ ] Usa store de obras
- [ ] Grid de tarjetas
- [ ] Información resumida
- [ ] "Ver detalles" button
- [ ] Responsive design

### Pages - UploadInvoicePage

- [ ] Drag & drop zone
- [ ] Upload a /api/files/upload
- [ ] Mostrar progreso
- [ ] Extraer datos del response
- [ ] Formulario de revisión
- [ ] Submit crea movimiento
- [ ] Validación de archivos

### Components

- [ ] Navbar: Logo, usuario, logout
- [ ] Layout: Navbar + main content
- [ ] Responsive (mobile, tablet, desktop)
- [ ] Colores ARM (rojo #dc2626, gris #1f2937)

### Styling (src/styles/globals.css)

- [ ] Tailwind directives (@apply, etc)
- [ ] Colores corporativos ARM
- [ ] Utilidades custom (.btn-primary, .card, etc)
- [ ] Responsive breakpoints

---

## 🐳 CHECKLIST - Docker

### Dockerfiles

- [ ] backend/Dockerfile existe
- [ ] frontend/Dockerfile existe
- [ ] Ambos usan imágenes base ligeras (alpine si es posible)
- [ ] Copian archivos correctos
- [ ] Exponen puertos correctos

### docker-compose.yml

- [ ] Versión 3.8+
- [ ] 3 servicios: postgres, backend, frontend
- [ ] Volúmenes compartidos para desarrollo
- [ ] Variables de entorno (.env)
- [ ] Health checks
- [ ] Depends_on configurado

### .gitignore

- [ ] __pycache__/
- [ ] *.pyc
- [ ] venv/
- [ ] .env
- [ ] uploads/
- [ ] node_modules/
- [ ] dist/
- [ ] .DS_Store
- [ ] *.log
- [ ] .vscode/, .idea/

---

## 🔒 CHECKLIST - Seguridad

- [ ] SECRET_KEY es aleatorio y largo (32+ chars)
- [ ] DATABASE_URL no contiene credenciales en Git
- [ ] .env está en .gitignore
- [ ] Contraseña de admin es temporal (cambiar después)
- [ ] HTTPS habilitado en producción (Render lo hace automáticamente)
- [ ] CORS restrictivo en producción
- [ ] DEBUG = False en producción
- [ ] JWT tokens con expiración

---

## 📝 CHECKLIST - Documentación

- [ ] README.md completo
- [ ] GETTING_STARTED.md paso a paso
- [ ] DEPLOYMENT.md con instrucciones
- [ ] RENDER_BLUEPRINT.md completo
- [ ] Código comentado (funciones principales)
- [ ] Variables de entorno documentadas
- [ ] Errores comunes y soluciones

---

## 🚀 CHECKLIST - PRE-COMMIT

Antes de hacer push a GitHub:

```bash
# Verificar estructura
- [ ] find . -name "__pycache__" -type d → No debe haber
- [ ] find . -name ".env" -type f → No debe haber
- [ ] ls render.yaml → Debe existir en raíz

# Validar YAML
- [ ] python -c "import yaml; yaml.safe_load(open('render.yaml'))"
- [ ] No errores de sintaxis

# Verificar git
- [ ] git status → No debe haber .env, __pycache__, uploads/
- [ ] git status → Debe mostrar solo archivos que queremos
```

---

## 📋 CHECKLIST - RENDER BLUEPRINT

Después de hacer push a GitHub:

1. [ ] Acceder a render.com
2. [ ] Conectar repositorio
3. [ ] Seleccionar rama main
4. [ ] Click "Create Blueprint Instance"
5. [ ] Render detecta render.yaml automáticamente
6. [ ] Revisar servicios detallados:
   - [ ] arm-cuentas-api: Python 3.9, Starter
   - [ ] arm-cuentas-web: Node 18, Starter
   - [ ] arm-cuentas-db: PostgreSQL Free
7. [ ] Revisar variables de entorno
8. [ ] Revisar disco persistente: /var/data (5GB)
9. [ ] Click "Deploy"
10. [ ] Esperar 15-25 minutos
11. [ ] Verificar logs de cada servicio
12. [ ] Acceder a URLs generadas
13. [ ] Health checks OK: https://api.url/health
14. [ ] Login con admin/Admin123!
15. [ ] Probar upload de factura
16. [ ] Dashboard muestra datos

---

## ✅ SEÑALES DE ÉXITO

Una vez desplegado, deberías ver:

```
✅ Frontend accesible: https://arm-cuentas-web.onrender.com
✅ Backend API: https://arm-cuentas-api.onrender.com/health → healthy
✅ PostgreSQL: Conectada
✅ Almacenamiento: /var/data accesible
✅ Login funciona
✅ Upload de facturas funciona
✅ Dashboard muestra datos
```

---

## 🆘 SI ALGO FALLA

1. [ ] Ver logs en Render (cada servicio)
2. [ ] Buscar error específico en RENDER_BLUEPRINT.md
3. [ ] Ejecutar health check: curl /health
4. [ ] Verificar DATABASE_URL
5. [ ] Verificar UPLOAD_DIR
6. [ ] Ejecutar init_db.py manualmente si es necesario

---

**Última actualización:** 2026-07-07  
**Versión:** ARM CUENTAS 1.0.0
