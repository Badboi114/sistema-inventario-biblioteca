"""
Script para importar SOLO las hojas principales sin duplicados
- LISTA DE LIBROS ACADEMICOS: 1704 libros académicos
- LIBROS DE LECTURA: 412 libros de lectura
- LISTA DE PROYECTOS DE GRADO (2): Tesis/proyectos (la más actualizada)
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


def importar_libros(df, nombre_hoja, orden_inicial):
    """Importa libros desde un DataFrame"""
    print(f"\n{'='*80}")
    print(f"Importando: {nombre_hoja}")
    print(f"{'='*80}")
    
    # Normalizar nombres de columnas
    df.columns = df.columns.str.strip().str.upper()
    
    creados = 0
    actualizados = 0
    omitidos = 0
    sin_codigo_count = 0
    orden_actual = orden_inicial
    
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
                
                # Verificar si existe por código o coincidencia total de título, autor y año
                libro_qs = Libro.objects.filter(
                    models.Q(codigo_nuevo=codigo) |
                    (
                        models.Q(titulo=datos['titulo']) &
                        models.Q(autor=datos['autor']) &
                        models.Q(anio=datos['anio'])
                    )
                )
                if libro_qs.exists():
                    libro = libro_qs.first()
                    for key, value in datos.items():
                        setattr(libro, key, value)
                    libro.save()
                    actualizados += 1
                else:
                    Libro.objects.create(**datos)
                    creados += 1
                
                orden_actual += 1
                
                if (creados + actualizados) % 100 == 0:
                    print(f"  Procesados: {creados + actualizados}")
                    
            except Exception as e:
                print(f"⚠️ Error en fila {idx + 2}: {str(e)}")
    
    print(f"\n📊 Resultados:")
    print(f"  ✅ Creados: {creados}")
    print(f"  🔄 Actualizados: {actualizados}")
    print(f"  📝 Sin código: {sin_codigo_count}")
    print(f"  ⏭️ Omitidos: {omitidos}")
    
    return orden_actual, creados, actualizados, sin_codigo_count


def importar_tesis(df, nombre_hoja):
    """Importa tesis desde un DataFrame"""
    print(f"\n{'='*80}")
    print(f"Importando: {nombre_hoja}")
    print(f"{'='*80}")
    
    # Normalizar nombres de columnas
    df.columns = df.columns.str.strip().str.upper()
    
    creados = 0
    actualizados = 0
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
                
                # Verificar si existe por código o coincidencia total de título, autor y año
                tesis_qs = TrabajoGrado.objects.filter(
                    models.Q(codigo_nuevo=codigo) |
                    (
                        models.Q(titulo=datos['titulo']) &
                        models.Q(autor=datos['autor']) &
                        models.Q(anio=datos['anio'])
                    )
                )
                if tesis_qs.exists():
                    tesis = tesis_qs.first()
                    for key, value in datos.items():
                        setattr(tesis, key, value)
                    tesis.save()
                    actualizados += 1
                else:
                    TrabajoGrado.objects.create(**datos)
                    creados += 1
                
                if (creados + actualizados) % 100 == 0:
                    print(f"  Procesados: {creados + actualizados}")
                    
            except Exception as e:
                print(f"⚠️ Error en fila {idx + 2}: {str(e)}")
    
    print(f"\n📊 Resultados:")
    print(f"  ✅ Creadas: {creados}")
    print(f"  🔄 Actualizadas: {actualizados}")
    print(f"  📝 Sin código: {sin_codigo_count}")
    print(f"  ⏭️ Omitidas: {omitidos}")
    
    return creados, actualizados, sin_codigo_count


def main():
    """Función principal"""
    archivo_excel = r'BASE DE EXISTENCIA DE LIBROS, PROYECTOS DE GRADO, TESIS Y TRABAJO DIRIGIDO (2).xlsx'
    
    if not os.path.exists(archivo_excel):
        print(f"❌ Error: No se encontró el archivo '{archivo_excel}'")
        return
    
    print(f"\n{'='*80}")
    print(f"IMPORTACIÓN CORRECTA - SIN DUPLICADOS")
    print(f"{'='*80}")
    print(f"Archivo: {archivo_excel}")
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Verificar estado inicial
    print(f"\nEstado inicial:")
    print(f"  Libros: {Libro.objects.count()}")
    print(f"  Tesis: {TrabajoGrado.objects.count()}")
    
    try:
        excel_file = pd.ExcelFile(archivo_excel)
        
        # Estadísticas totales
        total_libros_creados = 0
        total_libros_actualizados = 0
        total_tesis_creadas = 0
        total_tesis_actualizadas = 0
        total_sin_codigo = 0
        
        # Obtener el último orden de importación
        max_orden = Libro.objects.aggregate(max_orden=models.Max('orden_importacion'))['max_orden']
        orden_actual = (max_orden or 0) + 1
        
        # IMPORTAR SOLO LAS HOJAS PRINCIPALES
        
        # 1. LISTA DE LIBROS ACADEMICOS (1704 libros)
        print(f"\n{'='*80}")
        print("FASE 1: LIBROS ACADÉMICOS")
        print(f"{'='*80}")
        df_libros = pd.read_excel(archivo_excel, sheet_name='LISTA DE LIBROS ACADEMICOS')
        orden_actual, creados, actualizados, sin_codigo = importar_libros(df_libros, 'LISTA DE LIBROS ACADEMICOS', orden_actual)
        total_libros_creados += creados
        total_libros_actualizados += actualizados
        total_sin_codigo += sin_codigo
        
        # 2. LIBROS DE LECTURA (412 libros adicionales)
        print(f"\n{'='*80}")
        print("FASE 2: LIBROS DE LECTURA")
        print(f"{'='*80}")
        df_lectura = pd.read_excel(archivo_excel, sheet_name='LIBROS DE LECTURA')
        orden_actual, creados, actualizados, sin_codigo = importar_libros(df_lectura, 'LIBROS DE LECTURA', orden_actual)
        total_libros_creados += creados
        total_libros_actualizados += actualizados
        total_sin_codigo += sin_codigo
        
        # 3. LISTA DE PROYECTOS DE GRADO (2) - La más actualizada con 744 registros
        print(f"\n{'='*80}")
        print("FASE 3: TESIS Y PROYECTOS DE GRADO")
        print(f"{'='*80}")
        df_tesis = pd.read_excel(archivo_excel, sheet_name='LISTA DE PROYECTOS DE GRADO (2)')
        creados, actualizados, sin_codigo = importar_tesis(df_tesis, 'LISTA DE PROYECTOS DE GRADO (2)')
        total_tesis_creadas += creados
        total_tesis_actualizadas += actualizados
        
        # Resumen final
        print(f"\n{'='*80}")
        print(f"RESUMEN FINAL")
        print(f"{'='*80}")
        print(f"📚 Libros creados:      {total_libros_creados}")
        print(f"📝 Libros actualizados: {total_libros_actualizados}")
        print(f"🎓 Tesis creadas:       {total_tesis_creadas}")
        print(f"📄 Tesis actualizadas:  {total_tesis_actualizadas}")
        print(f"📝 Sin código original: {total_sin_codigo}")
        
        # Verificar totales en BD
        total_libros = Libro.objects.count()
        total_tesis = TrabajoGrado.objects.count()
        
        print(f"\n{'='*80}")
        print(f"ESTADO FINAL DE LA BASE DE DATOS")
        print(f"{'='*80}")
        print(f"📚 Total libros:  {total_libros}")
        print(f"🎓 Total tesis:   {total_tesis}")
        print(f"{'='*80}")
        
        # Verificación
        esperado_libros = 1704 + 412  # 2116 (si incluimos libros de lectura)
        print(f"\n✅ Esperado (sin duplicados): ~{esperado_libros} libros + ~744 tesis")
        print(f"✅ Obtenido: {total_libros} libros + {total_tesis} tesis")
        
    except Exception as e:
        print(f"\n❌ Error general: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
