"""
Script para importar la nueva base de datos de libros y tesis
Maneja correctamente registros sin código y actualiza toda la base de datos
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

from django.db import transaction
from django.db import models
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


def detectar_tipo_registro(row):
    """
    Detecta si un registro es un libro o una tesis/trabajo de grado
    basándose en las columnas disponibles
    """
    # Verificar si tiene campos específicos de tesis
    tiene_modalidad = limpiar_valor(row.get('MODALIDAD', ''))
    tiene_tutor = limpiar_valor(row.get('TUTOR', ''))
    tiene_carrera = limpiar_valor(row.get('CARRERA', '')) or limpiar_valor(row.get('CARRERA ', ''))
    
    # Verificar si tiene campos específicos de libros
    tiene_editorial = limpiar_valor(row.get('EDITORIAL', ''))
    tiene_edicion = limpiar_valor(row.get('EDICIÓN', ''))
    tiene_materia = limpiar_valor(row.get('MATERIA', ''))
    
    # Si tiene modalidad o tutor, es claramente una tesis
    if tiene_modalidad or tiene_tutor:
        return 'tesis'
    
    # Si tiene editorial, edición o materia, es un libro
    if tiene_editorial or tiene_edicion or tiene_materia:
        return 'libro'
    
    # Por defecto, si tiene carrera sin otros campos, asumir tesis
    if tiene_carrera:
        return 'tesis'
    
    # Por defecto, considerar como libro
    return 'libro'


def generar_codigo_unico(tipo, prefijo_sugerido=None):
    """
    Genera un código único para registros sin código
    """
    if tipo == 'libro':
        # Buscar códigos existentes que empiecen con SIN-LIB-
        max_codigo = Libro.objects.filter(
            codigo_nuevo__startswith='SIN-LIB-'
        ).count()
        return f'SIN-LIB-{max_codigo + 1:04d}'
    else:
        # Para tesis sin código
        max_codigo = TrabajoGrado.objects.filter(
            codigo_nuevo__startswith='SIN-TES-'
        ).count()
        return f'SIN-TES-{max_codigo + 1:04d}'


def importar_registro_libro(row, orden_importacion):
    """Importa un registro de libro"""
    titulo = limpiar_valor(row.get('TITULO', ''))
    if not titulo:
        return None, "Sin título"
    
    # Obtener código (puede ser None)
    raw_codigo = limpiar_valor(row.get('CODIGO NUEVO', ''))
    if not raw_codigo:
        raw_codigo = limpiar_valor(row.get('CODIGO NUEVO ', ''))
    
    # Si no hay código, generar uno temporal
    codigo = raw_codigo if raw_codigo else generar_codigo_unico('libro')
    
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
        'orden_importacion': orden_importacion,
    }
    
    # Verificar si ya existe un libro con este código
    if Libro.objects.filter(codigo_nuevo=codigo).exists():
        # Actualizar
        libro = Libro.objects.filter(codigo_nuevo=codigo).first()
        for key, value in datos.items():
            setattr(libro, key, value)
        libro.save()
        return libro, "actualizado"
    else:
        # Crear nuevo
        libro = Libro.objects.create(**datos)
        return libro, "creado"


def importar_registro_tesis(row):
    """Importa un registro de tesis/trabajo de grado"""
    titulo = limpiar_valor(row.get('TITULO', ''))
    if not titulo:
        return None, "Sin título"
    
    # Obtener código (puede ser None)
    raw_codigo = limpiar_valor(row.get('CODIGO NUEVO', ''))
    if not raw_codigo:
        raw_codigo = limpiar_valor(row.get('CODIGO NUEVO ', ''))
    
    # Si no hay código, generar uno temporal
    codigo = raw_codigo if raw_codigo else generar_codigo_unico('tesis')
    
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
        'ubicacion_seccion': limpiar_valor(row.get('SECCIÓN', '')),
        'ubicacion_repisa': limpiar_valor(row.get('REPISA', '')),
        'observaciones': limpiar_valor(row.get('OBSERVACIONES', '')),
    }
    
    # Verificar si ya existe una tesis con este código
    if TrabajoGrado.objects.filter(codigo_nuevo=codigo).exists():
        # Actualizar
        tesis = TrabajoGrado.objects.filter(codigo_nuevo=codigo).first()
        for key, value in datos.items():
            setattr(tesis, key, value)
        tesis.save()
        return tesis, "actualizado"
    else:
        # Crear nuevo
        tesis = TrabajoGrado.objects.create(**datos)
        return tesis, "creado"


def procesar_hoja(df, nombre_hoja):
    """Procesa una hoja del Excel"""
    print(f"\n{'='*80}")
    print(f"Procesando hoja: {nombre_hoja}")
    print(f"{'='*80}")
    
    # Normalizar nombres de columnas
    df.columns = df.columns.str.strip().str.upper()
    
    # Mostrar columnas disponibles
    print(f"Columnas encontradas: {', '.join(df.columns.tolist())}")
    
    # Estadísticas
    total_filas = len(df)
    libros_creados = 0
    libros_actualizados = 0
    tesis_creadas = 0
    tesis_actualizadas = 0
    omitidos = 0
    errores = 0
    
    # Obtener el último orden de importación para libros
    max_orden = Libro.objects.aggregate(max_orden=models.Max('orden_importacion'))['max_orden']
    orden_actual = (max_orden or 0) + 1
    
    print(f"Total de filas en la hoja: {total_filas}")
    print(f"Orden de importación inicial: {orden_actual}")
    print(f"\nIniciando importación...\n")
    
    with transaction.atomic():
        for idx, row in df.iterrows():
            try:
                # Detectar tipo de registro
                tipo = detectar_tipo_registro(row)
                
                if tipo == 'libro':
                    resultado, estado = importar_registro_libro(row, orden_actual)
                    if resultado:
                        if estado == "creado":
                            libros_creados += 1
                        elif estado == "actualizado":
                            libros_actualizados += 1
                        orden_actual += 1
                        if (libros_creados + libros_actualizados) % 50 == 0:
                            print(f"  Procesados {libros_creados + libros_actualizados} libros...")
                    else:
                        omitidos += 1
                else:  # tesis
                    resultado, estado = importar_registro_tesis(row)
                    if resultado:
                        if estado == "creado":
                            tesis_creadas += 1
                        elif estado == "actualizado":
                            tesis_actualizadas += 1
                        if (tesis_creadas + tesis_actualizadas) % 50 == 0:
                            print(f"  Procesadas {tesis_creadas + tesis_actualizadas} tesis...")
                    else:
                        omitidos += 1
                        
            except Exception as e:
                errores += 1
                print(f"⚠️ Error en fila {idx + 2}: {str(e)}")
    
    # Resumen
    print(f"\n{'='*80}")
    print(f"RESUMEN DE IMPORTACIÓN - {nombre_hoja}")
    print(f"{'='*80}")
    print(f"📚 Libros creados:      {libros_creados}")
    print(f"📝 Libros actualizados: {libros_actualizados}")
    print(f"🎓 Tesis creadas:       {tesis_creadas}")
    print(f"📄 Tesis actualizadas:  {tesis_actualizadas}")
    print(f"⏭️  Registros omitidos: {omitidos}")
    print(f"❌ Errores:             {errores}")
    print(f"{'='*80}\n")
    
    return {
        'libros_creados': libros_creados,
        'libros_actualizados': libros_actualizados,
        'tesis_creadas': tesis_creadas,
        'tesis_actualizadas': tesis_actualizadas,
        'omitidos': omitidos,
        'errores': errores
    }


def main():
    """Función principal"""
    archivo_excel = r'BASE DE EXISTENCIA DE LIBROS, PROYECTOS DE GRADO, TESIS Y TRABAJO DIRIGIDO (2).xlsx'
    
    if not os.path.exists(archivo_excel):
        print(f"❌ Error: No se encontró el archivo '{archivo_excel}'")
        return
    
    print(f"\n{'='*80}")
    print(f"IMPORTACIÓN DE NUEVA BASE DE DATOS")
    print(f"{'='*80}")
    print(f"Archivo: {archivo_excel}")
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*80}\n")
    
    try:
        # Leer todas las hojas del Excel
        excel_file = pd.ExcelFile(archivo_excel)
        print(f"Hojas encontradas en el archivo: {', '.join(excel_file.sheet_names)}\n")
        
        # Estadísticas totales
        total_stats = {
            'libros_creados': 0,
            'libros_actualizados': 0,
            'tesis_creadas': 0,
            'tesis_actualizadas': 0,
            'omitidos': 0,
            'errores': 0
        }
        
        # Procesar cada hoja
        for nombre_hoja in excel_file.sheet_names:
            try:
                df = pd.read_excel(archivo_excel, sheet_name=nombre_hoja)
                stats = procesar_hoja(df, nombre_hoja)
                
                # Acumular estadísticas
                for key in total_stats:
                    total_stats[key] += stats[key]
                    
            except Exception as e:
                print(f"❌ Error procesando hoja '{nombre_hoja}': {str(e)}\n")
        
        # Resumen final
        print(f"\n{'='*80}")
        print(f"RESUMEN FINAL DE IMPORTACIÓN")
        print(f"{'='*80}")
        print(f"📚 Total libros creados:      {total_stats['libros_creados']}")
        print(f"📝 Total libros actualizados: {total_stats['libros_actualizados']}")
        print(f"🎓 Total tesis creadas:       {total_stats['tesis_creadas']}")
        print(f"📄 Total tesis actualizadas:  {total_stats['tesis_actualizadas']}")
        print(f"⏭️  Total registros omitidos: {total_stats['omitidos']}")
        print(f"❌ Total errores:             {total_stats['errores']}")
        print(f"{'='*80}")
        print(f"\n✅ Importación completada exitosamente!")
        
        # Verificar totales en la base de datos
        total_libros = Libro.objects.count()
        total_tesis = TrabajoGrado.objects.count()
        libros_sin_codigo = Libro.objects.filter(codigo_nuevo__startswith='SIN-LIB-').count()
        tesis_sin_codigo = TrabajoGrado.objects.filter(codigo_nuevo__startswith='SIN-TES-').count()
        
        print(f"\n{'='*80}")
        print(f"ESTADO ACTUAL DE LA BASE DE DATOS")
        print(f"{'='*80}")
        print(f"📚 Total libros en BD:           {total_libros}")
        print(f"🎓 Total tesis en BD:            {total_tesis}")
        print(f"📝 Libros sin código original:   {libros_sin_codigo}")
        print(f"📄 Tesis sin código original:    {tesis_sin_codigo}")
        print(f"{'='*80}\n")
        
    except Exception as e:
        print(f"\n❌ Error general: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    from django.db.models import Max
    main()
