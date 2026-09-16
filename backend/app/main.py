from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import auth, clientes, documents, drafts, formulario, ia, tramites, solicitudes, reportes
from app.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(formulario.router, prefix=settings.API_V1_STR)
app.include_router(drafts.router, prefix=settings.API_V1_STR)
app.include_router(ia.router, prefix=settings.API_V1_STR)
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(clientes.router, prefix=settings.API_V1_STR)
app.include_router(tramites.router, prefix=settings.API_V1_STR)
app.include_router(solicitudes.router, prefix=settings.API_V1_STR)
app.include_router(reportes.router, prefix=settings.API_V1_STR)
app.include_router(documents.router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    return {"message": "EcoRegión App API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}