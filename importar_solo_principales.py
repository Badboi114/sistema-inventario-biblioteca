"""
Script para importar SOLO la hoja principal de libros (1704 o 1705 registros)
y la hoja principal de tesis
"""
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
    """Limpia y normaliza valores del Excel"""
    if pd.isna(valor):
        return ''
    valor_str = str(valor).strip()
    if valor_str.lower() in ['nan', 'none', '']:
        return ''
    return valor_str


def parse_anio(valor):
    """Convierte el año a entero"""
    try:
        if pd.isna(valor):
            return None
        return int(float(valor))
    except:
        return None


def normalizar_estado(estado):
    """Normaliza el estado del libro/tesis"""
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
    """Genera un código único para registros sin código"""
    if tipo == 'libro':
        return f'SIN-LIB-{contador:04d}'
    else:
        return f'SIN-TES-{contador:04d}'


def importar_libros_academicos(archivo_excel):
    """Importa solo la hoja LISTA DE LIBROS ACADEMICOS"""
    print(f"\n{'='*80}")
    print("IMPORTANDO: LIBROS ACADÉMICOS")
    print(f"{'='*80}")
    
    df = pd.read_excel(archivo_excel, sheet_name='LISTA DE LIBROS ACADEMICOS')
    df.columns = df.columns.str.strip().str.upper()
    
    print(f"Total de filas en el Excel: {len(df)}")
    
    creados = 0
    omitidos = 0
    sin_codigo_count = 0
    orden_actual = 1
    
    with transaction.atomic():
        for idx, row in df.iterrows():
            try:
                titulo = limpiar_valor(row.get('TITULO', ''))
                if not titulo:
                    omitidos += 1
                    continue
                
                # Obtener código (buscar variaciones)
                raw_codigo = limpiar_valor(row.get('CODIGO NUEVO', ''))
                if not raw_codigo:
                    raw_codigo = limpiar_valor(row.get('CODIGO NUEVO ', ''))
                
                # Si no hay código, generar uno
                if not raw_codigo:
                    sin_codigo_count += 1
                    codigo = generar_codigo_unico('libro', sin_codigo_count)
                else:
                    codigo = raw_codigo
                
                # Preparar datos
                datos = {
                    'codigo_nuevo': codigo,
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
                    'orden_importacion': orden_actual,
                }
                
                Libro.objects.create(**datos)
                creados += 1
                orden_actual += 1
                
                if creados % 100 == 0:
                    print(f"  Procesados: {creados}")
                    
            except Exception as e:
                print(f"⚠️ Error en fila {idx + 2}: {str(e)}")
    
    print(f"\n📊 Resultados:")
    print(f"  ✅ Creados: {creados}")
    print(f"  📝 Sin código original: {sin_codigo_count}")
    print(f"  ⏭️ Omitidos: {omitidos}")
    
    return creados, sin_codigo_count


def importar_tesis(archivo_excel):
    """Importa solo la hoja LISTA DE PROYECTOS DE GRADO (705 registros)"""
    print(f"\n{'='*80}")
    print("IMPORTANDO: TESIS Y PROYECTOS DE GRADO")
    print(f"{'='*80}")
    
    df = pd.read_excel(archivo_excel, sheet_name='LISTA DE PROYECTOS DE GRADO')
    df.columns = df.columns.str.strip().str.upper()
    
    print(f"Total de filas en el Excel: {len(df)}")
    
    creados = 0
    omitidos = 0
    sin_codigo_count = 0
    
    with transaction.atomic():
        for idx, row in df.iterrows():
            try:
                titulo = limpiar_valor(row.get('TITULO', ''))
                if not titulo:
                    omitidos += 1
                    continue
                
                # Obtener código (buscar variaciones)
                raw_codigo = limpiar_valor(row.get('CODIGO NUEVO', ''))
                if not raw_codigo:
                    raw_codigo = limpiar_valor(row.get('CODIGO NUEVO ', ''))
                
                # Si no hay código, generar uno
                if not raw_codigo:
                    sin_codigo_count += 1
                    codigo = generar_codigo_unico('tesis', sin_codigo_count)
                else:
                    codigo = raw_codigo
                
                # Obtener autor (puede ser ESTUDIANTE o AUTOR)
                autor = limpiar_valor(row.get('ESTUDIANTE', ''))
                if not autor:
                    autor = limpiar_valor(row.get('AUTOR', ''))
                
                # Obtener carrera (puede tener espacio al final)
                carrera = limpiar_valor(row.get('CARRERA', ''))
                if not carrera:
                    carrera = limpiar_valor(row.get('CARRERA ', ''))
                
                # Preparar datos
                datos = {
                    'codigo_nuevo': codigo,
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
                
                TrabajoGrado.objects.create(**datos)
                creados += 1
                
                if creados % 100 == 0:
                    print(f"  Procesados: {creados}")
                    
            except Exception as e:
                print(f"⚠️ Error en fila {idx + 2}: {str(e)}")
    
    print(f"\n📊 Resultados:")
    print(f"  ✅ Creadas: {creados}")
    print(f"  📝 Sin código original: {sin_codigo_count}")
    print(f"  ⏭️ Omitidas: {omitidos}")
    
    return creados, sin_codigo_count


def main():
    """Función principal"""
    archivo_excel = r'BASE DE EXISTENCIA DE LIBROS, PROYECTOS DE GRADO, TESIS Y TRABAJO DIRIGIDO (2).xlsx'
    
    if not os.path.exists(archivo_excel):
        print(f"❌ Error: No se encontró el archivo '{archivo_excel}'")
        return
    
    print(f"\n{'='*80}")
    print(f"IMPORTACIÓN FINAL - SOLO HOJAS PRINCIPALES")
    print(f"{'='*80}")
    print(f"Archivo: {archivo_excel}")
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Verificar estado inicial
    print(f"\nEstado inicial:")
    print(f"  Libros: {Libro.objects.count()}")
    print(f"  Tesis: {TrabajoGrado.objects.count()}")
    
    try:
        # Importar libros académicos
        libros_creados, libros_sin_codigo = importar_libros_academicos(archivo_excel)
        
        # Importar tesis
        tesis_creadas, tesis_sin_codigo = importar_tesis(archivo_excel)
        
        # Verificar totales en BD
        total_libros = Libro.objects.count()
        total_tesis = TrabajoGrado.objects.count()
        
        print(f"\n{'='*80}")
        print(f"RESUMEN FINAL")
        print(f"{'='*80}")
        print(f"📚 Total libros creados:      {libros_creados}")
        print(f"   - Sin código original:     {libros_sin_codigo}")
        print(f"🎓 Total tesis creadas:       {tesis_creadas}")
        print(f"   - Sin código original:     {tesis_sin_codigo}")
        
        print(f"\n{'='*80}")
        print(f"ESTADO FINAL DE LA BASE DE DATOS")
        print(f"{'='*80}")
        print(f"📚 Total libros en BD:  {total_libros}")
        print(f"🎓 Total tesis en BD:   {total_tesis}")
        print(f"{'='*80}\n")
        
        print(f"✅ Importación completada exitosamente!")
        
    except Exception as e:
        print(f"\n❌ Error general: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
