#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Análisis completo del Excel para entender las cantidades reales
"""
import pandas as pd

EXCEL_FILE = 'BASE DE EXISTENCIA DE LIBROS, PROYECTOS DE GRADO, TESIS Y TRABAJO DIRIGIDO (2).xlsx'

print("=" * 80)
print("ANÁLISIS DETALLADO DEL EXCEL")
print("=" * 80)

# Obtener todas las hojas
xl = pd.ExcelFile(EXCEL_FILE)
print(f"\nHOJAS EN EL EXCEL:")
for i, sheet in enumerate(xl.sheet_names, 1):
    print(f"  {i}. {sheet}")

print("\n" + "=" * 80)
print("ANÁLISIS POR HOJA:")
print("=" * 80)

sheets_tesis = ['LISTA DE PROYECTOS DE GRADO (2)', 'Tabla7', 'LISTA DE PROYECTOS DE GRADO']
sheets_libros = ['LISTA DE LIBROS ACADEMICOS', 'LIBROS DE LECTURA', 'PARA REPORTE']

total_registros_tesis = 0
total_registros_libros = 0
codigos_tesis_todos = []
codigos_libros_todos = []

# Analizar hojas de TESIS
print("\n--- HOJAS DE TESIS ---")
for sheet in sheets_tesis:
    df = pd.read_excel(EXCEL_FILE, sheet_name=sheet)
    total_filas = len(df)
    total_registros_tesis += total_filas
    
    print(f"\n{sheet}:")
    print(f"  Total filas: {total_filas}")
    
    if 'CODIGO NUEVO ' in df.columns:
        # Códigos no nulos
        codigos = df['CODIGO NUEVO '].dropna().astype(str).str.strip()
        codigos_validos = codigos[codigos != 'nan']
        codigos_tesis_todos.extend(codigos_validos.tolist())
        print(f"  Códigos no nulos: {len(codigos_validos)}")
        print(f"  Códigos únicos en esta hoja: {len(codigos_validos.unique())}")
        
        # Ver algunos ejemplos
        print(f"  Primeros 3 códigos: {codigos_validos.head(3).tolist()}")

# Analizar hojas de LIBROS
print("\n--- HOJAS DE LIBROS ---")
for sheet in sheets_libros:
    df = pd.read_excel(EXCEL_FILE, sheet_name=sheet)
    total_filas = len(df)
    total_registros_libros += total_filas
    
    print(f"\n{sheet}:")
    print(f"  Total filas: {total_filas}")
    
    if 'CODIGO NUEVO ' in df.columns:
        # Códigos no nulos
        codigos = df['CODIGO NUEVO '].dropna().astype(str).str.strip()
        codigos_validos = codigos[codigos != 'nan']
        codigos_libros_todos.extend(codigos_validos.tolist())
        print(f"  Códigos no nulos: {len(codigos_validos)}")
        print(f"  Códigos únicos en esta hoja: {len(codigos_validos.unique())}")
        
        # Ver algunos ejemplos
        print(f"  Primeros 3 códigos: {codigos_validos.head(3).tolist()}")

# RESUMEN FINAL
print("\n" + "=" * 80)
print("RESUMEN FINAL:")
print("=" * 80)

# Totales de filas
print(f"\n1. TOTAL DE FILAS (registros en Excel):")
print(f"   Tesis: {total_registros_tesis:,} filas")
print(f"   Libros: {total_registros_libros:,} filas")
print(f"   TOTAL: {total_registros_tesis + total_registros_libros:,} filas")

# Códigos únicos
codigos_tesis_unicos = set(codigos_tesis_todos)
codigos_libros_unicos = set(codigos_libros_todos)

print(f"\n2. CÓDIGOS ÚNICOS (sin duplicados):")
print(f"   Tesis: {len(codigos_tesis_unicos):,} códigos únicos")
print(f"   Libros: {len(codigos_libros_unicos):,} códigos únicos")
print(f"   TOTAL: {len(codigos_tesis_unicos) + len(codigos_libros_unicos):,} códigos únicos")

# Duplicados
duplicados_tesis = len(codigos_tesis_todos) - len(codigos_tesis_unicos)
duplicados_libros = len(codigos_libros_todos) - len(codigos_libros_unicos)

print(f"\n3. DUPLICADOS EN EL EXCEL:")
print(f"   Tesis: {duplicados_tesis} códigos duplicados")
print(f"   Libros: {duplicados_libros} códigos duplicados")

# Encontrar algunos duplicados
if duplicados_tesis > 0:
    from collections import Counter
    conteo_tesis = Counter(codigos_tesis_todos)
    dups_tesis = [(k, v) for k, v in conteo_tesis.items() if v > 1]
    print(f"\n   Ejemplos de códigos de tesis duplicados:")
    for codigo, veces in sorted(dups_tesis, key=lambda x: x[1], reverse=True)[:5]:
        print(f"     - {codigo}: {veces} veces")

if duplicados_libros > 0:
    from collections import Counter
    conteo_libros = Counter(codigos_libros_todos)
    dups_libros = [(k, v) for k, v in conteo_libros.items() if v > 1]
    print(f"\n   Ejemplos de códigos de libros duplicados:")
    for codigo, veces in sorted(dups_libros, key=lambda x: x[1], reverse=True)[:10]:
        print(f"     - {codigo}: {veces} veces")

print("\n" + "=" * 80)
print("CONCLUSIÓN:")
print("=" * 80)
print(f"""
El Excel contiene:
  - {total_registros_tesis:,} FILAS de tesis (con duplicados)
  - {len(codigos_tesis_unicos):,} TESIS ÚNICAS (sin duplicados)
  
  - {total_registros_libros:,} FILAS de libros (con duplicados)
  - {len(codigos_libros_unicos):,} LIBROS ÚNICOS (sin duplicados)

La base de datos debe contener solo los registros ÚNICOS, 
por lo tanto las cantidades correctas son:
  ✓ {len(codigos_tesis_unicos):,} tesis
  ✓ {len(codigos_libros_unicos):,} libros
""")
print("=" * 80)
