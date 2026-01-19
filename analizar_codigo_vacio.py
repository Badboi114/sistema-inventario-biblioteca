#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Analizar registros con código vacío - ¿Son todos duplicados excepto uno?
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
        if valor.upper() in ['SIN DATOS', 'SIN DETALLE', 'SIN DETALLES', 'N/A', 'NA']:
            return None
        # NO convertir cadena vacía a None
        if valor == '':
            return ''
    return str(valor) if valor else None

print("="*80)
print("ANÁLISIS DE REGISTROS CON CÓDIGO VACÍO")
print("="*80)

registros_codigo_vacio = []

for sheet_name in sheets_libros:
    df = pd.read_excel(EXCEL_FILE, sheet_name=sheet_name)
    
    for idx, row in df.iterrows():
        codigo_raw = row.get('CODIGO NUEVO ')
        
        # Detectar códigos vacíos
        if pd.isna(codigo_raw) or (isinstance(codigo_raw, str) and codigo_raw.strip() == ''):
            titulo = limpiar_valor(row.get('TITULO'))
            autor = limpiar_valor(row.get('AUTOR'))
            
            if titulo:  # Solo si tiene título válido
                registros_codigo_vacio.append({
                    'hoja': sheet_name,
                    'titulo': titulo,
                    'autor': autor
                })

print(f"\nTotal registros con código vacío pero título válido: {len(registros_codigo_vacio)}")

# Verificar cuántos son únicos por título+autor
registros_unicos = set()
for r in registros_codigo_vacio:
    clave = (r['titulo'], r['autor'])
    registros_unicos.add(clave)

print(f"De esos, cuántos son ÚNICOS por título+autor: {len(registros_unicos)}")

print("\nPrimeros 20 registros únicos con código vacío:")
for i, (titulo, autor) in enumerate(list(registros_unicos)[:20], 1):
    print(f"{i:3d}. {titulo[:60]:<60} - {autor if autor else 'SIN AUTOR'}")

print("\n" + "="*80)
print("CONCLUSIÓN:")
print("="*80)
print(f"El Excel tiene {len(registros_codigo_vacio)} registros con código vacío")
print(f"De los cuales {len(registros_unicos)} son únicos (por título+autor)")
print(f"Pero estamos generando {len(registros_codigo_vacio)} códigos SIN-CODIGO")
print(f"Solución: Necesitamos identificar duplicados ANTES de generar códigos")
