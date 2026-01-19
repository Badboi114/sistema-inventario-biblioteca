#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Analizar códigos únicos REALES (no vacíos) vs códigos generados
"""
import pandas as pd

EXCEL_FILE = 'BASE DE EXISTENCIA DE LIBROS, PROYECTOS DE GRADO, TESIS Y TRABAJO DIRIGIDO (2).xlsx'
sheets_libros = ['LISTA DE LIBROS ACADEMICOS', 'LIBROS DE LECTURA', 'PARA REPORTE']

print("="*80)
print("ANÁLISIS DE CÓDIGOS REALES VS VACÍOS")
print("="*80)

# Contar códigos NO vacíos (reales)
codigos_reales = set()
registros_codigo_vacio = []

for sheet_name in sheets_libros:
    df = pd.read_excel(EXCEL_FILE, sheet_name=sheet_name)
    
    for idx, row in df.iterrows():
        codigo_raw = row.get('CODIGO NUEVO ')
        
        # Código real (no vacío, no NaN)
        if pd.notna(codigo_raw) and isinstance(codigo_raw, str) and codigo_raw.strip() != '':
            codigos_reales.add(codigo_raw.strip())
        else:
            # Código vacío
            titulo = row.get('TITULO')
            if pd.notna(titulo) and isinstance(titulo, str) and titulo.strip() != '':
                registros_codigo_vacio.append({
                    'titulo': titulo.strip(),
                    'autor': row.get('AUTOR'),
                    'hoja': sheet_name
                })

print(f"\n1. CÓDIGOS REALES (NO VACÍOS) EN EXCEL: {len(codigos_reales)}")
print(f"2. REGISTROS CON CÓDIGO VACÍO: {len(registros_codigo_vacio)}")

# Verificar si algún libro con código vacío NO es duplicado de uno con código
# Para eso, comparo por título+autor
libros_con_codigo = {}
for sheet_name in sheets_libros:
    df = pd.read_excel(EXCEL_FILE, sheet_name=sheet_name)
    
    for idx, row in df.iterrows():
        codigo_raw = row.get('CODIGO NUEVO ')
        
        if pd.notna(codigo_raw) and isinstance(codigo_raw, str) and codigo_raw.strip() != '':
            titulo = row.get('TITULO')
            autor = row.get('AUTOR')
            
            if pd.notna(titulo):
                titulo_clean = titulo.strip() if isinstance(titulo, str) else str(titulo)
                autor_clean = autor.strip() if pd.notna(autor) and isinstance(autor, str) else None
                
                clave = (titulo_clean, autor_clean)
                libros_con_codigo[clave] = codigo_raw.strip()

print(f"\n3. LIBROS CON CÓDIGO (únicos por título+autor): {len(libros_con_codigo)}")

# Ahora verificar cuántos libros sin código NO están en libros_con_codigo
libros_sin_codigo_unicos = []
for registro in registros_codigo_vacio:
    titulo = registro['titulo']
    autor = registro.get('autor')
    autor_clean = autor.strip() if pd.notna(autor) and isinstance(autor, str) else None
    
    clave = (titulo, autor_clean)
    if clave not in libros_con_codigo:
        libros_sin_codigo_unicos.append(registro)

print(f"4. LIBROS SIN CÓDIGO QUE NO TIENEN VERSION CON CÓDIGO: {len(libros_sin_codigo_unicos)}")

if libros_sin_codigo_unicos:
    print("\n" + "="*80)
    print("ESTOS SON LOS ÚNICOS QUE NECESITAN CODIGO GENERADO:")
    print("="*80)
    for i, libro in enumerate(libros_sin_codigo_unicos[:20], 1):
        print(f"{i:3d}. {libro['titulo'][:60]:<60} - {libro.get('autor', 'SIN AUTOR')}")
    
    if len(libros_sin_codigo_unicos) > 20:
        print(f"      ... y {len(libros_sin_codigo_unicos) - 20} más")

print("\n" + "="*80)
print("CONCLUSIÓN:")
print("="*80)
print(f"Total códigos únicos esperados en BD:")
print(f"  - Códigos reales: {len(codigos_reales)}")
print(f"  - Códigos generados necesarios: {len(libros_sin_codigo_unicos)}")
print(f"  - TOTAL: {len(codigos_reales) + len(libros_sin_codigo_unicos)}")
