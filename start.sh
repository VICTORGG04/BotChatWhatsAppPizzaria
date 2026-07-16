#!/bin/sh
# Start.sh - Inicia gunicorn + celery worker+beat no mesmo container

echo "=== Iniciando PayPizzas Bot ==="

# Gera credentials.json se necessário
if [ -n "$GOOGLE_CREDENTIALS_B64" ] && [ ! -f credentials.json ]; then
    echo "$GOOGLE_CREDENTIALS_B64" | base64 -d > credentials.json 2>/dev/null && echo "credentials.json gerado" || echo "Falha ao gerar credentials.json"
fi

# Inicializa banco SQLite
python -c "from chatbot.storage.sqlite import setup_database; setup_database()"

# Inicia celery worker + beat (embutido) em background
echo "Iniciando celery worker + beat..."
celery -A celery_app worker -B -l WARNING -Q sheets,excel,database,default --concurrency=2 --scheduler celery.beat.PersistentScheduler &
CELERY_PID=$!

# Inicia gunicorn (web)
echo "Iniciando gunicorn na porta ${PORT:-5000}..."
gunicorn --bind 0.0.0.0:${PORT:-5000} --workers 2 --threads 2 --timeout 120 app:app &
GUNICORN_PID=$!

# Trap para desligamento gracioso
trap "kill $CELERY_PID $GUNICORN_PID 2>/dev/null; exit 0" SIGTERM SIGINT

echo "=== Pronto! PID gunicorn=$GUNICORN_PID, celery=$CELERY_PID ==="

# Aguarda algum processo terminar
wait
