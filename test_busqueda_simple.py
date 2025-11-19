#!/usr/bin/env python
"""
Script simplificado para probar búsqueda de CPU
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_biblioteca.settings')
django.setup()

from inventario.models import TrabajoGrado
from django.db.models import Q

print("🔍 PRUEBA DE BÚSQUEDA DE 'CPU'")
print("=" * 60)
print()

# 1. Búsqueda directa en codigo_nuevo
print("1️⃣ Búsqueda directa en codigo_nuevo:")
tesis_codigo = TrabajoGrado.objects.filter(codigo_nuevo__icontains='CPU')
print(f"   Resultados: {tesis_codigo.count()}")
for t in tesis_codigo[:3]:
    print(f"   - {t.codigo_nuevo}: {t.titulo[:50]}...")
print()

# 2. Búsqueda con Q (como lo hace SearchFilter)
print("2️⃣ Búsqueda con Q (simulando SearchFilter):")
tesis_q = TrabajoGrado.objects.filter(
    Q(codigo_nuevo__icontains='CPU') |
    Q(titulo__icontains='CPU') |
    Q(autor__icontains='CPU') |
    Q(tutor__icontains='CPU') |
    Q(carrera__icontains='CPU') |
    Q(facultad__icontains='CPU') |
    Q(modalidad__icontains='CPU')
)
print(f"   Resultados: {tesis_q.count()}")
for t in tesis_q[:3]:
    print(f"   - {t.codigo_nuevo}: {t.titulo[:50]}...")
print()

# 3. Verificar valores exactos de CPU-001
print("3️⃣ Verificación detallada de CPU-001:")
try:
    cpu001 = TrabajoGrado.objects.get(codigo_nuevo='CPU-001')
    print(f"   ✅ ENCONTRADA")
    print(f"   Código: '{cpu001.codigo_nuevo}' (longitud: {len(cpu001.codigo_nuevo)})")
    print(f"   Título: {cpu001.titulo[:60]}...")
    print(f"   Autor: {cpu001.autor}")
    print(f"   Carrera: {cpu001.carrera}")
    print(f"   Facultad: {cpu001.facultad}")
    
    # Verificar caracteres ocultos
    codigo_repr = repr(cpu001.codigo_nuevo)
    print(f"   Código (repr): {codigo_repr}")
    
except TrabajoGrado.DoesNotExist:
    print("   ❌ NO ENCONTRADA")
print()

print("=" * 60)
print("✅ Prueba completada")
