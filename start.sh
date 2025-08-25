#!/bin/bash

echo "🚀 Iniciando API de Microcréditos..."

# Verificar si el entorno virtual existe
if [ ! -d ".venv" ]; then
    echo "📦 Creando entorno virtual..."
    python3 -m venv .venv
fi

# Activar entorno virtual
echo "🔧 Activando entorno virtual..."
source .venv/bin/activate

# Instalar dependencias
echo "📚 Instalando dependencias..."
pip install -r requirements.txt

# Verificar si PostgreSQL está ejecutándose
echo "🗄️  Verificando conexión a PostgreSQL..."
if ! pg_isready -h localhost -p 5432 > /dev/null 2>&1; then
    echo "❌ PostgreSQL no está ejecutándose. Por favor, inicia PostgreSQL primero."
    echo "   En Arch Linux: sudo systemctl start postgresql"
    echo "   En Ubuntu/Debian: sudo systemctl start postgresql"
    exit 1
fi

echo "✅ PostgreSQL está ejecutándose"

# Crear base de datos si no existe
echo "🗃️  Verificando base de datos..."
psql -h localhost -U postgres -c "SELECT 1 FROM pg_database WHERE datname='microcreditos'" | grep -q 1
if [ $? -ne 0 ]; then
    echo "📊 Creando base de datos 'microcreditos'..."
    psql -h localhost -U postgres -c "CREATE DATABASE microcreditos;"
fi

# Inicializar base de datos con datos de ejemplo
echo "🎯 Inicializando base de datos..."
python scripts/init_db.py

# Iniciar la aplicación
echo "🌐 Iniciando la aplicación..."
echo "📖 Documentación disponible en: http://localhost:8000/docs"
echo "🔍 API disponible en: http://localhost:8000"
echo ""
echo "Presiona Ctrl+C para detener la aplicación"
echo ""

uvicorn main:app --reload --host 0.0.0.0 --port 8000
