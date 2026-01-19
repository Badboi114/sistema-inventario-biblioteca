#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Encontrar el libro faltante
"""
import os
import django
import pandas as pd

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from inventario.models import Libro

EXCEL_FILE = 'BASE DE EXISTENCIA DE LIBROS, PROYECTOS DE GRADO, TESIS Y TRABAJO DIRIGIDO (2).xlsx'

print("=" * 80)
print("BUSCANDO EL LIBRO FALTANTE")
print("=" * 80)

# Obtener todos los códigos del Excel
sheets_libros = ['LISTA DE LIBROS ACADEMICOS', 'LIBROS DE LECTURA', 'PARA REPORTE']
codigos_excel = set()

for sheet in sheets_libros:
    df = pd.read_excel(EXCEL_FILE, sheet_name=sheet)
    if 'CODIGO NUEVO ' in df.columns:
        codigos = df['CODIGO NUEVO '].dropna().astype(str).str.strip()
        codigos_validos = set(codigos[codigos != 'nan'].unique())
        codigos_excel.update(codigos_validos)

print(f"\nCódigos únicos en Excel: {len(codigos_excel)}")

# Obtener todos los códigos de la BD
codigos_bd = set(Libro.objects.values_list('codigo_nuevo', flat=True))
print(f"Códigos únicos en BD: {len(codigos_bd)}")

# Encontrar diferencias
faltantes_en_bd = codigos_excel - codigos_bd
extras_en_bd = codigos_bd - codigos_excel

print(f"\n" + "=" * 80)
if faltantes_en_bd:
    print(f"CÓDIGOS EN EXCEL PERO NO EN BD: {len(faltantes_en_bd)}")
    print("=" * 80)
    for codigo in sorted(faltantes_en_bd):
        # Buscar en el Excel para ver los detalles
        for sheet in sheets_libros:
            df = pd.read_excel(EXCEL_FILE, sheet_name=sheet)
            if 'CODIGO NUEVO ' in df.columns:
                mask = df['CODIGO NUEVO '].astype(str).str.strip() == codigo
                if mask.any():
                    row = df[mask].iloc[0]
                    titulo = row.get('TITULO', 'N/A')
                    print(f"\n  Código: {codigo}")
                    print(f"  Hoja: {sheet}")
                    print(f"  Título: {titulo}")
                    print(f"  Autor: {row.get('AUTOR', 'N/A')}")
                    break

if extras_en_bd:
    print(f"\nCÓDIGOS EN BD PERO NO EN EXCEL: {len(extras_en_bd)}")
    print("=" * 80)
    for codigo in sorted(extras_en_bd):
        libro = Libro.objects.filter(codigo_nuevo=codigo).first()
        if libro:
            print(f"\n  Código: {codigo}")
            print(f"  Título: {libro.titulo[:60]}")

if not faltantes_en_bd and not extras_en_bd:
    print("\n✓ TODOS LOS CÓDIGOS COINCIDEN PERFECTAMENTE")

print("\n" + "=" * 80)
