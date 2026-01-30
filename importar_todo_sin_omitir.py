import os
import sys
import django
import pandas as pd
from datetime import datetime

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.db import transaction, models
from inventario.models import Libro, TrabajoGrado

def limpiar_valor(valor):
    if pd.isna(valor):
        return ''
    valor_str = str(valor).strip()
    if valor_str.lower() in ['nan', 'none', '']:
        return ''
    return valor_str

def parse_anio(valor):
    try:
        if pd.isna(valor):
            return None
        return int(float(valor))
    except:
        return None

def normalizar_estado(estado):
    estado_str = limpiar_valor(estado).upper()
    if not estado_str:
        return 'REGULAR'
    if 'BUEN' in estado_str:
        return 'BUENO'
    elif 'MAL' in estado_str:
        return 'MALO'
    elif 'REGULAR' in estado_str:
        return 'REGULAR'
    elif 'REPARACION' in estado_str:
        return 'EN REPARACION'
    else:
        return 'REGULAR'

def generar_codigo_unico(tipo, contador):
    if tipo == 'libro':
        return f'SIN-LIB-{contador:04d}'
    else:
        return f'SIN-TES-{contador:04d}'

def importar_libros_y_tesis():
    archivo_excel = r'BASE DE EXISTENCIA DE LIBROS, PROYECTOS DE GRADO, TESIS Y TRABAJO DIRIGIDO (2).xlsx'
    if not os.path.exists(archivo_excel):
        print(f"❌ Error: No se encontró el archivo '{archivo_excel}'")
        return
    excel_file = pd.ExcelFile(archivo_excel)
    # Libros académicos
    df_libros = pd.read_excel(archivo_excel, sheet_name='LISTA DE LIBROS ACADEMICOS')
    # Libros de lectura
    df_lectura = pd.read_excel(archivo_excel, sheet_name='LIBROS DE LECTURA')
    # Tesis
    df_tesis = pd.read_excel(archivo_excel, sheet_name='LISTA DE PROYECTOS DE GRADO (2)')
    # Unificar libros
    df_libros = pd.concat([df_libros, df_lectura], ignore_index=True)
    # Importar libros
    print('Importando libros...')
    codigos_libros = set()
    with transaction.atomic():
        for idx, row in df_libros.iterrows():
            titulo = limpiar_valor(row.get('TITULO', ''))
            raw_codigo = limpiar_valor(row.get('CODIGO NUEVO', ''))
            if not raw_codigo:
                raw_codigo = limpiar_valor(row.get('CODIGO NUEVO ', ''))
            if not raw_codigo:
                raw_codigo = generar_codigo_unico('libro', idx+1)
            if raw_codigo in codigos_libros:
                continue
            codigos_libros.add(raw_codigo)
            datos = {
                'codigo_nuevo': raw_codigo,
                'titulo': titulo,
                'autor': limpiar_valor(row.get('AUTOR', '')),
                'editorial': limpiar_valor(row.get('EDITORIAL', '')),
                'edicion': limpiar_valor(row.get('EDICIÓN', '')),
                'anio': parse_anio(row.get('AÑO')),
                'facultad': limpiar_valor(row.get('FACULTAD', '')),
                'materia': limpiar_valor(row.get('MATERIA', '')),
                'codigo_antiguo': limpiar_valor(row.get('CODIGO ANTIGUO', '')),
                'codigo_seccion_full': limpiar_valor(row.get('CODIGO DE SECCION', '')),
                'ubicacion_seccion': limpiar_valor(row.get('SECCIÓN', '')),
                'ubicacion_repisa': limpiar_valor(row.get('REPISA', '')),
                'estado': normalizar_estado(row.get('ESTADO', 'REGULAR')),
                'observaciones': limpiar_valor(row.get('OBSERVACIONES', '')),
                'orden_importacion': idx+1,
            }
            Libro.objects.update_or_create(codigo_nuevo=raw_codigo, defaults=datos)
    print(f"Libros importados: {len(codigos_libros)}")
    # Importar tesis
    print('Importando tesis...')
    codigos_tesis = set()
    with transaction.atomic():
        for idx, row in df_tesis.iterrows():
            titulo = limpiar_valor(row.get('TITULO', ''))
            raw_codigo = limpiar_valor(row.get('CODIGO NUEVO', ''))
            if not raw_codigo:
                raw_codigo = limpiar_valor(row.get('CODIGO NUEVO ', ''))
            if not raw_codigo:
                raw_codigo = generar_codigo_unico('tesis', idx+1)
            if raw_codigo in codigos_tesis:
                continue
            codigos_tesis.add(raw_codigo)
            autor = limpiar_valor(row.get('ESTUDIANTE', ''))
            if not autor:
                autor = limpiar_valor(row.get('AUTOR', ''))
            carrera = limpiar_valor(row.get('CARRERA', ''))
            if not carrera:
                carrera = limpiar_valor(row.get('CARRERA ', ''))
            datos = {
                'codigo_nuevo': raw_codigo,
                'titulo': titulo,
                'autor': autor,
                'tutor': limpiar_valor(row.get('TUTOR', '')),
                'modalidad': limpiar_valor(row.get('MODALIDAD', '')),
                'carrera': carrera,
                'facultad': limpiar_valor(row.get('FACULTAD', '')),
                'anio': parse_anio(row.get('AÑO')),
                'estado': normalizar_estado(row.get('ESTADO', 'REGULAR')),
                'ubicacion_seccion': limpiar_valor(row.get('SECCION', '')),
                'ubicacion_repisa': limpiar_valor(row.get('REPISA', '')),
                'observaciones': limpiar_valor(row.get('OBSERVACIONES', '')),
            }
            TrabajoGrado.objects.update_or_create(codigo_nuevo=raw_codigo, defaults=datos)
    print(f"Tesis importadas: {len(codigos_tesis)}")

if __name__ == '__main__':
    importar_libros_y_tesis()
