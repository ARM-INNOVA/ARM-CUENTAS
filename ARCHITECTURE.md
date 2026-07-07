# 🏗️ ARQUITECTURA DE ARM CUENTAS

## Diagrama General

```
┌─────────────────────────────────────────────────────────────────┐
│                          USUARIO FINAL                          │
└──────────────────────────┬──────────────────────────────────────┘
                           │
         ┌─────────────────┼─────────────────┐
         │                 │                 │
    ┌────▼────┐       ┌────▼────┐      ┌────▼────┐
    │  MOBILE  │       │ DESKTOP │      │  TABLET │
    │  (PWA)   │       │(Browser)│      │(Browser)│
    └────┬────┘       └────┬────┘      └────┬────┘
         │                 │                 │
         └─────────────────┼─────────────────┘
                           │
                    ┌──────▼──────┐
                    │ React + Vite │
                    │   Frontend   │
                    │ (Localhost   │
                    │   :5173)     │
                    └──────┬──────┘
                           │ API HTTP
                    ┌──────▼──────┐
        ┌───────────┤  FastAPI    ├──────────┐
        │           │   Backend   │          │
        │           │ (Localhost  │          │
        │           │   :8000)    │          │
        │           └──────┬──────┘          │
        │                  │                 │
   ┌────▼────┐      ┌──────▼──────┐   ┌────▼─────┐
   │ PyJWT    │      │ SQLAlchemy  │   │ PyPDF2 + │
   │ AUTH     │      │    ORM      │   │Tesseract │
   │          │      │             │   │  (OCR)   │
   └──────────┘      └──────┬──────┘   └──────────┘
                            │
                      ┌─────▼──────┐
                      │ PostgreSQL  │
                      │  Database   │
                      │ (Port 5432) │
                      └─────┬──────┘
                            │
              ┌─────────────┼─────────────┐
              │             │             │
         ┌────▼──┐     ┌───▼───┐  ┌──────▼─────┐
         │ Users │     │Obras  │  │ Movements  │
         └───────┘     └───────┘  └────────────┘
              │             │             │
         ┌────▼──┐     ┌───▼───┐  ┌──────▼─────┐
         │ Auth  │     │ Files │  │Categories  │
         └───────┘     └───────┘  └────────────┘
                             │
                             │
                      ┌──────▼──────┐
                      │  /uploads/   │
                      │ (PDF, JPG)   │
                      └──────────────┘
```

## Flujo de Datos - Login

```
Usuario                Frontend                Backend              BD
   │                      │                        │                 │
   │ Email + Pass         │                        │                 │
   ├─────────────────────>│                        │                 │
   │                      │ POST /api/auth/login  │                 │
   │                      ├──────────────────────>│                 │
   │                      │                      │ SELECT user     │
   │                      │                      ├────────────────>│
   │                      │                      │<────────────────┤
   │                      │                      │ Validar pass    │
   │                      │                      │ Crear JWT       │
   │                      │<──────────────────────┤                 │
   │ JWT + User Info      │                        │                 │
   │<─────────────────────┤                        │                 │
   │ Guardar JWT          │                        │                 │
   │ en localStorage      │                        │                 │
   │                      │                        │                 │
```

## Flujo de Datos - Subida de Factura

```
Usuario            Frontend           Backend             DB          Archivo
   │                  │                  │                │              │
   │ Arrastra PDF     │                  │                │              │
   ├─────────────────>│                  │                │              │
   │                  │ POST /api/files/upload (con JWT) │              │
   │                  ├─────────────────>│                │              │
   │                  │                  │ Validar       │              │
   │                  │                  │ - Tamaño      │              │
   │                  │                  │ - Tipo        │              │
   │                  │                  │ - Token       │              │
   │                  │                  ├──────────────>│ Guardar     │
   │                  │                  │<──────────────┤             │
   │                  │                  │ Leer PDF      │              │
   │                  │                  ├──────────────────────────────>│
   │                  │                  │<──────────────────────────────┤
   │                  │                  │ Extraer texto                  │
   │                  │                  │ con PyPDF2                     │
   │                  │                  │                               │
   │                  │                  │ Si texto vacío → OCR           │
   │                  │                  │ Parsing de datos              │
   │                  │                  │ (fecha, monto, NIF)           │
   │                  │                  │ Guardar metadata  │             │
   │                  │                  ├──────────────────┤             │
   │                  │                  │<────────────────┤             │
   │ Datos Extraídos  │                  │                              │
   │ + Archivo        │<─────────────────┤                              │
   │ Revisar datos    │                  │                              │
```

## Flujo de Datos - Dashboard

```
Usuario            Frontend           Backend             DB
   │                  │                  │                 │
   │ Click Dashboard  │                  │                 │
   ├─────────────────>│                  │                 │
   │                  │ GET /api/movements/dashboard/summary │
   │                  │ (con JWT)                           │
   │                  ├─────────────────>│                 │
   │                  │                  │ SELECT *        │
   │                  │                  │ FROM movements  │
   │                  │                  │ WHERE user_id   │
   │                  │                  ├────────────────>│
   │                  │                  │<────────────────┤
   │                  │                  │ Calcular:       │
   │                  │                  │ - Ingresos      │
   │                  │                  │ - Gastos        │
   │                  │                  │ - Beneficio     │
   │                  │                  │ - IVA           │
   │                  │ Tarjetas JSON    │                 │
   │ Dashboard        │<─────────────────┤                 │
   │ actualizado      │                  │                 │
   │<─────────────────┤                  │                 │
   │                  │                  │                 │
```

## Componentes Backend

```
┌──────────────────────────────────────────────────────────┐
│                      FastAPI App                         │
│  ┌────────────────────────────────────────────────────┐ │
│  │ Middleware (CORS, Auth)                           │ │
│  └────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────┐ │
│  │              Routes (7 módulos)                    │ │
│  ├─ /api/auth      (Login, Register)                  │ │
│  ├─ /api/movements (CRUD + Dashboard)                │ │
│  ├─ /api/obras     (CRUD + Summary)                  │ │
│  ├─ /api/files     (Upload, Extract)                 │ │
│  ├─ /api/categories (CRUD)                          │ │
│  ├─ /api/providers  (CRUD + Search)                 │ │
│  └─ /health        (Status check)                    │ │
│  └────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────┐ │
│  │          Services (Business Logic)                 │ │
│  ├─ UserService                                       │ │
│  ├─ MovementService (Calculations)                   │ │
│  ├─ CategoryService                                  │ │
│  ├─ ProviderService                                  │ │
│  └─ ObraService                                      │ │
│  └────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────┐ │
│  │              Utils & Tools                         │ │
│  ├─ JWT (create, verify, decode)                     │ │
│  ├─ Files (upload, sanitize, validate)              │ │
│  └─ InvoiceExtractor (OCR, parsing)                 │ │
│  └────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────┐ │
│  │       Database Layer (SQLAlchemy ORM)            │ │
│  └────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────┘
                         │
              ┌──────────▼──────────┐
              │    PostgreSQL       │
              │   7 Tables          │
              │   Relaciones 1:N    │
              └─────────────────────┘
```

## Componentes Frontend

```
┌──────────────────────────────────────────────────────────┐
│                    React App                            │
│  ┌────────────────────────────────────────────────────┐ │
│  │          App.jsx (Router)                         │ │
│  │  └─ LoginPage (/)                                │ │
│  │  └─ DashboardPage (/dashboard)                   │ │
│  │  └─ MovementsPage (/movements)                   │ │
│  │  └─ ObrasPage (/obras)                           │ │
│  │  └─ UploadInvoicePage (/upload)                  │ │
│  └────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────┐ │
│  │         Components (Reutilizables)               │ │
│  │  └─ Navbar (Barra de navegación)                 │ │
│  │  └─ Layout (Layout base)                         │ │
│  └────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────┐ │
│  │           State Management (Zustand)             │ │
│  │  └─ useAuthStore (user, token, login/logout)    │ │
│  │  └─ useMovementsStore (movements)                │ │
│  │  └─ useDashboardStore (summary)                  │ │
│  └────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────┐ │
│  │         Custom Hooks                             │ │
│  │  └─ useAuth (login logic)                        │ │
│  │  └─ useStore (state access)                      │ │
│  └────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────┐ │
│  │          API Client (Axios)                      │ │
│  │  Interceptadores para JWT                        │ │
│  │  Manejo de errores 401                           │ │
│  └────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────┐ │
│  │          Styles (Tailwind CSS)                   │ │
│  │  Responsive design                               │ │
│  │  Colores corporativos ARM                        │ │
│  └────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────┘
          ▲                                      │
          │              HTTP                   │
          │          JSON + JWT                 │
          └──────────────────────────────────────┘
```

## Base de Datos - Modelo Relacional

```
┌──────────────────┐     ┌────────────────┐
│     USERS        │     │  AUDIT_LOGS    │
├──────────────────┤     ├────────────────┤
│ id (PK)          │────>│ id (PK)        │
│ email            │     │ user_id (FK)   │
│ username         │     │ accion         │
│ hashed_password  │     │ entidad        │
│ role             │     │ cambios (JSON) │
│ is_active        │     │ timestamp      │
│ created_at       │     └────────────────┘
│ updated_at       │
│ last_login       │
└─────────┬────────┘
          │
          │ crea
          ▼
┌──────────────────┐
│   MOVEMENTS      │
├──────────────────┤
│ id (PK)          │
│ user_id (FK)     │────> USERS
│ obra_id (FK)     │────> OBRAS
│ categoria_id(FK) │────> CATEGORIES
│ proveedor_id(FK) │────> PROVIDERS
│ fecha            │
│ tipo             │(ingreso/gasto)
│ concepto         │
│ importe_total    │
│ iva_cantidad     │
│ iva_porcentaje   │
│ estado           │(pendiente/pagado)
│ forma_pago       │
│ numero_factura   │
│ created_at       │
│ updated_at       │
└─────────┬────────┘
          │
          │ contiene
          ▼
┌──────────────────┐
│    FILES         │
├──────────────────┤
│ id (PK)          │
│ movement_id (FK) │────> MOVEMENTS
│ nombre_original  │
│ nombre_guardado  │
│ tipo (MIME)      │
│ tamaño           │
│ ruta             │
│ datos_extraidos  │(JSON)
│ confianza        │(0-100)
│ necesita_revision│
│ created_at       │
└──────────────────┘

┌──────────────────┐
│    OBRAS         │
├──────────────────┤
│ id (PK)          │
│ nombre           │
│ cliente          │
│ direccion        │
│ estado           │(activa/pausada...)
│ fecha_inicio     │
│ fecha_fin        │
│ presupuesto      │
│ observaciones    │
│ created_at       │
│ updated_at       │
└──────────────────┘

┌─────────────────────┐
│   CATEGORIES        │
├─────────────────────┤
│ id (PK)             │
│ nombre              │
│ descripcion         │
│ color (hex)         │
│ activa              │
│ created_at          │
└─────────────────────┘

┌─────────────────────┐
│   PROVIDERS         │
├─────────────────────┤
│ id (PK)             │
│ nombre              │
│ nif_cif             │
│ email               │
│ telefono            │
│ direccion           │
│ tipo                │
│ activo              │
│ created_at          │
└─────────────────────┘
```

## Flujo Completo - Crear un Gasto

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. USUARIO SUBE FACTURA PDF                                     │
│    Frontend: UploadInvoicePage                                  │
│    └─ Drag & drop o click                                       │
└────────────┬────────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────────┐
│ 2. FRONTEND VALIDA Y ENVÍA                                      │
│    POST /api/files/upload                                       │
│    Encabezados: Authorization: Bearer {JWT_TOKEN}               │
│    Body: multipart/form-data {file}                             │
└────────────┬────────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────────┐
│ 3. BACKEND PROCESA                                              │
│    routes/files.py: upload_file()                               │
│    ├─ Verificar JWT token                                       │
│    ├─ Validar extensión (.pdf, .jpg, .png, .webp)              │
│    ├─ Validar tamaño (<50MB)                                    │
│    ├─ Crear nombre seguro (UUID)                                │
│    ├─ Guardar archivo en /uploads/                              │
│    └─ Enviar a InvoiceExtractor                                 │
└────────────┬────────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────────┐
│ 4. OCR Y EXTRACCIÓN (utils/invoice_extractor.py)                │
│    ├─ PyPDF2: Extraer texto del PDF                             │
│    ├─ Si no hay texto → Tesseract OCR                           │
│    ├─ Regex: Buscar:                                            │
│    │  ├─ Fecha (DD/MM/YYYY)                                     │
│    │  ├─ Número factura (N°, Factura:)                          │
│    │  ├─ NIF/CIF                                                │
│    │  ├─ Importes (€ o números con 2 decimales)                 │
│    │  └─ Porcentaje IVA                                         │
│    ├─ Detectar tipo (ingreso/gasto)                             │
│    └─ Calcular confianza (0-100)                                │
└────────────┬────────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────────┐
│ 5. GUARDAR METADATA EN BD                                       │
│    INSERT INTO files (...)                                      │
│    ├─ nombre_original: "Factura_Leroy_Merlin.pdf"               │
│    ├─ nombre_guardado: "UUID_timestamp.pdf"                     │
│    ├─ ruta: "/uploads/UUID_timestamp.pdf"                       │
│    ├─ datos_extraidos: { JSON con datos }                       │
│    └─ confianza_extraccion: 75                                  │
│                                                                 │
│    Relaciones BD:                                               │
│    ├─ Files.id = 42                                             │
│    └─ INSERT completed                                          │
└────────────┬────────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────────┐
│ 6. RESPUESTA AL FRONTEND                                        │
│    {                                                             │
│      "file_id": 42,                                              │
│      "nombre_original": "Factura.pdf",                           │
│      "tipo_detectado": "gasto",                                  │
│      "datos_extraidos": {                                        │
│        "fecha": "15/01/2024",                                    │
│        "numero_factura": "INV-2024-001",                         │
│        "importe_total": 150.50,                                  │
│        "iva_porcentaje": 21,                                     │
│        "confianza": 85                                           │
│      },                                                          │
│      "necesita_revision": false                                  │
│    }                                                             │
└────────────┬────────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────────┐
│ 7. FRONTEND MUESTRA FORMULARIO DE REVISIÓN                      │
│    ├─ Mostrar datos extraídos                                   │
│    ├─ Permitir editar                                           │
│    ├─ Selector de Obra                                          │
│    ├─ Selector de Categoría                                     │
│    └─ Botón "Guardar Movimiento"                                │
└────────────┬────────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────────┐
│ 8. USUARIO CONFIRMA DATOS Y SELECCIONA OBRA/CATEGORÍA           │
│    Frontend: POST /api/movements/                               │
│    {                                                             │
│      "fecha": "2024-01-15T00:00:00",                             │
│      "tipo": "gasto",                                            │
│      "concepto": "Materiales construcción",                      │
│      "obra_id": 5,                                               │
│      "categoria_id": 1,                                          │
│      "proveedor_id": 12,                                         │
│      "importe_total": 150.50,                                    │
│      "base_imponible": 124.47,                                   │
│      "iva_porcentaje": 21,                                       │
│      "iva_cantidad": 26.13,                                      │
│      "numero_factura": "INV-2024-001"                            │
│    }                                                             │
└────────────┬────────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────────┐
│ 9. BACKEND CREA MOVIMIENTO                                      │
│    services/movement_service.py: create_movement()              │
│    ├─ Validar datos con Pydantic                                │
│    ├─ Verificar permisos del usuario                            │
│    ├─ Calcular IVA si falta                                     │
│    ├─ INSERT INTO movements (...)                               │
│    └─ Actualizar relación con file                              │
└────────────┬────────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────────┐
│ 10. RESPUESTA: MOVIMIENTO CREADO                                │
│     {                                                            │
│       "id": 1234,                                                │
│       "fecha": "2024-01-15T00:00:00",                            │
│       "tipo": "gasto",                                           │
│       "importe_total": 150.50,                                   │
│       "estado": "pendiente",                                     │
│       "created_at": "2024-07-07T..."                             │
│     }                                                            │
└────────────┬────────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────────┐
│ 11. FRONTEND ACTUALIZA                                          │
│     ├─ Cerrar formulario                                        │
│     ├─ Mostrar confirmación                                     │
│     ├─ Actualizar lista de movimientos                          │
│     ├─ Refrescar dashboard                                      │
│     └─ Mostrar: "+150.50€ en gastos"                             │
└─────────────────────────────────────────────────────────────────┘
```

## Despliegue - Arquitectura en Render

```
┌────────────────────────────────────────────────────────────────┐
│                     RENDER CLOUD                               │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │ Frontend Static Site                                     │ │
│  │ ├─ Build: npm run build                                 │ │
│  │ ├─ Publish: dist/                                       │ │
│  │ └─ URL: https://arm-cuentas.onrender.com                │ │
│  └──────────────────────────────────────────────────────────┘ │
│                           │                                    │
│                      ┌────▼────┐                               │
│                      │ Usuarios │                              │
│                      └─────────┘                               │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │ Backend Web Service                                      │ │
│  │ ├─ Runtime: Python 3.9                                 │ │
│  │ ├─ Build: pip install -r requirements.txt             │ │
│  │ ├─ Start: gunicorn app.main:app                        │ │
│  │ └─ URL: https://arm-cuentas-api.onrender.com           │ │
│  └──────────────────────────────────────────────────────────┘ │
│                           │                                    │
│                      ┌────▼────┐                               │
│                      │ FastAPI │                              │
│                      └────┬────┘                               │
│                           │                                    │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │ PostgreSQL Database                                      │ │
│  │ ├─ Plan: Free (¡suficiente para pequeñas empresas!)    │ │
│  │ ├─ Credenciales: Guardadas como variables de env       │ │
│  │ └─ Backups: Automáticos (7 días)                       │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                 │
└────────────────────────────────────────────────────────────────┘
           │
           │ (Opcional)
           ▼
    ┌──────────────────┐
    │    AWS S3        │
    │  (Almacenamiento │
    │   de facturas)   │
    └──────────────────┘
```

---

Esta es la arquitectura completa de **ARM CUENTAS**. Cada componente se comunica de forma clara y eficiente. 🏗️
