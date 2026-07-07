# 🚀 DESPLIEGUE EN RENDER CON BLUEPRINT

Esta guía te ayudará a desplegar **ARM CUENTAS** en **Render** usando **Blueprint** automáticamente.

## ¿Qué es Render Blueprint?

**Blueprint** es la forma automática de desplegar toda tu aplicación (backend, frontend, base de datos y almacenamiento) en Render con un solo click.

### Ventajas de Blueprint

✅ Despliegue completamente automatizado  
✅ Base de datos PostgreSQL incluida  
✅ Almacenamiento persistente para facturas  
✅ Configuración de variables de entorno  
✅ URLs públicas generadas automáticamente  
✅ Sin configuración manual de servicios  

---

## 📋 PRE-REQUISITOS

1. **Cuenta en GitHub**
   - Crear si no tienes: https://github.com/signup

2. **Cuenta en Render**
   - Crear si no tienes: https://render.com
   - Usar GitHub para login (recomendado)

3. **Git configurado localmente**
   ```bash
   git config --global user.name "Tu Nombre"
   git config --global user.email "tu@email.com"
   ```

---

## 🔧 PASO 1: PREPARAR EL REPOSITORIO

### 1.1 Crear repositorio en GitHub

```bash
# En /workspaces/ARM-CUENTAS
git init
git add .
git commit -m "Initial commit: ARM CUENTAS v1.0.0"

# Crear repositorio en GitHub manualmente o con:
# gh repo create ARM-CUENTAS --source=. --remote=origin --push
```

### 1.2 Verificar que `render.yaml` existe y es válido

```bash
# Desde raíz del proyecto
cat render.yaml

# Debe mostrar:
# - Servicio web: arm-cuentas-api
# - Servicio web: arm-cuentas-web
# - Base de datos: arm-cuentas-db
# - Disco persistente: arm-cuentas-storage
```

### 1.3 Verificar que el backend esté listo

```bash
# Comprobar que requirements.txt existe
ls -la backend/requirements.txt

# Comprobar que app/main.py existe
ls -la backend/app/main.py

# Comprobar que init_db.py existe
ls -la backend/init_db.py
```

### 1.4 Verificar que el frontend esté listo

```bash
# Comprobar que package.json existe
ls -la frontend/package.json

# Comprobar que vite.config.js existe
ls -la frontend/vite.config.js
```

---

## 🌐 PASO 2: CONECTAR CON RENDER

### 2.1 Ir a Render

1. Abre https://render.com
2. Click en **"Sign up"** o **"Log in"**
3. Usa GitHub para autenticarte (recomendado)

### 2.2 Crear nuevo Blueprint

1. En el dashboard, click en **"New +"** (arriba a la derecha)
2. Selecciona **"Blueprint"**
3. Conecta tu repositorio de GitHub

### 2.3 Autorizar acceso a GitHub

1. Si es la primera vez, te pedirá autorización
2. Click en **"Authorize Render"**
3. Selecciona los repositorios a los que Render puede acceder
4. Click en **"Authorize"**

---

## 📦 PASO 3: DETECTAR BLUEPRINT

### 3.1 Seleccionar repositorio

1. En Render, busca tu repositorio **ARM-CUENTAS**
2. Selecciona la rama **main** (por defecto)
3. Click en **"Create Blueprint Instance"**

### 3.2 Render detecta automáticamente

Render debería detectar el archivo `render.yaml`:

```
✅ Detected render.yaml
  - Service: arm-cuentas-api (web, Python 3.9)
  - Service: arm-cuentas-web (web, Node 18)
  - Database: arm-cuentas-db (PostgreSQL)
```

Si **no ve el archivo**, verifica:
- `render.yaml` está en la **raíz del proyecto** (no en subcarpetas)
- No tiene errores de sintaxis YAML
- Nombres de servicios son correctos

---

## ⚙️ PASO 4: REVISAR CONFIGURACIÓN

### 4.1 Revisar servicios

En la pantalla "Create Blueprint Instance", deberías ver:

| Servicio | Tipo | Runtime | Plan |
|----------|------|---------|------|
| arm-cuentas-api | web | Python 3.9 | Starter |
| arm-cuentas-web | web | Node 18 | Starter |
| arm-cuentas-db | PostgreSQL | - | Free |

### 4.2 Revisar variables de entorno

Deberías ver pre-rellenas:

```
DATABASE_URL          → Se conecta a arm-cuentas-db automáticamente
SECRET_KEY            → Generado automáticamente (largo y seguro)
UPLOAD_DIR            → /var/data/uploads
DEBUG                 → False
PYTHONUNBUFFERED      → 1
ENVIRONMENT           → production
```

### 4.3 Disco persistente

Debería estar configurado:

```
Nombre: arm-cuentas-storage
Tamaño: 5 GB
Montado en: /var/data
Servicios: arm-cuentas-api
```

### 4.4 Revisar manualmente render.yaml

Si quieres editar variables antes de desplegar:

```yaml
# Ver archivo y hacer cambios
nano render.yaml

# Busca estas secciones y verifica:
- DATABASE_URL: Debe decir "fromDatabase: arm-cuentas-db"
- SECRET_KEY: Debe decir "generateValue: true"
- UPLOAD_DIR: Debe ser "/var/data/uploads"
```

---

## 🎯 PASO 5: DESPLEGAR

### 5.1 Click en "Deploy"

En la pantalla de revisión:
1. Lee la configuración (última oportunidad para cambiar)
2. Click en **"Create Blueprint Instance"** o **"Deploy"**

### 5.2 Esperar despliegue

Render desplegará automáticamente en este orden:

```
1️⃣ Crear base de datos PostgreSQL
   ⏱️ ~2-3 minutos
   Status: "Creating..."

2️⃣ Crear almacenamiento persistente
   ⏱️ ~1 minuto
   Status: "Creating..."

3️⃣ Construir y desplegar backend
   ⏱️ ~5-10 minutos (primera vez más lenta)
   Status: "Build in progress..." → "Deployed"

4️⃣ Construir y desplegar frontend
   ⏱️ ~5-10 minutos
   Status: "Build in progress..." → "Deployed"
```

**Total estimado: 15-25 minutos**

### 5.3 Monitorear despliegue

En Render:

1. Ve a tu Blueprint Instance
2. Click en cada servicio para ver logs:
   - **arm-cuentas-api**: Backend logs
   - **arm-cuentas-web**: Frontend logs
   - **arm-cuentas-db**: Database logs

Deberías ver en los logs:

```
Backend:
✅ Database initialized
✅ Upload directory created: /var/data/uploads
✅ Server listening on 0.0.0.0:PORT

Frontend:
✅ Build successful
✅ Serving dist/ on port PORT
```

---

## ✅ PASO 6: VERIFICAR DESPLIEGUE

### 6.1 Obtener URLs

Una vez desplegado, Render genera URLs:

```
Backend:  https://arm-cuentas-api.onrender.com
Frontend: https://arm-cuentas-web.onrender.com
Database: PostgreSQL (solo interno)
```

### 6.2 Acceder a la aplicación

1. Abre https://arm-cuentas-web.onrender.com (o tu URL personalizada)
2. Deberías ver login de ARM CUENTAS
3. Las primeras cargas pueden ser lentas (~5-10s) en Render free tier

### 6.3 Health checks

Verifica que todo funciona:

```bash
# Backend health
curl https://arm-cuentas-api.onrender.com/health

# Debería responder:
{
  "status": "healthy",
  "version": "1.0.0",
  "environment": "production",
  "database": "✅ connected",
  "storage": "✅ available"
}

# Frontend
curl https://arm-cuentas-web.onrender.com

# Debería devolver HTML de React
```

---

## 🔐 PASO 7: CREAR USUARIO ADMINISTRADOR

### 7.1 Opción A: Vía Terminal en Render

1. En Render, ve a **arm-cuentas-api** → **"Shell"**
2. Ejecuta:
   ```bash
   cd /backend
   python create_admin.py
   ```
3. Debería mostrar:
   ```
   ✅ Usuario administrador creado exitosamente
      Username: admin
      Password: Admin123!
      Email: admin@armcuentas.local
   ```

### 7.2 Opción B: Vía Variable de Entorno (Render Trigger)

En el `render.yaml` futuro, podríamos agregar:

```yaml
- key: CREATE_DEFAULT_ADMIN
  value: "true"
```

Y en `main.py`:

```python
if os.getenv("CREATE_DEFAULT_ADMIN") == "true":
    from backend.create_admin import create_admin
    create_admin()
```

---

## 🎮 PASO 8: LOGIN Y PRIMEROS PASOS

### 8.1 Login

1. Abre https://arm-cuentas-web.onrender.com
2. Username: `admin`
3. Password: `Admin123!`
4. Click "Login"

### 8.2 Cambiar contraseña

**IMPORTANTE:** Después de la primera vez:

1. Ve a Perfil/Settings (futuro)
2. Cambia la contraseña de `Admin123!` a algo seguro

### 8.3 Crear una obra

1. Ve a "Obras"
2. Click "Nueva Obra"
3. Nombre: "Mi Primera Obra"
4. Guarda

### 8.4 Probar upload de factura

1. Ve a "Subir Factura"
2. Arrastra un PDF de ejemplo
3. Debería extraer datos automáticamente
4. Revisa y guarda

---

## 🐛 SOLUCIÓN DE PROBLEMAS

### Problema: "render.yaml not detected"

**Causa:** Archivo no está en la raíz o tiene errores YAML  
**Solución:**
```bash
# Verifica ubicación
ls render.yaml  # Debe estar en la raíz

# Valida sintaxis YAML
python -c "import yaml; yaml.safe_load(open('render.yaml'))"
```

---

### Problema: "Build failed: No such file or directory"

**Causa:** Rutas incorrectas en `buildCommand` o `startCommand`  
**Solución:**
```yaml
# ❌ INCORRECTO
buildCommand: pip install -r requirements.txt

# ✅ CORRECTO
buildCommand: cd backend && pip install -r requirements.txt
```

---

### Problema: "DATABASE_URL is not set"

**Causa:** Base de datos no se inicializó correctamente  
**Solución:**
1. Ve a "arm-cuentas-db" en Render
2. Verifica que está "Available"
3. Si está roja, elimina y crea nueva Blueprint

---

### Problema: "Permission denied /var/data/uploads"

**Causa:** Disco persistente no está montado correctamente  
**Solución:**
```yaml
disk:
  name: arm-cuentas-storage
  mountPath: /var/data
  sizeGB: 5
```

Verificar en Render:
1. Ve a "arm-cuentas-api"
2. Sección "Disk"
3. Debe mostrar: "arm-cuentas-storage (5 GB) mounted at /var/data"

---

### Problema: "Application not responsive" o "500 error"

**Causa:** Backend no inició correctamente  
**Solución:**
1. Ve a "arm-cuentas-api" → "Logs"
2. Busca mensajes de error
3. Errores comunes:
   ```
   ❌ Error inicializando BD → Check DATABASE_URL
   ❌ ModuleNotFoundError → Missing dependency en requirements.txt
   ❌ Address already in use → Port conflict (no debería pasar en Render)
   ```

---

### Problema: Facturas no se guardan

**Causa:** Almacenamiento persistente no funciona  
**Solución:**
```bash
# En Shell de Render para arm-cuentas-api:
ls -la /var/data/
mkdir -p /var/data/uploads
chmod 755 /var/data/uploads
```

---

## 📈 OPTIMIZACIONES PARA PRODUCCIÓN

### Después del despliegue, considera:

1. **Agregar dominio personalizado**
   - Render → Settings → Custom Domain
   - Ej: `armcuentas.tuempresa.com`

2. **Subir a plan mejor** (si crece)
   - Cambiar de "Starter" a "Standard"
   - Más memoria, más concurrencia

3. **Backup de base de datos**
   - Render crea backups automáticos
   - Configurar retención en Settings

4. **Caché y CDN**
   - Render tiene CDN integrado
   - Archivos estáticos se cachean automáticamente

5. **Monitoreo**
   - Render envía alertas si el servicio cae
   - Ver en Render Dashboard → Alerts

---

## 🔄 ACTUALIZAR APLICACIÓN DESPUÉS DE CAMBIOS

Después de hacer cambios locales:

```bash
# 1. Commit y push a GitHub
git add .
git commit -m "Fix: descripción del cambio"
git push origin main

# 2. Render se redesplegará automáticamente
# (si tienes "Auto-deploy on push" habilitado)

# 3. Ver logs en Render para verificar
# Render → arm-cuentas-api/web → Logs
```

---

## 🧹 LIMPIAR BLUEPRINT

Si necesitas empezar de nuevo:

1. Abre Render Dashboard
2. Ve al Blueprint Instance
3. Click "⋮" (Más opciones) → "Delete"
4. Confirma

Luego crea uno nuevo siguiendo esta guía.

---

## 📊 LÍMITES DE RENDER FREE TIER

| Aspecto | Límite |
|---------|--------|
| Almacenamiento | 5 GB (configurable) |
| CPU | Compartido (3 vCPU compartidas) |
| Memoria | 512 MB |
| Transferencia de datos | 100 GB/mes |
| Base de datos | 30 MB (PostgreSQL Free) |
| Inactividad | Se duerme después de 15 min sin uso |

**Nota:** En el plan free, la app "se duerme" si no se usa por 15 minutos. La primera petición después tarda ~30s en despertar.

---

## 🎯 CHECKLIST FINAL

- [ ] Repositorio en GitHub
- [ ] `render.yaml` en la raíz del proyecto
- [ ] Backend con `requirements.txt` actualizado
- [ ] Frontend con `package.json` actualizado
- [ ] `init_db.py` en el backend
- [ ] `create_admin.py` en el backend
- [ ] Variables de entorno configuradas
- [ ] Disco persistente configurado
- [ ] Health check endpoints funcionando
- [ ] Blueprint creado en Render
- [ ] Despliegue completado exitosamente
- [ ] Acceso a https://arm-cuentas-web.onrender.com
- [ ] Login con admin/Admin123! funcionando
- [ ] Upload de facturas funcionando
- [ ] Dashboard mostrando datos

---

## 📞 SOPORTE RENDER

Si algo no funciona:

1. **Render Docs:** https://render.com/docs
2. **Render Community:** https://render.com/community
3. **Estado de servicios:** https://render-status.com
4. **Contact:** support@render.com

---

## 🎉 ¡LISTO!

Tu aplicación ARM CUENTAS está en internet en:

```
🌐 https://arm-cuentas-web.onrender.com
🔌 Backend API: https://arm-cuentas-api.onrender.com/docs
📊 Dashboard: https://arm-cuentas-web.onrender.com
```

**Comparte el link con tu equipo y empieza a usar!**

---

**Versión:** 1.0  
**Última actualización:** 2026-07-07  
**Autor:** ARM CUENTAS Team
