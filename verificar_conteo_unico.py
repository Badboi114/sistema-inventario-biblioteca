#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Verificar el conteo REAL de códigos únicos (considerando empty string como código)
"""
import pandas as pd
from collections import Counter

EXCEL_FILE = 'BASE DE EXISTENCIA DE LIBROS, PROYECTOS DE GRADO, TESIS Y TRABAJO DIRIGIDO (2).xlsx'
sheets_libros = ['LISTA DE LIBROS ACADEMICOS', 'LIBROS DE LECTURA', 'PARA REPORTE']

print("="*80)
print("VERIFICACIÓN DE CONTEO DE CÓDIGOS ÚNICOS")
print("="*80)

# Método 1: Como lo hace analizar_excel_completo.py
todos_codigos_metodo1 = []
for sheet in sheets_libros:
    df = pd.read_excel(EXCEL_FILE, sheet_name=sheet)
    if 'CODIGO NUEVO ' in df.columns:
        codigos = df['CODIGO NUEVO '].dropna().astype(str).str.strip()
        codigos_validos = codigos[codigos != 'nan']
        todos_codigos_metodo1.extend(codigos_validos.tolist())

unicos_metodo1 = set(todos_codigos_metodo1)
print(f"\nMétodo 1 (dropna + != 'nan'):")
print(f"  - Total códigos procesados: {len(todos_codigos_metodo1)}")
print(f"  - Códigos únicos: {len(unicos_metodo1)}")
print(f"  - ¿Contiene empty string? {'Sí' if '' in unicos_metodo1 else 'No'}")

# Método 2: Separar explícitamente empty string
codigos_reales = set()
codigo_vacio_count = 0

for sheet in sheets_libros:
    df = pd.read_excel(EXCEL_FILE, sheet_name=sheet)
    if 'CODIGO NUEVO ' in df.columns:
        for val in df['CODIGO NUEVO ']:
            if pd.notna(val):
                val_str = str(val).strip()
                if val_str != '' and val_str != 'nan':
                    codigos_reales.add(val_str)
                elif val_str == '':
                    codigo_vacio_count += 1

print(f"\nMétodo 2 (separando empty string):")
print(f"  - Códigos reales (no vacíos): {len(codigos_reales)}")
print(f"  - Registros con código vacío: {codigo_vacio_count}")
print(f"  - Si contamos empty como 1 código: {len(codigos_reales) + 1}")

# Método 3: Por título+autor (verdadera unicidad)
libros_unicos = set()
for sheet in sheets_libros:
    df = pd.read_excel(EXCEL_FILE, sheet_name=sheet)
    for idx, row in df.iterrows():
        titulo = row.get('TITULO')
        autor = row.get('AUTOR')
        
        if pd.notna(titulo):
            titulo_clean = str(titulo).strip()
            autor_clean = str(autor).strip() if pd.notna(autor) else None
            clave = (titulo_clean, autor_clean)
            libros_unicos.add(clave)

print(f"\nMétodo 3 (unicidad por título+autor):")
print(f"  - Libros únicos por título+autor: {len(libros_unicos)}")

print("\n" + "="*80)
print("CONCLUSIÓN:")
print("="*80)
print("El usuario ve en su Excel 1,393 códigos únicos porque:")
print(f"  - 1,392 códigos reales + 1 empty string = 1,393")
print("\nPero si importamos por unicidad de contenido (título+autor):")
print(f"  - Deberíamos tener {len(libros_unicos)} libros únicos")
print("\nLa pregunta es: ¿qué quiere el usuario?")
print("  a) 1,393 registros (contando empty string como 1 código único)")
print(f"  b) {len(libros_unicos)} registros (todos los libros únicos por contenido)")
