#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para limpiar completamente la BD e importar solo del Excel correcto
SIN duplicados, SIN registros extra
"""
import os
import django
import pandas as pd
from decimal import Decimal

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
        if valor.upper() in ['SIN DATOS', 'SIN DETALLE', 'SIN DETALLES', 'N/A', 'NA', '']:
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
    """Normaliza el estado del activo"""
    if not estado:
        return 'BUENO'
    estado = str(estado).upper().strip()
    if 'MALO' in estado or 'MAL' in estado:
        return 'MALO'
    elif 'REGULAR' in estado or 'REG' in estado:
        return 'REGULAR'
    else:
        return 'BUENO'

print("=" * 80)
print("LIMPIEZA COMPLETA E IMPORTACION LIMPIA")
print("=" * 80)

# PASO 1: ELIMINAR TODOS LOS PRESTAMOS
print("\n1. Eliminando prestamos existentes...")
prestamos_count = Prestamo.objects.count()
Prestamo.objects.all().delete()
print(f"   [OK] {prestamos_count} prestamos eliminados")

# PASO 2: ELIMINAR TODOS LOS LIBROS Y TESIS
print("\n2. Eliminando libros y tesis existentes...")
libros_count = Libro.objects.count()
tesis_count = TrabajoGrado.objects.count()
Libro.objects.all().delete()
TrabajoGrado.objects.all().delete()
print(f"   [OK] {libros_count} libros eliminados")
print(f"   [OK] {tesis_count} tesis eliminadas")

# PASO 3: IMPORTAR TESIS
print("\n3. Importando TESIS (sin duplicados)...")
sheets_tesis = [
    'LISTA DE PROYECTOS DE GRADO (2)',
    'Tabla7',
    'LISTA DE PROYECTOS DE GRADO'
]

codigos_tesis_importados = set()
tesis_creadas = 0
tesis_omitidas = 0

for sheet_name in sheets_tesis:
    print(f"\n   Procesando: {sheet_name}")
    df = pd.read_excel(EXCEL_FILE, sheet_name=sheet_name)
    
    for idx, row in df.iterrows():
        try:
            codigo_nuevo = limpiar_valor(row.get('CODIGO NUEVO '))
            
            # Validar codigo_nuevo
            if not codigo_nuevo or codigo_nuevo == 'nan':
                tesis_omitidas += 1
                continue
            
            # Verificar duplicados
            if codigo_nuevo in codigos_tesis_importados:
                print(f"      [SKIP] Duplicado: {codigo_nuevo}")
                tesis_omitidas += 1
                continue
            
            # Crear tesis
            with transaction.atomic():
                TrabajoGrado.objects.create(
                    codigo_nuevo=codigo_nuevo,
                    codigo_antiguo=limpiar_valor(row.get('CODIGO ANTIGUO')),
                    titulo=limpiar_valor(row.get('TITULO')) or 'SIN TITULO',
                    modalidad=limpiar_valor(row.get('MODALIDAD')),
                    autor=limpiar_valor(row.get('AUTOR')),
                    tutor=limpiar_valor(row.get('TUTOR')),
                    anio=parse_anio(row.get('AÑO')),
                    estado=normalizar_estado(row.get('ESTADO')),
                    ubicacion_seccion=limpiar_valor(row.get('SECCION')),
                    ubicacion_repisa=limpiar_valor(row.get('REPISA')),
                    facultad=limpiar_valor(row.get('FACULTAD')),
                    carrera=limpiar_valor(row.get('CARRERA ')),  # Espacio al final
                    observaciones=limpiar_valor(row.get('OBSERVACIONES'))
                )
                codigos_tesis_importados.add(codigo_nuevo)
                tesis_creadas += 1
                
        except Exception as e:
            print(f"      [ERROR] Fila {idx}: {str(e)}")
            tesis_omitidas += 1

print(f"\n   [OK] TESIS creadas: {tesis_creadas}")
print(f"   [INFO] TESIS omitidas: {tesis_omitidas}")

# PASO 4: IMPORTAR LIBROS
print("\n4. Importando LIBROS (sin duplicados)...")
sheets_libros = [
    'LISTA DE LIBROS ACADEMICOS',
    'LIBROS DE LECTURA',
    'PARA REPORTE'
]

codigos_libros_importados = set()
libros_creados = 0
libros_omitidos = 0
contador_sin_codigo = 0
libros_vistos = set()  # Detectar duplicados por (codigo OR (titulo, autor))

for sheet_name in sheets_libros:
    print(f"\n   Procesando: {sheet_name}")
    df = pd.read_excel(EXCEL_FILE, sheet_name=sheet_name)
    
    for idx, row in df.iterrows():
        try:
            codigo_nuevo = limpiar_valor(row.get('CODIGO NUEVO '))
            titulo = limpiar_valor(row.get('TITULO'))
            autor = limpiar_valor(row.get('AUTOR'))
            
            if not titulo:
                # Sin título, omitir
                libros_omitidos += 1
                continue
            
            # Determinar clave de unicidad
            if codigo_nuevo and codigo_nuevo != 'nan':
                # Tiene código: usar código como clave única
                clave_unica = ('codigo', codigo_nuevo)
            else:
                # Sin código: usar título+autor como clave única
                clave_unica = ('titulo_autor', titulo, autor)
            
            # Verificar duplicados
            if clave_unica in libros_vistos:
                if codigo_nuevo:
                    print(f"      [SKIP] Duplicado: {codigo_nuevo}")
                else:
                    print(f"      [SKIP] Duplicado sin código: {titulo[:50]}")
                libros_omitidos += 1
                continue
            
            libros_vistos.add(clave_unica)
            
            # Asignar código si no tiene
            if not codigo_nuevo or codigo_nuevo == 'nan':
                contador_sin_codigo += 1
                codigo_nuevo = f'SIN-CODIGO-{contador_sin_codigo:04d}'
                print(f"      [INFO] Libro sin código, asignando: {codigo_nuevo} - {titulo[:50]}")
            
            # Marcar como procesado
            codigos_libros_importados.add(codigo_nuevo)
            
            # Crear libro
            with transaction.atomic():
                Libro.objects.create(
                    codigo_nuevo=codigo_nuevo,
                    codigo_antiguo=limpiar_valor(row.get('CODIGO ANTIGUO')),
                    titulo=titulo or 'SIN TITULO',
                    autor=autor,
                    editorial=limpiar_valor(row.get('EDITORIAL')),
                    anio=parse_anio(row.get('AÑO')),
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

# PASO 5: VERIFICACION FINAL
print("\n" + "=" * 80)
print("VERIFICACION FINAL:")
print("=" * 80)

total_tesis_bd = TrabajoGrado.objects.count()
total_libros_bd = Libro.objects.count()

print(f"\nBase de Datos:")
print(f"  Tesis:  {total_tesis_bd}")
print(f"  Libros: {total_libros_bd}")
print(f"  TOTAL:  {total_tesis_bd + total_libros_bd}")

print(f"\nCodigos unicos importados:")
print(f"  Tesis:  {len(codigos_tesis_importados)}")
print(f"  Libros: {len(codigos_libros_importados)}")

# Verificar sin duplicados
from collections import Counter
tesis_codigos = list(TrabajoGrado.objects.values_list('codigo_nuevo', flat=True))
libros_codigos = list(Libro.objects.values_list('codigo_nuevo', flat=True))
tesis_duplicados = {codigo: count for codigo, count in Counter(tesis_codigos).items() if count > 1}
libros_duplicados = {codigo: count for codigo, count in Counter(libros_codigos).items() if count > 1}

if not tesis_duplicados:
    print(f"\n[OK] TESIS: Sin duplicados")
else:
    print(f"\n[!] TESIS: {len(tesis_duplicados)} duplicados encontrados")

if not libros_duplicados:
    print(f"[OK] LIBROS: Sin duplicados")
else:
    print(f"[!] LIBROS: {len(libros_duplicados)} duplicados encontrados")

print("\n" + "=" * 80)
print("IMPORTACION COMPLETA Y LIMPIA FINALIZADA")
print("=" * 80)
