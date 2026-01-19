#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
IMPORTACIÓN FINAL Y DEFINITIVA
Limpia todo e importa SOLO del Excel, sin duplicados, todos los libros únicos
"""
import os
import django
import pandas as pd

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.db import transaction
from inventario.models import Libro, TrabajoGrado, Prestamo

EXCEL_FILE = 'BASE DE EXISTENCIA DE LIBROS, PROYECTOS DE GRADO, TESIS Y TRABAJO DIRIGIDO (2).xlsx'

def limpiar_valor(valor):
    """Limpia y normaliza valores del Excel"""
    if pd.isna(valor):
        return None
    if isinstance(valor, str):
        valor = valor.strip()
        if valor.upper() in ['SIN DATOS', 'SIN DETALLE', 'SIN DETALLES', 'N/A', 'NA']:
            return None
        if valor == '':
            return None
    return str(valor) if valor else None

def parse_anio(valor):
    """Convierte año a entero"""
    if pd.isna(valor):
        return None
    try:
        anio = int(float(str(valor)))
        if 1900 <= anio <= 2100:
            return anio
    except:
        pass
    return None

def normalizar_estado(estado):
    """Normaliza estado a BUENO/REGULAR/MALO"""
    if pd.isna(estado):
        return 'REGULAR'
    estado_str = str(estado).strip().upper()
    if any(x in estado_str for x in ['BUENO', 'BUEN', 'BIEN', 'EXCELENTE', 'NUEVO']):
        return 'BUENO'
    elif any(x in estado_str for x in ['MALO', 'MAL', 'DETERIORADO', 'DAÑADO']):
        return 'MALO'
    return 'REGULAR'

print("="*80)
print("LIMPIEZA TOTAL E IMPORTACIÓN DEFINITIVA")
print("="*80)

# PASO 1: ELIMINAR TODO
print("\n1. ELIMINANDO TODOS LOS DATOS...")
with transaction.atomic():
    prestamos_deleted = Prestamo.objects.all().delete()[0]
    libros_deleted = Libro.objects.all().delete()[0]
    tesis_deleted = TrabajoGrado.objects.all().delete()[0]
    
print(f"   [OK] Eliminados: {prestamos_deleted} préstamos, {libros_deleted} libros, {tesis_deleted} tesis")

# PASO 2: IMPORTAR TESIS (por código único)
print("\n2. IMPORTANDO TESIS...")
sheets_tesis = ['LISTA DE PROYECTOS DE GRADO (2)', 'Tabla7', 'LISTA DE PROYECTOS DE GRADO']
codigos_tesis = set()
tesis_creadas = 0
tesis_omitidas = 0

for sheet_name in sheets_tesis:
    print(f"\n   Procesando: {sheet_name}")
    df = pd.read_excel(EXCEL_FILE, sheet_name=sheet_name)
    
    for idx, row in df.iterrows():
        try:
            codigo_nuevo = limpiar_valor(row.get('CODIGO NUEVO '))
            
            if not codigo_nuevo or codigo_nuevo == 'nan':
                tesis_omitidas += 1
                continue
            
            if codigo_nuevo in codigos_tesis:
                print(f"      [SKIP] Duplicado: {codigo_nuevo}")
                tesis_omitidas += 1
                continue
            
            codigos_tesis.add(codigo_nuevo)
            
            with transaction.atomic():
                TrabajoGrado.objects.create(
                    codigo_nuevo=codigo_nuevo,
                    codigo_antiguo=limpiar_valor(row.get('CODIGO ANTIGUO')),
                    titulo=limpiar_valor(row.get('TITULO')) or 'SIN TITULO',
                    autor=limpiar_valor(row.get('AUTOR')),
                    tutor=limpiar_valor(row.get('TUTOR')),
                    modalidad=limpiar_valor(row.get('MODALIDAD')),
                    carrera=limpiar_valor(row.get('CARRERA ')),
                    anio=parse_anio(row.get('AÑO')),
                    estado=normalizar_estado(row.get('ESTADO')),
                    ubicacion_seccion=limpiar_valor(row.get('SECCION')),
                    ubicacion_repisa=limpiar_valor(row.get('REPISA')),
                    facultad=limpiar_valor(row.get('FACULTAD')),
                    observaciones=limpiar_valor(row.get('OBSERVACIONES'))
                )
                tesis_creadas += 1
        except Exception as e:
            print(f"      [ERROR] Fila {idx}: {str(e)}")
            tesis_omitidas += 1

print(f"\n   [OK] TESIS creadas: {tesis_creadas}")
print(f"   [INFO] TESIS omitidas: {tesis_omitidas}")

# PASO 3: IMPORTAR LIBROS (por unicidad: código O título+autor)
print("\n3. IMPORTANDO LIBROS...")
sheets_libros = ['LISTA DE LIBROS ACADEMICOS', 'LIBROS DE LECTURA', 'PARA REPORTE']
libros_unicos = set()  # Set para (codigo) o (titulo, autor, editorial, anio)
libros_creados = 0
libros_omitidos = 0
contador_sin_codigo = 0

for sheet_name in sheets_libros:
    print(f"\n   Procesando: {sheet_name}")
    df = pd.read_excel(EXCEL_FILE, sheet_name=sheet_name)
    
    for idx, row in df.iterrows():
        try:
            codigo_nuevo = limpiar_valor(row.get('CODIGO NUEVO '))
            titulo = limpiar_valor(row.get('TITULO'))
            autor = limpiar_valor(row.get('AUTOR'))
            editorial = limpiar_valor(row.get('EDITORIAL'))
            anio = parse_anio(row.get('AÑO'))
            
            if not titulo:
                libros_omitidos += 1
                continue
            
            # Determinar clave de unicidad
            if codigo_nuevo and codigo_nuevo != 'nan':
                # Tiene código: usar solo código como clave
                clave_unica = ('codigo', codigo_nuevo)
            else:
                # Sin código: usar contenido completo para detectar duplicados
                clave_unica = ('contenido', titulo, autor, editorial, anio)
            
            # Verificar duplicados
            if clave_unica in libros_unicos:
                if codigo_nuevo:
                    print(f"      [SKIP] Duplicado: {codigo_nuevo}")
                else:
                    print(f"      [SKIP] Duplicado sin código: {titulo[:40]}")
                libros_omitidos += 1
                continue
            
            libros_unicos.add(clave_unica)
            
            # Asignar código si no tiene
            if not codigo_nuevo or codigo_nuevo == 'nan':
                contador_sin_codigo += 1
                codigo_nuevo = f'SIN-CODIGO-{contador_sin_codigo:04d}'
                print(f"      [INFO] Libro sin código, asignando: {codigo_nuevo} - {titulo[:40]}")
            
            with transaction.atomic():
                Libro.objects.create(
                    codigo_nuevo=codigo_nuevo,
                    codigo_antiguo=limpiar_valor(row.get('CODIGO ANTIGUO')),
                    titulo=titulo,
                    autor=autor,
                    editorial=editorial,
                    anio=anio,
                    edicion=limpiar_valor(row.get('EDICION')),
                    materia=limpiar_valor(row.get('MATERIA')),
                    estado=normalizar_estado(row.get('ESTADO')),
                    ubicacion_seccion=limpiar_valor(row.get('SECCION')),
                    ubicacion_repisa=limpiar_valor(row.get('REPISA')),
                    facultad=limpiar_valor(row.get('FACULTAD')),
                    observaciones=limpiar_valor(row.get('OBSERVACIONES'))
                )
                libros_creados += 1
        except Exception as e:
            print(f"      [ERROR] Fila {idx}: {str(e)}")
            libros_omitidos += 1

print(f"\n   [OK] LIBROS creados: {libros_creados}")
print(f"   [INFO] LIBROS omitidos: {libros_omitidos}")
print(f"   [INFO] Códigos generados (SIN-CODIGO): {contador_sin_codigo}")

# VERIFICACIÓN FINAL
print("\n" + "="*80)
print("VERIFICACIÓN FINAL:")
print("="*80)

tesis_bd = TrabajoGrado.objects.count()
libros_bd = Libro.objects.count()
print(f"\nBase de Datos:")
print(f"  Tesis:  {tesis_bd}")
print(f"  Libros: {libros_bd}")
print(f"  TOTAL:  {tesis_bd + libros_bd}")

print(f"\nCódigos únicos importados:")
print(f"  Tesis:  {len(codigos_tesis)}")
print(f"  Libros: {len(libros_unicos)}")

# Verificar duplicados
from collections import Counter
codigos_tesis_bd = list(TrabajoGrado.objects.values_list('codigo_nuevo', flat=True))
codigos_libros_bd = list(Libro.objects.values_list('codigo_nuevo', flat=True))

dup_tesis = [k for k, v in Counter(codigos_tesis_bd).items() if v > 1]
dup_libros = [k for k, v in Counter(codigos_libros_bd).items() if v > 1]

if dup_tesis:
    print(f"\n[!] ADVERTENCIA: {len(dup_tesis)} códigos duplicados en tesis")
else:
    print(f"\n[OK] TESIS: Sin duplicados")

if dup_libros:
    print(f"[!] ADVERTENCIA: {len(dup_libros)} códigos duplicados en libros")
else:
    print(f"[OK] LIBROS: Sin duplicados")

print("\n" + "="*80)
print("IMPORTACIÓN DEFINITIVA COMPLETADA")
print("="*80)
