"""Punto de entrada serverless para Vercel (proyecto con Root Directory = `backend`).

El runtime @vercel/python detecta la app ASGI `app` (FastAPI) y la invoca en
cada request; `backend/vercel.json` redirige todas las rutas a este archivo.
Mangum queda como fallback para runtimes tipo Lambda (AWS), no se usa en Vercel.
"""

from app.main import app  # noqa: F401 — Vercel invoca esta app ASGI

from mangum import Mangum

handler = Mangum(app, lifespan="off")
