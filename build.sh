#!/bin/bash
echo "🚀 Iniciando build en Render..."

# Instalar dependencias
echo "📦 Instalando dependencias..."
pip install -r requirements.txt

# Verificar si estamos en producción (Render)
if [ "$ENVIRONMENT" = "production" ]; then
    echo "🏭 Entorno de producción detectado"
    
    # Esperar a que la base de datos esté disponible
    echo "⏳ Esperando a que la base de datos esté disponible..."
    python -c "
import time
import psycopg2
import os

while True:
    try:
        conn = psycopg2.connect(os.getenv('DATABASE_URL'))
        conn.close()
        print('✅ Base de datos conectada exitosamente')
        break
    except Exception as e:
        print(f'⏳ Esperando conexión a BD: {e}')
        time.sleep(2)
"
    
    # Ejecutar migraciones si existen
    if [ -d "alembic" ]; then
        echo "🔄 Ejecutando migraciones de Alembic..."
        alembic upgrade head
    else
        echo "📊 Creando tablas iniciales..."
        python -c "
from main import startup_event
import asyncio
asyncio.run(startup_event())
"
    fi
    
    echo "✅ Build completado exitosamente"
else
    echo "🔧 Entorno de desarrollo detectado"
    echo "✅ Build completado"
fi
