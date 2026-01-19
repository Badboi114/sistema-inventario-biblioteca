import pandas as pd
import os
import django
from django.db import transaction

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from inventario.models import TrabajoGrado, Libro, Prestamo

# Ruta al archivo Excel
EXCEL_FILE = r"C:\Users\4dm1n\OneDrive - Universidad Privada Domingo Savio\Escritorio\a\SISTEMA DE INVENTARIO DE BIBLIOTECA\BASE DE EXISTENCIA DE LIBROS, PROYECTOS DE GRADO, TESIS Y TRABAJO DIRIGIDO (2).xlsx"

# Hojas de TESIS
HOJAS_TESIS = [
    'LISTA DE PROYECTOS DE GRADO (2)',
    'Tabla7',
    'LISTA DE PROYECTOS DE GRADO'
]

# Hojas de LIBROS
HOJAS_LIBROS = [
    'LISTA DE LIBROS ACADEMICOS',
    'LIBROS DE LECTURA',
    'PARA REPORTE'
]

def limpiar_valor(valor):
    """Limpia un valor del Excel, retorna None si está vacío"""
    if pd.isna(valor):
        return None
    valor_str = str(valor).strip()
    if valor_str.lower() in ['nan', '', 'none']:
        return None
    return valor_str

def parse_anio(valor):
    """Convierte un valor a año entero válido"""
    if pd.isna(valor):
        return None
    try:
        anio = int(float(valor))
        if 1900 <= anio <= 2100:
            return anio
    except:
        pass
    return None

def normalizar_estado(estado):
    """Normaliza el estado a valores permitidos"""
    if not estado:
        return 'REGULAR'
    estado_upper = str(estado).upper().strip()
    if 'BUEN' in estado_upper or estado_upper == 'B':
        return 'BUENO'
    elif 'MAL' in estado_upper or estado_upper == 'M':
        return 'MALO'
    else:
        return 'REGULAR'

print("="*80)
print("IMPORTACIÓN EXACTA POR FILAS DEL EXCEL")
print("="*80)
print("\nESTRATEGIA: Importar CADA FILA que tenga título válido")
print("- No importa si tiene código o no")
print("- Cada fila con título = 1 registro en la base de datos")
print("="*80)

# ============================================================================
# PASO 1: LIMPIAR TODA LA BASE DE DATOS
# ============================================================================
print("\n[PASO 1] Limpiando base de datos...")

with transaction.atomic():
    prestamos_eliminados = Prestamo.objects.all().delete()[0]
    libros_eliminados = Libro.objects.all().delete()[0]
    tesis_eliminadas = TrabajoGrado.objects.all().delete()[0]

print(f"   [OK] Eliminados: {prestamos_eliminados} préstamos, {libros_eliminados} libros, {tesis_eliminadas} tesis")

# ============================================================================
# PASO 2: IMPORTAR TESIS (CADA FILA CON TÍTULO)
# ============================================================================
print("\n[PASO 2] Importando TESIS...")

tesis_creadas = 0
tesis_sin_titulo = 0
contador_sin_codigo = 0

for hoja in HOJAS_TESIS:
    print(f"\n   Procesando hoja: {hoja}")
    
    try:
        df = pd.read_excel(EXCEL_FILE, sheet_name=hoja)
        # Limpiar nombres de columnas (quitar espacios)
        df.columns = df.columns.str.strip()
        
        filas_hoja = 0
        
        for _, row in df.iterrows():
            # Extraer campos
            codigo_nuevo = limpiar_valor(row.get('CODIGO NUEVO'))
            titulo = limpiar_valor(row.get('TITULO'))
            autor = limpiar_valor(row.get('AUTOR'))
            anio = parse_anio(row.get('AÑO'))
            estado = normalizar_estado(row.get('ESTADO'))
            ubicacion_seccion = limpiar_valor(row.get('SECCION'))
            ubicacion_repisa = limpiar_valor(row.get('REPISA'))
            facultad = limpiar_valor(row.get('FACULTAD'))
            observaciones = limpiar_valor(row.get('OBSERVACIONES'))
            modalidad = limpiar_valor(row.get('MODALIDAD'))
            tutor = limpiar_valor(row.get('TUTOR'))
            carrera = limpiar_valor(row.get('CARRERA'))
            
            # CRITERIO: Si hay título, es una tesis válida
            if not titulo:
                tesis_sin_titulo += 1
                continue
            
            # Si no tiene código, generar uno
            if not codigo_nuevo:
                contador_sin_codigo += 1
                codigo_nuevo = f'SIN-CODIGO-T-{contador_sin_codigo:04d}'
                print(f"      [INFO] Tesis sin código, asignando: {codigo_nuevo} - {titulo[:50]}")
            
            # Crear la tesis
            try:
                TrabajoGrado.objects.create(
                    codigo_nuevo=codigo_nuevo,
                    titulo=titulo,
                    autor=autor,
                    anio=anio,
                    estado=estado,
                    ubicacion_seccion=ubicacion_seccion,
                    ubicacion_repisa=ubicacion_repisa,
                    facultad=facultad,
                    observaciones=observaciones,
                    modalidad=modalidad,
                    tutor=tutor,
                    carrera=carrera
                )
                tesis_creadas += 1
                filas_hoja += 1
            except Exception as e:
                print(f"      [ERROR] No se pudo crear tesis: {titulo[:50]} - {e}")
        
        print(f"      [OK] Importadas: {filas_hoja} tesis")
        
    except Exception as e:
        print(f"      [ERROR] No se pudo leer la hoja: {e}")

print(f"\n   [OK] TESIS creadas: {tesis_creadas}")
print(f"   [INFO] TESIS sin título (omitidas): {tesis_sin_titulo}")

# ============================================================================
# PASO 3: IMPORTAR LIBROS (CADA FILA CON TÍTULO)
# ============================================================================
print("\n[PASO 3] Importando LIBROS...")

libros_creados = 0
libros_sin_titulo = 0
contador_sin_codigo_libro = 0

for hoja in HOJAS_LIBROS:
    print(f"\n   Procesando hoja: {hoja}")
    
    try:
        df = pd.read_excel(EXCEL_FILE, sheet_name=hoja)
        # Limpiar nombres de columnas
        df.columns = df.columns.str.strip()
        
        filas_hoja = 0
        
        for _, row in df.iterrows():
            # Extraer campos
            codigo_nuevo = limpiar_valor(row.get('CODIGO NUEVO'))
            titulo = limpiar_valor(row.get('TITULO'))
            autor = limpiar_valor(row.get('AUTOR'))
            anio = parse_anio(row.get('AÑO'))
            estado = normalizar_estado(row.get('ESTADO'))
            ubicacion_seccion = limpiar_valor(row.get('SECCION'))
            ubicacion_repisa = limpiar_valor(row.get('REPISA'))
            facultad = limpiar_valor(row.get('FACULTAD'))
            observaciones = limpiar_valor(row.get('OBSERVACIONES'))
            materia = limpiar_valor(row.get('MATERIA'))
            editorial = limpiar_valor(row.get('EDITORIAL'))
            edicion = limpiar_valor(row.get('EDICION'))
            
            # CRITERIO: Si hay título, es un libro válido
            if not titulo:
                libros_sin_titulo += 1
                continue
            
            # Si no tiene código, generar uno
            if not codigo_nuevo:
                contador_sin_codigo_libro += 1
                codigo_nuevo = f'SIN-CODIGO-L-{contador_sin_codigo_libro:04d}'
                # No imprimir cada uno para no saturar la consola
            
            # Crear el libro
            try:
                Libro.objects.create(
                    codigo_nuevo=codigo_nuevo,
                    titulo=titulo,
                    autor=autor,
                    anio=anio,
                    estado=estado,
                    ubicacion_seccion=ubicacion_seccion,
                    ubicacion_repisa=ubicacion_repisa,
                    facultad=facultad,
                    observaciones=observaciones,
                    materia=materia,
                    editorial=editorial,
                    edicion=edicion
                )
                libros_creados += 1
                filas_hoja += 1
            except Exception as e:
                print(f"      [ERROR] No se pudo crear libro: {titulo[:50]} - {e}")
        
        print(f"      [OK] Importados: {filas_hoja} libros")
        
    except Exception as e:
        print(f"      [ERROR] No se pudo leer la hoja: {e}")

print(f"\n   [OK] LIBROS creados: {libros_creados}")
print(f"   [INFO] LIBROS sin título (omitidos): {libros_sin_titulo}")
print(f"   [INFO] Códigos generados para libros sin código: {contador_sin_codigo_libro}")

# ============================================================================
# PASO 4: VERIFICACIÓN FINAL
# ============================================================================
print("\n" + "="*80)
print("VERIFICACIÓN FINAL")
print("="*80)

tesis_bd = TrabajoGrado.objects.count()
libros_bd = Libro.objects.count()

print(f"\nBase de Datos:")
print(f"  Tesis:  {tesis_bd}")
print(f"  Libros: {libros_bd}")
print(f"  TOTAL:  {tesis_bd + libros_bd}")

# Verificar contra el Excel
print(f"\nExcel (filas con título válido):")
total_tesis_excel = 0
total_libros_excel = 0

for hoja in HOJAS_TESIS:
    df = pd.read_excel(EXCEL_FILE, sheet_name=hoja)
    df.columns = df.columns.str.strip()
    for _, row in df.iterrows():
        if limpiar_valor(row.get('TITULO')):
            total_tesis_excel += 1

for hoja in HOJAS_LIBROS:
    df = pd.read_excel(EXCEL_FILE, sheet_name=hoja)
    df.columns = df.columns.str.strip()
    for _, row in df.iterrows():
        if limpiar_valor(row.get('TITULO')):
            total_libros_excel += 1

print(f"  Tesis:  {total_tesis_excel}")
print(f"  Libros: {total_libros_excel}")
print(f"  TOTAL:  {total_tesis_excel + total_libros_excel}")

print(f"\n¿Coinciden exactamente?")
print(f"  Tesis:  {'✅ SÍ' if tesis_bd == total_tesis_excel else f'❌ NO (BD: {tesis_bd}, Excel: {total_tesis_excel})'}")
print(f"  Libros: {'✅ SÍ' if libros_bd == total_libros_excel else f'❌ NO (BD: {libros_bd}, Excel: {total_libros_excel})'}")

print("\n" + "="*80)
print("IMPORTACIÓN COMPLETADA")
print("="*80)
