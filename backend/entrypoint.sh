#!/bin/sh
# Entrypoint del backend: aplica migraciones antes de arrancar.
# Sin esto, en un equipo nuevo faltarían las tablas y fallaría auth/drafts/solicitudes.
set -e

echo "Aplicando migraciones de base de datos..."
alembic upgrade head
echo "Migraciones al día."

exec "$@"
