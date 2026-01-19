#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Validación de integridad de datos críticos
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from inventario.models import Libro, TrabajoGrado
from django.db.models import Count

print("=" * 80)
print("VALIDACION DE INTEGRIDAD DE DATOS CRITICOS")
print("=" * 80)

# 1. Verificar que todos los registros tengan código
print("\n1. REGISTROS CON CODIGO:")
print("-" * 80)
tesis_con_codigo = TrabajoGrado.objects.exclude(codigo_nuevo__isnull=True).exclude(codigo_nuevo='').count()
libros_con_codigo = Libro.objects.exclude(codigo_nuevo__isnull=True).exclude(codigo_nuevo='').count()
total_tesis = TrabajoGrado.objects.count()
total_libros = Libro.objects.count()

print(f"Tesis con codigo: {tesis_con_codigo}/{total_tesis}")
print(f"Libros con codigo: {libros_con_codigo}/{total_libros}")

if tesis_con_codigo == total_tesis:
    print("[OK] Todas las tesis tienen codigo")
else:
    print(f"[!] {total_tesis - tesis_con_codigo} tesis sin codigo")

if libros_con_codigo == total_libros:
    print("[OK] Todos los libros tienen codigo")
else:
    print(f"[!] {total_libros - libros_con_codigo} libros sin codigo")

# 2. Verificar que todos tengan título
print("\n2. REGISTROS CON TITULO:")
print("-" * 80)
tesis_con_titulo = TrabajoGrado.objects.exclude(titulo__isnull=True).exclude(titulo='').exclude(titulo='SIN TITULO').count()
libros_con_titulo = Libro.objects.exclude(titulo__isnull=True).exclude(titulo='').exclude(titulo='SIN TITULO').count()

print(f"Tesis con titulo valido: {tesis_con_titulo}/{total_tesis}")
print(f"Libros con titulo valido: {libros_con_titulo}/{total_libros}")

if tesis_con_titulo == total_tesis:
    print("[OK] Todas las tesis tienen titulo")
else:
    print(f"[INFO] {total_tesis - tesis_con_titulo} tesis con titulo generico o vacio")

if libros_con_titulo == total_libros:
    print("[OK] Todos los libros tienen titulo")
else:
    print(f"[INFO] {total_libros - libros_con_titulo} libros con titulo generico o vacio")

# 3. Verificar distribución por carreras (Tesis)
print("\n3. DISTRIBUCION DE TESIS POR CARRERA:")
print("-" * 80)
carreras = TrabajoGrado.objects.values('carrera').annotate(total=Count('id')).order_by('-total')[:10]
for c in carreras:
    carrera = c['carrera'] if c['carrera'] else 'SIN CARRERA'
    print(f"  {carrera}: {c['total']} tesis")

# 4. Verificar distribución por facultades (Libros)
print("\n4. DISTRIBUCION DE LIBROS POR FACULTAD:")
print("-" * 80)
facultades = Libro.objects.values('facultad').annotate(total=Count('id')).order_by('-total')[:10]
for f in facultades:
    facultad = f['facultad'] if f['facultad'] else 'SIN FACULTAD'
    print(f"  {facultad}: {f['total']} libros")

# 5. Verificar estado de los activos
print("\n5. DISTRIBUCION POR ESTADO:")
print("-" * 80)
print("Tesis:")
estados_tesis = TrabajoGrado.objects.values('estado').annotate(total=Count('id')).order_by('-total')
for e in estados_tesis:
    print(f"  {e['estado']}: {e['total']}")

print("\nLibros:")
estados_libros = Libro.objects.values('estado').annotate(total=Count('id')).order_by('-total')
for e in estados_libros:
    print(f"  {e['estado']}: {e['total']}")

# 6. Verificar años
print("\n6. RANGO DE AÑOS:")
print("-" * 80)
from django.db.models import Min, Max

anios_tesis = TrabajoGrado.objects.exclude(anio__isnull=True).aggregate(Min('anio'), Max('anio'))
anios_libros = Libro.objects.exclude(anio__isnull=True).aggregate(Min('anio'), Max('anio'))

print(f"Tesis: {anios_tesis['anio__min']} - {anios_tesis['anio__max']}")
print(f"Libros: {anios_libros['anio__min']} - {anios_libros['anio__max']}")

tesis_sin_anio = TrabajoGrado.objects.filter(anio__isnull=True).count()
libros_sin_anio = Libro.objects.filter(anio__isnull=True).count()
print(f"\nTesis sin año: {tesis_sin_anio}")
print(f"Libros sin año: {libros_sin_anio}")

# 7. Ejemplos aleatorios
print("\n7. EJEMPLOS ALEATORIOS:")
print("-" * 80)
print("\n3 Tesis aleatorias:")
for t in TrabajoGrado.objects.order_by('?')[:3]:
    print(f"  [{t.codigo_nuevo}] {t.titulo[:60]}...")
    print(f"      Autor: {t.autor or 'N/A'} | Carrera: {t.carrera or 'N/A'}")

print("\n3 Libros aleatorios:")
for l in Libro.objects.order_by('?')[:3]:
    print(f"  [{l.codigo_nuevo}] {l.titulo[:60]}...")
    print(f"      Autor: {l.autor or 'N/A'} | Editorial: {l.editorial or 'N/A'}")

print("\n" + "=" * 80)
print("VALIDACION COMPLETADA")
print("=" * 80)
