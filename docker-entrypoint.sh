#!/bin/sh
set -e

echo "=> Aplicando migrations..."
flask db upgrade || echo "Nenhuma migration pendente."

echo "=> Iniciando aplicação..."
exec "$@"