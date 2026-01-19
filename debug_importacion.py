#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Debug: Entender por qué se importaron 2,285 libros cuando solo hay 1,393 únicos
"""
import pandas as pd

EXCEL_FILE = 'BASE DE EXISTENCIA DE LIBROS, PROYECTOS DE GRADO, TESIS Y TRABAJO DIRIGIDO (2).xlsx'

sheets_libros = ['LISTA DE LIBROS ACADEMICOS', 'LIBROS DE LECTURA', 'PARA REPORTE']

def limpiar_valor(valor):
    """Limpia y normaliza valores del Excel"""
    if pd.isna(valor):
        return None
    if isinstance(valor, str):
        valor = valor.strip()
        if valor.upper() in ['SIN DATOS', 'SIN DETALLE', 'SIN DETALLES', 'N/A', 'NA', '']:
            return None
    return str(valor) if valor else None

print("="*80)
print("ANÁLISIS DE LA IMPORTACIÓN")
print("="*80)

codigos_vacios = 0
codigos_none = 0
codigos_validos = 0
codigos_unicos = set()
contador_sin_codigo = 0

for sheet_name in sheets_libros:
    print(f"\nHoja: {sheet_name}")
    df = pd.read_excel(EXCEL_FILE, sheet_name=sheet_name)
    print(f"  Total filas: {len(df)}")
    
    for idx, row in df.iterrows():
        codigo_raw = row.get('CODIGO NUEVO ')
        codigo_limpio = limpiar_valor(codigo_raw)
        
        # Simular la lógica del script de importación
        if not codigo_limpio or codigo_limpio == 'nan':
            titulo = limpiar_valor(row.get('TITULO'))
            if titulo:
                contador_sin_codigo += 1
                codigo_final = f'SIN-CODIGO-{contador_sin_codigo:04d}'
                codigos_vacios += 1
            else:
                continue
        else:
            codigo_final = codigo_limpio
            codigos_validos += 1
        
        # Verificar duplicados (lo que hace el script)
        if codigo_final in codigos_unicos:
            # Este sería omitido por duplicado
            continue
        else:
            codigos_unicos.add(codigo_final)

print("\n" + "="*80)
print("RESUMEN:")
print("="*80)
print(f"Códigos válidos encontrados: {codigos_validos}")
print(f"Códigos vacíos (generados SIN-CODIGO-####): {codigos_vacios}")
print(f"Total códigos únicos que serían importados: {len(codigos_unicos)}")
print(f"  - De los cuales son SIN-CODIGO: {len([c for c in codigos_unicos if c.startswith('SIN-CODIGO')])}")
print(f"  - De los cuales son códigos reales: {len([c for c in codigos_unicos if not c.startswith('SIN-CODIGO')])}")

print("\n" + "="*80)
print("CONCLUSIÓN:")
print("="*80)
print(f"El script debería importar {len(codigos_unicos)} libros")
print(f"Pero la BD tiene 2,285 libros")
print(f"Diferencia: {2285 - len(codigos_unicos)} libros de más")
