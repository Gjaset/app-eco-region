#!/bin/sh
# Entrypoint script para instalar dependencias si el volumen node_modules está vacío

set -e

echo "Verificando node_modules en el volumen..."

if [ ! -d "/app/node_modules" ] || [ -z "$(ls -A /app/node_modules)" ]; then
    echo "Volumen node_modules vacío, instalando dependencias..."
    npm install --legacy-peer-deps
    echo "Dependencias instaladas correctamente"
else
    echo "node_modules ya existe, verificando integridad..."
    # Verificar que las dependencias principales estén instaladas
    if [ ! -d "/app/node_modules/docx" ] || \
       [ ! -d "/app/node_modules/xlsx" ] || \
       [ ! -d "/app/node_modules/file-saver" ] || \
       [ ! -d "/app/node_modules/docx-preview" ] || \
       [ ! -d "/app/node_modules/react-pdf" ] || \
       [ ! -d "/app/node_modules/pdfjs-dist" ]; then
        echo "Faltan dependencias críticas, reinstalando..."
        rm -rf /app/node_modules
        npm install --legacy-peer-deps
    else
        echo "Dependencias OK"
    fi
fi

# Ejecutar comando original
exec "$@"