#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para verificar integridad de datos entre Excel y Base de Datos
"""
import os
import django
import pandas as pd
from collections import Counter

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from inventario.models import Libro, TrabajoGrado

# Archivo Excel
EXCEL_FILE = 'BASE DE EXISTENCIA DE LIBROS, PROYECTOS DE GRADO, TESIS Y TRABAJO DIRIGIDO (2).xlsx'

print("=" * 80)
print("VERIFICACION DE INTEGRIDAD DE DATOS")
print("=" * 80)

# 1. CONTAR REGISTROS EN EXCEL
print("\n1. CONTEO EN EXCEL:")
print("-" * 80)

sheets_tesis = ['LISTA DE PROYECTOS DE GRADO (2)', 'Tabla7', 'LISTA DE PROYECTOS DE GRADO']
sheets_libros = ['LISTA DE LIBROS ACADEMICOS', 'LIBROS DE LECTURA', 'PARA REPORTE']

total_tesis_excel = 0
total_libros_excel = 0
codigos_tesis_excel = []
codigos_libros_excel = []

for sheet in sheets_tesis:
    df = pd.read_excel(EXCEL_FILE, sheet_name=sheet)
    count = len(df)
    total_tesis_excel += count
    # Obtener codigos (con espacio al final)
    if 'CODIGO NUEVO ' in df.columns:
        codigos = df['CODIGO NUEVO '].dropna().astype(str).str.strip().tolist()
        codigos_tesis_excel.extend(codigos)
    print(f"  {sheet}: {count} registros")

for sheet in sheets_libros:
    df = pd.read_excel(EXCEL_FILE, sheet_name=sheet)
    count = len(df)
    total_libros_excel += count
    # Obtener codigos
    if 'CODIGO NUEVO ' in df.columns:
        codigos = df['CODIGO NUEVO '].dropna().astype(str).str.strip().tolist()
        codigos_libros_excel.extend(codigos)
    print(f"  {sheet}: {count} registros")

print(f"\n  TOTAL Tesis en Excel: {total_tesis_excel}")
print(f"  TOTAL Libros en Excel: {total_libros_excel}")
print(f"  TOTAL GENERAL Excel: {total_tesis_excel + total_libros_excel}")

# 2. CONTAR REGISTROS EN BASE DE DATOS
print("\n2. CONTEO EN BASE DE DATOS:")
print("-" * 80)

total_tesis_bd = TrabajoGrado.objects.count()
total_libros_bd = Libro.objects.count()

print(f"  Tesis en BD: {total_tesis_bd}")
print(f"  Libros en BD: {total_libros_bd}")
print(f"  TOTAL GENERAL BD: {total_tesis_bd + total_libros_bd}")

# 3. VERIFICAR DUPLICADOS EN BD
print("\n3. VERIFICACION DE DUPLICADOS EN BD:")
print("-" * 80)

# Duplicados en Tesis
tesis_codigos = list(TrabajoGrado.objects.values_list('codigo_nuevo', flat=True))
tesis_duplicados = {codigo: count for codigo, count in Counter(tesis_codigos).items() if count > 1}

# Duplicados en Libros
libros_codigos = list(Libro.objects.values_list('codigo_nuevo', flat=True))
libros_duplicados = {codigo: count for codigo, count in Counter(libros_codigos).items() if count > 1}

if tesis_duplicados:
    print(f"  [!] DUPLICADOS en Tesis: {len(tesis_duplicados)} codigos duplicados")
    for codigo, count in list(tesis_duplicados.items())[:5]:
        print(f"      - {codigo}: {count} veces")
    if len(tesis_duplicados) > 5:
        print(f"      ... y {len(tesis_duplicados) - 5} mas")
else:
    print(f"  [OK] Sin duplicados en Tesis")

if libros_duplicados:
    print(f"  [!] DUPLICADOS en Libros: {len(libros_duplicados)} codigos duplicados")
    for codigo, count in list(libros_duplicados.items())[:5]:
        print(f"      - {codigo}: {count} veces")
    if len(libros_duplicados) > 5:
        print(f"      ... y {len(libros_duplicados) - 5} mas")
else:
    print(f"  [OK] Sin duplicados en Libros")

# 4. VERIFICAR CODIGOS UNICOS
print("\n4. CODIGOS UNICOS:")
print("-" * 80)

codigos_tesis_excel_unicos = set([c for c in codigos_tesis_excel if c and c != 'nan'])
codigos_libros_excel_unicos = set([c for c in codigos_libros_excel if c and c != 'nan'])
codigos_tesis_bd_unicos = set([c for c in tesis_codigos if c])
codigos_libros_bd_unicos = set([c for c in libros_codigos if c])

print(f"  Tesis - Codigos unicos en Excel: {len(codigos_tesis_excel_unicos)}")
print(f"  Tesis - Codigos unicos en BD: {len(codigos_tesis_bd_unicos)}")
print(f"  Libros - Codigos unicos en Excel: {len(codigos_libros_excel_unicos)}")
print(f"  Libros - Codigos unicos en BD: {len(codigos_libros_bd_unicos)}")

# 5. CODIGOS EN EXCEL PERO NO EN BD
print("\n5. CODIGOS FALTANTES EN BD:")
print("-" * 80)

tesis_faltantes = codigos_tesis_excel_unicos - codigos_tesis_bd_unicos
libros_faltantes = codigos_libros_excel_unicos - codigos_libros_bd_unicos

if tesis_faltantes:
    print(f"  [!] Tesis en Excel pero NO en BD: {len(tesis_faltantes)}")
    for codigo in list(tesis_faltantes)[:5]:
        print(f"      - {codigo}")
    if len(tesis_faltantes) > 5:
        print(f"      ... y {len(tesis_faltantes) - 5} mas")
else:
    print(f"  [OK] Todas las tesis del Excel estan en BD")

if libros_faltantes:
    print(f"  [!] Libros en Excel pero NO en BD: {len(libros_faltantes)}")
    for codigo in list(libros_faltantes)[:5]:
        print(f"      - {codigo}")
    if len(libros_faltantes) > 5:
        print(f"      ... y {len(libros_faltantes) - 5} mas")
else:
    print(f"  [OK] Todos los libros del Excel estan en BD")

# 6. CODIGOS EN BD PERO NO EN EXCEL
print("\n6. CODIGOS EXTRA EN BD (no deberian existir):")
print("-" * 80)

tesis_extra = codigos_tesis_bd_unicos - codigos_tesis_excel_unicos
libros_extra = codigos_libros_bd_unicos - codigos_libros_excel_unicos

if tesis_extra:
    print(f"  [!] Tesis en BD pero NO en Excel: {len(tesis_extra)}")
    for codigo in list(tesis_extra)[:5]:
        tesis = TrabajoGrado.objects.filter(codigo_nuevo=codigo).first()
        print(f"      - {codigo}: {tesis.titulo[:50] if tesis else 'N/A'}...")
    if len(tesis_extra) > 5:
        print(f"      ... y {len(tesis_extra) - 5} mas")
else:
    print(f"  [OK] No hay tesis extra en BD")

if libros_extra:
    print(f"  [!] Libros en BD pero NO en Excel: {len(libros_extra)}")
    for codigo in list(libros_extra)[:5]:
        libro = Libro.objects.filter(codigo_nuevo=codigo).first()
        print(f"      - {codigo}: {libro.titulo[:50] if libro else 'N/A'}...")
    if len(libros_extra) > 5:
        print(f"      ... y {len(libros_extra) - 5} mas")
else:
    print(f"  [OK] No hay libros extra en BD")

# 7. RESUMEN
print("\n" + "=" * 80)
print("RESUMEN:")
print("=" * 80)

diferencia_tesis = total_tesis_bd - len(codigos_tesis_excel_unicos)
diferencia_libros = total_libros_bd - len(codigos_libros_excel_unicos)

if diferencia_tesis == 0 and not tesis_duplicados and not tesis_faltantes and not tesis_extra:
    print("[OK] TESIS: Base de datos CORRECTA")
else:
    print(f"[!] TESIS: Requiere correccion")
    if tesis_duplicados:
        print(f"    - {len(tesis_duplicados)} codigos duplicados")
    if tesis_faltantes:
        print(f"    - {len(tesis_faltantes)} codigos faltantes")
    if tesis_extra:
        print(f"    - {len(tesis_extra)} codigos extra")

if diferencia_libros == 0 and not libros_duplicados and not libros_faltantes and not libros_extra:
    print("[OK] LIBROS: Base de datos CORRECTA")
else:
    print(f"[!] LIBROS: Requiere correccion")
    if libros_duplicados:
        print(f"    - {len(libros_duplicados)} codigos duplicados")
    if libros_faltantes:
        print(f"    - {len(libros_faltantes)} codigos faltantes")
    if libros_extra:
        print(f"    - {len(libros_extra)} codigos extra")

print("=" * 80)
