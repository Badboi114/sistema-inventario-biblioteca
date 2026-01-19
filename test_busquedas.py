#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para probar funcionalidad de búsqueda
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from inventario.models import Libro, TrabajoGrado

print("=" * 80)
print("PRUEBAS DE BUSQUEDA")
print("=" * 80)

# TEST 1: Buscar tesis RED-0006 (el que buscabas como "590")
print("\nTEST 1: Buscar tesis RED-0006")
print("-" * 80)
tesis = TrabajoGrado.objects.filter(codigo_nuevo='RED-0006').first()
if tesis:
    print(f"[OK] Encontrada: {tesis.codigo_nuevo} - {tesis.titulo[:60]}...")
else:
    print("[ERROR] NO encontrada")

# TEST 2: Buscar por parte del código
print("\nTEST 2: Buscar tesis que contengan 'RED'")
print("-" * 80)
tesis_red = TrabajoGrado.objects.filter(codigo_nuevo__icontains='RED')[:5]
print(f"Encontradas: {tesis_red.count()} tesis")
for t in tesis_red:
    print(f"  - {t.codigo_nuevo}: {t.titulo[:50]}...")

# TEST 3: Buscar por título
print("\nTEST 3: Buscar tesis por título (palabra 'RED')")
print("-" * 80)
tesis_titulo = TrabajoGrado.objects.filter(titulo__icontains='RED')[:5]
print(f"Encontradas: {tesis_titulo.count()} tesis")
for t in tesis_titulo:
    print(f"  - {t.codigo_nuevo}: {t.titulo[:50]}...")

# TEST 4: Buscar libros por código
print("\nTEST 4: Buscar libros por código (330)")
print("-" * 80)
libros = Libro.objects.filter(codigo_nuevo__icontains='330')[:5]
print(f"Encontrados: {libros.count()} libros")
for l in libros:
    print(f"  - {l.codigo_nuevo}: {l.titulo[:50]}...")

# TEST 5: Buscar libros por título
print("\nTEST 5: Buscar libros por título (palabra 'ECONOMIA')")
print("-" * 80)
libros_titulo = Libro.objects.filter(titulo__icontains='ECONOMIA')[:5]
print(f"Encontrados: {libros_titulo.count()} libros")
for l in libros_titulo:
    print(f"  - {l.codigo_nuevo}: {l.titulo[:50]}...")

# TEST 6: Buscar por autor
print("\nTEST 6: Buscar por autor (palabra 'GARCIA')")
print("-" * 80)
libros_autor = Libro.objects.filter(autor__icontains='GARCIA')[:5]
tesis_autor = TrabajoGrado.objects.filter(autor__icontains='GARCIA')[:5]
print(f"Libros: {libros_autor.count()}, Tesis: {tesis_autor.count()}")
if libros_autor.exists():
    for l in libros_autor:
        print(f"  Libro - {l.codigo_nuevo}: {l.autor} - {l.titulo[:40]}...")
if tesis_autor.exists():
    for t in tesis_autor:
        print(f"  Tesis - {t.codigo_nuevo}: {t.autor} - {t.titulo[:40]}...")

# TEST 7: Búsqueda combinada (código O título O autor)
print("\nTEST 7: Busqueda combinada (codigo='CPU' O titulo='SISTEMA' O autor='RODRIGUEZ')")
print("-" * 80)
from django.db.models import Q
resultados = Libro.objects.filter(
    Q(codigo_nuevo__icontains='CPU') | 
    Q(titulo__icontains='SISTEMA') | 
    Q(autor__icontains='RODRIGUEZ')
)[:10]
print(f"Encontrados: {resultados.count()} libros")
for r in resultados:
    print(f"  - {r.codigo_nuevo}: {r.titulo[:50]}...")

print("\n" + "=" * 80)
print("TODAS LAS PRUEBAS DE BUSQUEDA COMPLETADAS")
print("=" * 80)
