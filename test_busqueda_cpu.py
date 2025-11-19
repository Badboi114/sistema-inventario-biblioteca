#!/usr/bin/env python
"""
Script para probar la búsqueda de CPU en la API
"""
import requests

print("🔍 Probando búsqueda de 'CPU' en la API de Tesis...")
print()

try:
    response = requests.get('http://127.0.0.1:8000/api/tesis/?search=CPU')
    print(f"📡 Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Resultados encontrados: {len(data)}")
        print()
        
        if len(data) > 0:
            print("📋 Primeros 5 resultados:")
            for i, tesis in enumerate(data[:5], 1):
                print(f"  {i}. {tesis['codigo_nuevo']}: {tesis['titulo'][:60]}...")
        else:
            print("⚠️ No se encontraron resultados para 'CPU'")
    else:
        print(f"❌ Error en la API: {response.text}")
        
except requests.exceptions.ConnectionError:
    print("❌ ERROR: No se puede conectar al servidor backend.")
    print("   Asegúrate de que 'python manage.py runserver' esté corriendo.")
except Exception as e:
    print(f"❌ Error inesperado: {e}")

print()
print("🔎 Probando búsqueda directa en la base de datos...")
print()

# Verificar directamente en la base de datos
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_biblioteca.settings')
django.setup()

from inventario.models import TrabajoGrado

tesis_cpu = TrabajoGrado.objects.filter(codigo_nuevo__icontains='CPU')
print(f"📊 Tesis con 'CPU' en base de datos: {tesis_cpu.count()}")

if tesis_cpu.exists():
    print()
    print("📋 Primeros 5 de la base de datos:")
    for i, t in enumerate(tesis_cpu[:5], 1):
        print(f"  {i}. {t.codigo_nuevo}: {t.titulo[:60]}...")
