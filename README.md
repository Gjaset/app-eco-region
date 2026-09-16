# EcoRegión App

Plataforma web para automatizar la gestión del permiso de **Aprovechamiento Forestal** de la empresa **ECO REGIÓN SAS BIC** (consultora ambiental colombiana).

## Descripción

EcoRegión App reemplaza el proceso manual (WhatsApp + correos + Word) con un formulario guiado, normalización automática de datos y generación del documento técnico Word listo para radicar ante la CAR o la SDA.

## Stack Técnico

| Capa | Tecnología |
|------|------------|
| Backend API | Python 3.12 + FastAPI + Uvicorn |
| ORM / DB | SQLAlchemy 2.0 + PostgreSQL 16 |
| Migraciones | Alembic (se aplican solas al arrancar el backend) |
| Auth | JWT + Argon2 (`pwdlib`) |
| Generación Word | `docxtpl` (Jinja2 sobre plantilla .docx) |
| Relleno PDF | `pypdf` + `reportlab` sobre la plantilla oficial FUN |
| Fuzzy matching | `rapidfuzz` (municipios y especies) |
| Asistente IA | Nvidia OpenAI-compatible Chat Completions |
| Frontend | React 18 + Vite + TypeScript + Tailwind CSS (Node 20+) |
| Contenedores | Docker + Docker Compose |
| Testing | Pytest + pytest-asyncio |

## Inicio rápido (recomendado: Docker)

### Prerrequisitos

- Docker y Docker Compose
- Git
- Opcional: API key de Nvidia (el asistente usa una respuesta determinista si no está configurada)

### Paso a Paso

1. Clonar el repositorio:
   ```bash
   git clone <repository-url>
   cd ecoregionapp
   ```

2. Configurar variables de entorno (solo la primera vez):
   ```bash
   cp backend/.env.example backend/.env
   cp frontend/.env.example frontend/.env   # opcional: ya trae valores por defecto
   # Editar backend/.env con tus valores reales (SECRET_KEY, NVIDIA_API_KEY, ...)
   ```

3. Construir y levantar todo (las migraciones de BD corren automáticamente):
   ```bash
   docker compose up --build
   ```

4. Crear el usuario administrador (solo la primera vez):
   ```bash
   docker compose exec backend python scripts/crear_admin.py --email admin@admin.com --password <clave-de-8+-caracteres>
   ```

5. Abrir:
   - Frontend: http://localhost:5173 (regístrate o inicia sesión)
   - Backend: http://localhost:8000 (docs interactivas en http://localhost:8000/docs)

> Sin `backend/.env` el backend usa valores de desarrollo. Sin `NVIDIA_API_KEY`
> el asistente IA responde con orientación determinista. Sin admin creado,
> regístrate por la UI (rol `cliente`) y promueve con el script de arriba.

## Estructura del Proyecto

```
ecoregionapp/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── core/
│   │   │   ├── normalizacion/      # municipios, especies, coordenadas, tipo
│   │   │   ├── reglas/             # car_selector, requisitos
│   │   │   ├── generacion/         # documento_word (docx), fun_pdf (PDF oficial)
│   │   │   ├── drafts.py           # fallback en memoria para borradores
│   │   │   ├── solicitudes.py      # persistencia de copias exportadas
│   │   │   └── seguridad.py        # JWT + Argon2 + guards de rol
│   │   ├── api/routes/             # auth, formulario, drafts, ia, clientes, tramites, solicitudes
│   │   ├── models/                 # usuario, tramite, draft, solicitud
│   │   └── schemas/                # auth, formulario, fun, drafts, ia, tramites, solicitudes
│   ├── data/                       # datasets DANE/IDEAM (solo lectura)
│   ├── templates/                  # fun_template.pdf + plantilla docx
│   ├── generated/                  # copias exportadas (ignorado por git, se crea solo)
│   ├── scripts/crear_admin.py      # crea/actualiza el administrador
│   ├── tests/  +  alembic/  +  requirements.txt  +  Dockerfile  +  entrypoint.sh  +  .env.example
├── frontend/
│   ├── src/
│   │   ├── components/             # comunes (Navbar, Footer, AIAssistant) + formulario + formatos
│   │   ├── pages/                  # Main, FormularioFUN, FormCAR, Formatos, auth, admin, MisSolicitudes
│   │   ├── context/AuthContext.tsx # sesión JWT contra el backend
│   │   ├── hooks/                  # useDraftSync, useTramiteWizard
│   │   └── services/api.ts         # cliente HTTP con interceptor Bearer
│   ├── package.json  +  vite.config.ts  +  Dockerfile  +  entrypoint.sh  +  .env.example
├── docker-compose.yml
└── README.md
```

## Variables de entorno (referencia)

### Prerrequisitos por modo

- **Docker (recomendado):** solo Docker + Docker Compose + Git.
- **Desarrollo local:** Python 3.12 (+ `uv`), Node.js 20+ y npm, PostgreSQL accesible.
- Opcional: API key de Nvidia (sin ella, el asistente responde de forma determinista).

### Paso a Paso (detalle, ya cubierto en el inicio rápido)

1. Clonar el repositorio:
   ```bash
   git clone <repository-url>
   cd ecoregionapp
   ```

2. Configurar variables de entorno:
   ```bash
   cp backend/.env.example backend/.env
   # Editar backend/.env con tus valores reales
   ```
   Variables del backend:
   - `NVIDIA_API_KEY`: clave opcional de Nvidia.
   - `NVIDIA_API_URL`: endpoint compatible con OpenAI (por defecto `https://integrate.api.nvidia.com/v1/chat/completions`).
   - `NVIDIA_MODEL`: modelo a utilizar (por defecto `openai/gpt-oss-20b`).
   - `CORS_ORIGINS`, `DATABASE_URL`, `SECRET_KEY`, `DATA_PATH`, `TEMPLATES_PATH` y `GENERATED_PATH`: configuración de la aplicación.
   - En producción (`APP_ENV=production`) el backend **exige** un `SECRET_KEY` real y falla al arrancar si es el valor de ejemplo.

3. Construir y levantar los contenedores:
   ```bash
   docker-compose up --build
   ```

4. El backend estará disponible en: http://localhost:8000
5. El frontend estará disponible en: http://localhost:5173

> Si vienes de una versión anterior: `docker compose build backend` para
> reconstruir la imagen con las dependencias actuales.

## Desarrollo local (sin Docker)

### Backend

Requiere Python 3.12 y un PostgreSQL accesible. La forma más simple es usar
solo la BD de Docker y correr el backend en local:

```bash
docker compose up -d db
cd backend
cp .env.example .env   # y ajusta DATABASE_URL:
# DATABASE_URL=postgresql://admin:admin@localhost:5432/ecoregion_db
uv sync
uv run alembic upgrade head
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Crear el admin (con el backend corriendo o no, pero con BD arriba):

```bash
cd backend
uv run python scripts/crear_admin.py --email admin@admin.com --password <clave-de-8+-caracteres>
```

### Frontend

Requiere Node.js 20+ y npm:

```bash
cd frontend
cp .env.example .env   # opcional
npm install --legacy-peer-deps
npm run dev
```

## Testing

Ejecutar los tests (desde la raíz, sin necesidad de Docker ni Postgres: usan SQLite en memoria):

```bash
uv run pytest -q
```

Chequeo de tipos del frontend:

```bash
cd frontend && npx tsc --noEmit
```

La aplicación incluye el flujo MVP de normalización, confirmación manual,
checklist de anexos por autoridad y generación del documento Word. La plantilla
de desarrollo disponible es `backend/templates/aprovechamiento_forestal_fixed.docx`.

El Formulario Único Nacional se exporta en PDF sobre la plantilla oficial
(`backend/templates/fun_template.pdf`) mediante `POST /api/formulario/fun/exportar-pdf`
(requiere login). Cada exportación guarda una copia asociada al usuario
(`backend/generated/`, tabla `solicitudes`).

Los borradores se guardan con versión entera mediante `GET`/`PUT
/api/formulario/drafts/{draft_id}`. Una escritura con una versión antigua recibe
`409`; la interfaz muestra el conflicto y conserva los cambios locales. Cuando
la API no está disponible, usa `localStorage` y `BroadcastChannel` como respaldo.
El almacenamiento primario es la tabla `drafts` en Postgres; el store en memoria
solo actúa como fallback si la BD no está disponible.

Autenticación JWT con roles `admin` / `consultor` / `cliente`. La descarga de
documentos requiere sesión; cada usuario ve su historial en “Mis solicitudes” y
el admin ve todo, filtra por usuario y descarga ZIP (`{Usuario}_{AAAAMMDD_HHMM}.zip`).

El asistente está disponible desde el botón flotante. `POST /api/ia/chat` llama
al endpoint Nvidia mediante `httpx`, con timeout y logging; sin configuración o
ante un error responde de forma segura con una orientación determinista.

## API Endpoints

- `POST /api/formulario/normalizar` - Normaliza los datos del formulario
- `POST /api/formulario/generar-documento` - Genera el documento Word (requiere login, guarda copia)
- `POST /api/formulario/fun/exportar-pdf` - Rellena el FUN oficial en PDF (requiere login, guarda copia)
- `GET /api/formulario/drafts/{draft_id}` - Lee un borrador versionado
- `PUT /api/formulario/drafts/{draft_id}` - Guarda un borrador con concurrencia optimista
- `POST /api/ia/chat` - Asistente IA Nvidia con fallback seguro
- `POST /api/auth/register` - Registro (rol `cliente` por defecto)
- `POST /api/auth/login` - Login OAuth2, devuelve JWT
- `GET /api/auth/me` - Perfil del usuario autenticado
- `GET /api/auth/usuarios` - Lista usuarios (solo admin)
- `PATCH /api/auth/usuarios/{id}` - Cambia rol/activo (solo admin)
- `DELETE /api/auth/usuarios/{id}` - Elimina usuario (solo admin)
- `GET /api/solicitudes/mias` - Historial propio ordenado con fecha y hora
- `GET /api/solicitudes` - Todas las solicitudes, filtro `?usuario_id=` (solo admin)
- `GET /api/solicitudes/{id}/descargar` - Descarga una copia (propia o admin)
- `GET /api/solicitudes/descargar-zip?ids=1,2` - ZIP múltiple (propias o admin)
- `GET/POST /api/clientes`, `GET/POST/PATCH /api/tramites` - Gestión interna (roles `admin`/`consultor`)
- `POST /api/ia/agente` - Agente IA con candado temático CAR/SDA/Corpoboyacá

## Despliegue en Vercel

Son **dos proyectos Vercel** (Vercel no corre Docker ni Postgres local):

| Proyecto | Root Directory | Qué hace |
|---|---|---|
| `ecoregion-front` | `frontend` | React + Vite estático (`frontend/vercel.json` trae los rewrites SPA) |
| `ecoregion-back` | `backend` | FastAPI en serverless vía `backend/api/index.py` (Mangum). `backend/vercel.json` redirige todo al handler |

### 1. Base de datos (Neon o Supabase)

Crea un Postgres externo y usa su URL **del pooler** (imprescindible en serverless):

```bash
# Desde backend/ (alembic.ini vive ahí), con la URL de producción:
cd backend
DATABASE_URL="postgresql://usuario:clave@pooler.neon.tech:5432/db" uv run alembic upgrade head
DATABASE_URL="..." uv run python scripts/crear_admin.py --email admin@tudominio.com --password <clave-8+>
```

Las migraciones **no** corren en Vercel: se aplican una vez desde local antes de desplegar (la migración `0005` guarda los documentos en la DB, por eso Vercel no necesita disco).

### 2. Variables en cada proyecto (dashboard → Settings → Environment Variables)

Backend (`ecoregion-back`):
- `DATABASE_URL` (pooler), `SECRET_KEY` (secreto real, `APP_ENV=production`)
- `CORS_ORIGINS=https://ecoregion-front.vercel.app` (tu dominio del front)
- `NVIDIA_API_KEY`, `NVIDIA_MODEL=openai/gpt-oss-20b` (opcional, el agente degrada sin ellas)

Frontend (`ecoregion-front`):
- `VITE_API_BASE_URL=https://ecoregion-back.vercel.app/api`

### 3. Notas serverless

- Con `VERCEL=1` (lo pone Vercel solo) el backend usa `NullPool` y omite el disco: las copias van a la columna `contenido` (migración `0005`). La `0006` añade `estado` a las solicitudes para el panel admin.
- Cold starts de ~2-5 s en el primer request; el resto va normal.
- Límite de función: se eliminó `pandas` (no se usaba) para caber en los 250 MB.

### 4. Plantillas de formularios (XLSX / DOCX)

Las plantillas oficiales (F1, F2, FGR-06, FGR-29, F3) viven en `frontend/public/formatos/` y **se sirven como estáticos** desde el frontend (se copian a `dist/formatos/` en el build). El editor en pantalla las carga, permite diligenciarlas y las exporta **preservando los logos** (se parchea el XML interno, no se regenera el archivo).

Las librerías más pesadas (`docx-preview`, `react-pdf`, `pdfjs-dist`) se cargan **bajo demanda** (lazy-load) para no inflar el bundle inicial.

### 5. Formato Único Nacional (FUN, PDF)

El `fun_template.pdf` vive en `backend/templates/` y se resuelve por `__file__`, así que viaja dentro de la función serverless sin configuración extra.

## Licencia

Este proyecto es un prototipo académico de uso demostrativo y se distribuye bajo una licencia privada. No constituye una plataforma oficial para la radicación, gestión o seguimiento de trámites legales o administrativos, y sus autores no se hacen responsables por decisiones, solicitudes, documentos o consecuencias derivadas de su uso.

El código, los diseños, las plantillas y los demás recursos del proyecto están protegidos por la legislación aplicable. Cualquier modificación, copia, descarga, publicación, distribución o divulgación no autorizada puede generar consecuencias legales. Para utilizar, adaptar o redistribuir este proyecto, se debe contar previamente con la autorización expresa de sus titulares.