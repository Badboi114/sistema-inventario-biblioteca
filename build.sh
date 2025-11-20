#!/usr/bin/env bash
# Script de construcción para Render
# Este script se ejecuta automáticamente cada vez que se despliega el proyecto

# Salir inmediatamente si algún comando falla
set -o errexit

# Instalar todas las dependencias de Python
echo "📦 Instalando dependencias..."
pip install -r requirements.txt

# Recolectar archivos estáticos (CSS, JS, imágenes del admin de Django)
echo "🎨 Recolectando archivos estáticos..."
python manage.py collectstatic --no-input

# Aplicar todas las migraciones a la base de datos PostgreSQL
echo "🗄️ Aplicando migraciones a PostgreSQL..."
python manage.py migrate

echo "✅ Build completado exitosamente!"
