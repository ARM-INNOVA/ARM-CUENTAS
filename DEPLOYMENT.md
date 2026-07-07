# 🚀 Guía Completa de Despliegue en Render

## Prerrequisitos

- Cuenta en GitHub con el código pusheado
- Cuenta en Render (free: https://render.com)
- Cuenta en AWS (opcional, para S3)

## Paso 1: Preparar el Código para Producción

### 1.1 Backend

```bash
# Agregar gunicorn a requirements.txt
echo "gunicorn==21.2.0" >> backend/requirements.txt

# Crear archivo Procfile (opcional, Render lo detecta)
cat > backend/Procfile << 'EOF'
web: gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT
EOF
```

### 1.2 Frontend

```bash
# Compilar para producción
cd frontend
npm run build

# El directorio dist/ será desplegado
```

### 1.3 Variables de Entorno

```bash
# backend/.env.production
DATABASE_URL=postgresql://...
SECRET_KEY=generate_strong_key_here
DEBUG=False
PYTHONUNBUFFERED=1
UPLOAD_DIR=/tmp/uploads
USE_S3=True
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_S3_BUCKET=arm-cuentas-prod
```

## Paso 2: Subir a GitHub

```bash
git add .
git commit -m "Preparar para despliegue en Render"
git push origin main
```

## Paso 3: Crear Servicio en Render

### 3.1 Crear Base de Datos

1. Ve a https://render.com/dashboard
2. Haz clic en "New +" → "PostgreSQL"
3. Configura:
   - Name: `arm-cuentas-db`
   - Database: `arm_cuentas`
   - User: `armcuentas`
   - Region: `Frankfurt` (o la más cercana)
   - PostgreSQL Version: 15
   - Plan: **Free** ($0)
4. **Copia la conexión URL externa**

### 3.2 Crear Servicio Web Backend

1. Ve a https://render.com/dashboard
2. Haz clic en "New +" → "Web Service"
3. Selecciona tu repositorio de GitHub
4. Configura:
   - **Name**: `arm-cuentas-api`
   - **Root Directory**: `backend`
   - **Runtime**: `Python 3.9`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000`
   - **Plan**: **Free** ($0)
   - **Region**: Same as DB
   - **Auto-Deploy**: Yes

5. Haz clic en "Create Web Service"

### 3.3 Agregar Variables de Entorno al Backend

1. En Render, ve a tu servicio web
2. Haz clic en "Environment"
3. Agrega:

```
DATABASE_URL=postgresql://armcuentas:PASSWORD@HOST:5432/arm_cuentas
SECRET_KEY=your_super_secret_key_here_change_this
DEBUG=False
PYTHONUNBUFFERED=1
UPLOAD_DIR=/tmp/uploads
USE_S3=True
AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_aws_secret
AWS_S3_BUCKET=arm-cuentas-prod
```

4. Haz clic en "Save Changes"

### 3.4 Crear Servicio Frontend

1. Ve a https://render.com/dashboard
2. Haz clic en "New +" → "Static Site"
3. Selecciona tu repositorio
4. Configura:
   - **Name**: `arm-cuentas`
   - **Root Directory**: `frontend`
   - **Build Command**: `npm install && npm run build`
   - **Publish Directory**: `dist`
   - **Plan**: **Free** ($0)
   - **Region**: Same as backend

5. Haz clic en "Create Static Site"

### 3.5 Configurar CORS en Frontend

En tu variable de entorno del frontend, o en `frontend/src/services/api.js`:

```javascript
const API_BASE_URL = 'https://tu-api-render.onrender.com/api'
```

## Paso 4: Configurar S3 para Almacenamiento (Recomendado)

### 4.1 Crear Bucket S3

1. Ve a AWS Console
2. S3 → Create Bucket
3. Name: `arm-cuentas-prod-xxxxxx` (debe ser único)
4. Region: `eu-west-1`
5. Block all public access: **ON**
6. Create Bucket

### 4.2 Crear IAM User

1. IAM → Users → Create User
2. Name: `arm-cuentas-api`
3. Attach policy: `AmazonS3FullAccess`
4. Create Access Key
5. **Guarda Access Key ID y Secret Access Key**

### 4.3 Agregar a Render

En tu servicio web en Render, agrega:

```
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...
AWS_S3_BUCKET=arm-cuentas-prod-xxxxxx
```

## Paso 5: Inicializar Base de Datos

```bash
# Conectar por SSH a Render (si tienes acceso)
# O crear un script de inicialización

# backend/migrations/init_db.py
from app.database import init_db
init_db()

# Ejecutar una sola vez
python -c "from app.database import init_db; init_db()"
```

### Alternativa: Usar Alembic para Migraciones

```bash
# Instalar Alembic
pip install alembic

# Inicializar
alembic init alembic

# Crear migración inicial
alembic revision --autogenerate -m "Initial migration"

# En render.yaml, ejecutar antes de arrancar:
# upgrade head
```

## Paso 6: Crear Usuario Administrador Inicial

```bash
# backend/create_admin.py
import os
from app.database import SessionLocal
from app.models.user import User
from app.services.user_service import UserService

db = SessionLocal()

# Crear admin
admin = User(
    email="admin@armcuentas.com",
    username="admin",
    full_name="Administrador",
    hashed_password=User.hash_password("password123"),  # CAMBIAR EN PRODUCCIÓN
    role="admin",
    is_active=True
)

db.add(admin)
db.commit()
print("Admin creado exitosamente")
```

## Paso 7: Verificar Despliegue

1. Ve a tu servicio web en Render
2. Busca en Logs si hay errores
3. Copia la URL: `https://tu-api-render.onrender.com`
4. Prueba: `https://tu-api-render.onrender.com/health`

Si ves `{"status":"healthy"}`, ¡está funcionando!

## Paso 8: Conectar Frontend a Backend

En `frontend/src/services/api.js`:

```javascript
const API_BASE_URL = 'https://tu-api-render.onrender.com/api'
```

O usar variable de entorno:

```bash
# frontend/.env.production
VITE_API_URL=https://tu-api-render.onrender.com/api
```

## Paso 9: SSL y Dominio Personalizado

### Con Dominio en Render

1. En Render, ve a Settings
2. Busca "Custom Domain"
3. Agrega tu dominio: `armcuentas.tuempresa.com`
4. Render genera automáticamente certificado SSL

### Con Dominio Externo

1. Obtén el dominio (GoDaddy, NameCheap, etc.)
2. Cambia DNS a apuntar a Render:
   - Render te dará los name servers
   - O agrega CNAME record
3. Espera propagación (24-48 horas)

## Solución de Problemas

### Error: "ModuleNotFoundError"

```bash
# Ensure requirements.txt contiene todas las dependencias
pip freeze > requirements.txt
```

### Error: "Connection refused" a base de datos

1. Verifica DATABASE_URL en Render
2. Asegúrate que PostgreSQL está creado
3. Reinicia el servicio web

### Error: "413 Request Entity Too Large"

Aumenta el límite en `backend/app/config.py`:

```python
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100 MB
```

### Frontend no se comunica con API

1. Verifica URL de API en `api.js`
2. Verifica CORS en `backend/app/main.py`
3. Abre consola del navegador (F12) para ver errores

### Archivos no se guardan entre despliegues

1. Usa S3 (recomendado)
2. O agrega disco persistente en Render
3. Configura `UPLOAD_DIR=/mnt/data` (si usas disco)

## Monitoreo en Producción

### Logs

```bash
# Ver logs en tiempo real
# Render Dashboard → Logs

# O via CLI
render logs -i service_id
```

### Health Check

```bash
curl https://tu-api-render.onrender.com/health
```

### Backups de Base de Datos

En Render, tu base de datos libre tiene backups automáticos de 7 días.

Para backups más frecuentes, usa:

```bash
# Descarga de backup manual
pg_dump -h host -U user -d database > backup.sql

# Restaurar
psql -h host -U user -d database < backup.sql
```

## Próximos Pasos

- [ ] Configurar dominio personalizado
- [ ] Activar monitoreo y alertas
- [ ] Configurar backups automáticos en S3
- [ ] Implementar logging centralizado (Papertrail, etc)
- [ ] Configurar CI/CD en GitHub Actions
- [ ] Agregar tests automáticos
- [ ] Documentar API con Swagger

## Referencias

- Render Docs: https://render.com/docs
- FastAPI: https://fastapi.tiangolo.com/
- React: https://react.dev/
- PostgreSQL: https://www.postgresql.org/docs/

---

¡Tu aplicación **ARM CUENTAS** está lista para producción! 🎉
