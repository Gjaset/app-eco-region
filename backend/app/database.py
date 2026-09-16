import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import NullPool
from app.config import settings

# En serverless (Vercel) las instancias se congelan entre requests: con un
# pool persistente las conexiones quedan rancias. NullPool abre/cierra por
# petición. En producción usa la URL del pooler (Neon/Supabase) si hay
# alta concurrencia.
_connect_args = {"connect_timeout": 10}
_engine_kwargs = {"pool_pre_ping": True}
if os.getenv("VERCEL"):
    _engine_kwargs = {"poolclass": NullPool, "connect_args": _connect_args}

# Create database engine
engine = create_engine(settings.DATABASE_URL, **_engine_kwargs)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()