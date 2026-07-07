# ARM CUENTAS - Gestión de Ingresos, Gastos y Facturas

**ARM CUENTAS** es una aplicación web moderna para gestionar ingresos, gastos y facturas de empresas de reformas. Diseñada para ser sencilla, rápida y preparada para producción.

## 🎯 Características Principales

### Gestión de Movimientos
- ✅ Registro de ingresos y gastos
- ✅ Clasificación por obra, categoría y proveedor
- ✅ Control de estado (pendiente, pagado, cobrado)
- ✅ Formas de pago: efectivo, banco, tarjeta, transferencia, Bizum
- ✅ Cálculo automático de IVA

### Lectura de Facturas
- ✅ Subida de PDF, JPG, PNG y WEBP
- ✅ Extracción automática de datos
- ✅ OCR para PDFs sin texto
- ✅ Pantalla de revisión y corrección
- ✅ Detección de duplicados

### Gestión de Obras
- ✅ Crear y clasificar obras
- ✅ Resumen económico por obra
- ✅ Control de presupuesto
- ✅ Estados: activa, pausada, terminada, archivada

### Dashboard
- ✅ Resumen mensual y anual
- ✅ Ingresos, gastos y beneficio
- ✅ Cálculo de IVA
- ✅ Gráficos de evolución

### Exportaciones
- ✅ Excel y CSV
- ✅ Resúmenes por período, obra, categoría
- ✅ Descarga de facturas en ZIP

### Seguridad
- ✅ Autenticación multiusuario
- ✅ Roles: administrador, usuario, solo lectura
- ✅ Contraseñas cifradas
- ✅ Tokens JWT

### PWA
- ✅ Instalable en móvil y ordenador
- ✅ Funciona offline (básico)
- ✅ Responsive design

## 🚀 Despliegue en Render con Blueprint (Recomendado)

### ⚡ La forma más rápida (5 minutos)

1. **Sube a GitHub**
   ```bash
   git push origin main
   ```

2. **Abre Render**
   - Ve a https://render.com
   - Click "New +" → "Blueprint"
   - Conecta tu repositorio ARM-CUENTAS
   - Rama: main

3. **Render hace todo automáticamente**
   - ✅ Base de datos PostgreSQL
   - ✅ Backend FastAPI
   - ✅ Frontend React
   - ✅ Almacenamiento de facturas
   - ✅ HTTPS habilitado

4. **Listo en 15-20 minutos**
   - Tu app está en: `https://arm-cuentas-web.onrender.com`
   - Login: `admin` / `Admin123!`

**Ver guía completa:** [RENDER_BLUEPRINT.md](./RENDER_BLUEPRINT.md)

---

### Requisitos
- Python 3.9+
- Node.js 18+
- PostgreSQL 12+

### Instalación Backend

```bash
cd backend

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus datos

# Iniciar servidor
python -m uvicorn app.main:app --reload
```

Backend disponible en: http://localhost:8000

### Instalación Frontend

```bash
cd frontend

# Instalar dependencias
npm install

# Iniciar servidor de desarrollo
npm run dev
```

Frontend disponible en: http://localhost:5173

## 🐳 Despliegue en Render

Ver [DEPLOYMENT.md](./DEPLOYMENT.md) para instrucciones completas.

### Resumen Rápido

1. Push a GitHub
2. Conecta Render a tu repositorio
3. Configura PostgreSQL en Render
4. Agrega variables de entorno
5. Deploy automático al hacer push

## 📱 Uso de la Aplicación

### Para Administrador

1. **Crear usuarios**: Usuarios → Nuevo Usuario
2. **Crear categorías**: Configuración → Categorías
3. **Crear obras**: Obras → Nueva Obra
4. **Ver informes**: Informes → Seleccionar período

### Para Usuario

1. **Subir factura**: Pulsa "Subir Factura" o arrastra el PDF
2. **Revisar datos**: Corrige los datos extraídos
3. **Guardar**: Selecciona obra y categoría
4. **Ver movimientos**: Movimientos → Filtrar por período

### Para Solo Lectura

1. Puede ver todos los movimientos
2. Puede generar informes
3. No puede crear ni modificar nada

## 🛠️ Tecnologías

### Backend
- **Framework**: FastAPI
- **Base de datos**: PostgreSQL
- **ORM**: SQLAlchemy
- **Autenticación**: JWT
- **Validación**: Pydantic
- **Lectura PDF**: PyPDF2, pdfplumber, Tesseract

### Frontend
- **Framework**: React 18
- **Build**: Vite
- **Estilos**: Tailwind CSS
- **Routing**: React Router v6
- **State**: Zustand
- **HTTP**: Axios
- **Gráficos**: Chart.js

## 📊 Estructura de Archivos

```
arm-cuentas/
├── backend/
│   ├── app/
│   │   ├── main.py              # Aplicación FastAPI
│   │   ├── config.py            # Configuración
│   │   ├── database.py          # Base de datos
│   │   ├── models/              # Modelos SQLAlchemy
│   │   ├── routes/              # Rutas API
│   │   ├── schemas/             # Esquemas Pydantic
│   │   ├── services/            # Lógica de negocio
│   │   ├── utils/               # Utilidades
│   │   └── middleware/          # Middleware
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── App.jsx              # Componente principal
│   │   ├── main.jsx             # Entry point
│   │   ├── pages/               # Páginas
│   │   ├── components/          # Componentes
│   │   ├── services/            # Servicios API
│   │   ├── hooks/               # Custom hooks
│   │   └── styles/              # Estilos
│   ├── public/                  # Archivos estáticos
│   ├── package.json
│   └── vite.config.js
├── render.yaml                  # Configuración Render
└── README.md                    # Este archivo
```

## 🔐 Seguridad

- ✅ Contraseñas hasheadas con bcrypt
- ✅ Tokens JWT para autenticación
- ✅ Control de acceso por rol
- ✅ CORS configurado
- ✅ Validación de formularios
- ✅ Sanitización de nombres de archivo
- ✅ Límite de tamaño de archivo
- ✅ Solo tipos de archivo permitidos

## 📝 API Endpoints

### Autenticación
- `POST /api/auth/login` - Iniciar sesión
- `POST /api/auth/register` - Registrarse

### Movimientos
- `GET /api/movements/` - Listar movimientos
- `POST /api/movements/` - Crear movimiento
- `GET /api/movements/{id}` - Obtener movimiento
- `PUT /api/movements/{id}` - Actualizar movimiento
- `DELETE /api/movements/{id}` - Eliminar movimiento
- `GET /api/movements/dashboard/summary` - Resumen dashboard

### Obras
- `GET /api/obras/` - Listar obras
- `POST /api/obras/` - Crear obra
- `GET /api/obras/{id}` - Obtener obra
- `PUT /api/obras/{id}` - Actualizar obra
- `DELETE /api/obras/{id}` - Eliminar obra

### Archivos
- `POST /api/files/upload` - Subir archivo
- `GET /api/files/{id}` - Obtener información
- `GET /api/files/{id}/download` - Descargar archivo
- `POST /api/files/{id}/extract` - Extraer datos

## 🤝 Contribuciones

¡Las contribuciones son bienvenidas! Por favor:

1. Fork el proyecto
2. Crea una rama (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo licencia MIT.

## 📧 Soporte

Para soporte, por favor abre un issue en GitHub o contacta con el equipo de desarrollo.

---

**ARM CUENTAS** - Gestión simple y profesional de cuentas para reformas.