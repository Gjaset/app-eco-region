"""Punto de entrada serverless para Vercel (proyecto con Root Directory = `backend`).

Vercel invoca `handler` en cada request; Mangum traduce el evento a ASGI y
reutiliza la misma `app` de FastAPI del desarrollo local. Sin este archivo
el desarrollo con Docker/uvicorn no cambia en nada.
"""

from mangum import Mangum

from app.main import app

handler = Mangum(app, lifespan="off")
