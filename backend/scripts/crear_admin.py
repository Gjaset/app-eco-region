"""Crea o actualiza un usuario administrador.

Uso (con docker):
    docker compose exec backend python scripts/crear_admin.py --email admin@admin.com --password admin

Uso (desarrollo local, desde ./backend):
    uv run python scripts/crear_admin.py --email admin@admin.com --password admin

Requiere que las migraciones estén aplicadas (`alembic upgrade head`).
Es idempotente: si el email ya existe, actualiza nombre, contraseña y rol.
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import select
from sqlalchemy.exc import OperationalError

from app.config import settings
from app.core.seguridad import hash_password
from app.database import SessionLocal
from app.models.usuario import Usuario


def main() -> None:
    parser = argparse.ArgumentParser(description="Crea o actualiza un administrador.")
    parser.add_argument("--email", required=True, help="Email del administrador")
    parser.add_argument("--password", required=True, help="Contraseña (mínimo 8 caracteres)")
    parser.add_argument("--nombre", default="Administrador", help="Nombre a mostrar")
    args = parser.parse_args()

    if len(args.password) < 8:
        parser.error("La contraseña debe tener al menos 8 caracteres.")

    db = SessionLocal()
    try:
        usuario = db.scalar(select(Usuario).where(Usuario.email == args.email.lower()))
        if usuario is None:
            usuario = Usuario(email=args.email.lower(), nombre=args.nombre)
            db.add(usuario)
        usuario.nombre = args.nombre
        usuario.password_hash = hash_password(args.password)
        usuario.rol = "admin"
        usuario.activo = True
        db.commit()
        db.refresh(usuario)
        print(f"OK: {usuario.email} (id={usuario.id}, rol={usuario.rol})")
    except OperationalError:
        print(
            "ERROR: no se pudo conectar a la base de datos.\n"
            f"Revisa DATABASE_URL (actual: {settings.DATABASE_URL}).\n"
            "Con Docker: `docker compose up -d db`. En local ajusta backend/.env.",
            file=sys.stderr,
        )
        raise SystemExit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()
