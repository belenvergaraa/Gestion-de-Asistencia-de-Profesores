#!/bin/bash

echo "🚀 Iniciando Sistema de Gestión de Asistencia de Profesores..."
echo "========================================================"

# Verificar que Python esté instalado
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 no está instalado"
    exit 1
fi

# Verificar que las dependencias estén instaladas
echo "📦 Verificando dependencias..."
python3 -c "import flask, sqlite3, datetime" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  Instalando dependencias..."
    pip install --break-system-packages -r requirements.txt
fi

# Crear directorio de base de datos si no existe
mkdir -p database

echo "🗄️  Inicializando base de datos..."
echo "🌐 Iniciando servidor web..."
echo ""
echo "✅ Aplicación disponible en: http://localhost:5000"
echo "✅ Para detener el servidor, presiona Ctrl+C"
echo ""
echo "📝 Funcionalidades disponibles:"
echo "   • Registro de profesores: http://localhost:5000/register"
echo "   • Login: http://localhost:5000/login"
echo "   • Gestión de profesores: http://localhost:5000/gestionar_profesores"
echo "   • Reportes: http://localhost:5000/reportes"
echo ""

# Ejecutar la aplicación
python3 app.py