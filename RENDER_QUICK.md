# 🚀 DESPLIEGUE RÁPIDO EN RENDER (5 minutos)

## ⚡ Los 5 Pasos Essenciales

### 1️⃣ Ejecutar verificación
```bash
cd /workspaces/ARM-CUENTAS
bash pre-deploy-check.sh
```

Si todo pasa ✅, continúa. Si hay ❌, arréglalo primero.

### 2️⃣ Subir a GitHub
```bash
git add .
git commit -m "Ready for Render: ARM CUENTAS v1.0.0"
git push origin main
```

### 3️⃣ Ir a Render
Abre: https://render.com

Login con GitHub → Dashboard

### 4️⃣ Crear Blueprint
1. Click **"New +"** (arriba derecha)
2. Selecciona **"Blueprint"**
3. Busca tu repositorio **ARM-CUENTAS**
4. Rama: **main**
5. Click **"Create Blueprint Instance"**

### 5️⃣ Desplegar
Render detecta `render.yaml` automáticamente ✅

Revisa la configuración:
- Backend: `arm-cuentas-api` (Python 3.9)
- Frontend: `arm-cuentas-web` (Node 18)
- BD: `arm-cuentas-db` (PostgreSQL)
- Almacenamiento: `arm-cuentas-storage` (/var/data)

Click **"Deploy"** y espera 15-25 minutos ⏳

---

## 🎉 ¡LISTO!

Después del despliegue, tu app estará en:

```
🌐 https://arm-cuentas-web.onrender.com
🔌 API: https://arm-cuentas-api.onrender.com
📊 Docs: https://arm-cuentas-api.onrender.com/docs
```

**Login inicial:**
- Username: `admin`
- Password: `Admin123!`

---

## 🐛 Si algo falla

Ver logs en Render:
1. Click en servicio (backend/frontend)
2. Pestaña "Logs"
3. Busca el error

Errores comunes:
- `render.yaml not detected` → Debe estar en RAÍZ
- `DATABASE_URL not set` → Espera a que BD se cree
- `BUILD_FAILED` → Ver error completo en logs

---

## 📞 Documentación Completa

- **RENDER_BLUEPRINT.md** - Guía detallada paso a paso
- **PRE_DEPLOYMENT_CHECKLIST.md** - Lista de verificación
- **DEPLOYMENT.md** - Guía antigua (aún válida)

---

¿Necesitas ayuda? Lee **RENDER_BLUEPRINT.md**
