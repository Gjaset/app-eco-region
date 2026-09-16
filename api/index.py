import sys, os
# Ensure backend is on sys.path
sys.path.append('backend')
from app.main import app as fastapi_app

# The function that Vercel will invoke
async def __call__(event, context):
    # Mangum is used for ASGI on Vercel
    from mangum import Mangum
    handler = Mangum(fastapi_app)
    return handler(event, context)
