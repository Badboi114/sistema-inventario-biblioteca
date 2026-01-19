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
print("IMPORTACIÓN DE LIBROS Y TESIS ÚNICOS POR CÓDIGO")
print("="*80)
print("\nESTRATEGIA: Importar solo registros con código único")
print("- Tesis: por código único")
print("- Libros: por código único")
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
# PASO 2: IMPORTAR TESIS (SOLO CÓDIGOS ÚNICOS)
# ============================================================================
print("\n[PASO 2] Importando TESIS (solo códigos únicos)...")

codigos_tesis_vistos = set()
tesis_creadas = 0
tesis_duplicadas = 0
tesis_sin_codigo = 0

for hoja in HOJAS_TESIS:
    print(f"\n   Procesando hoja: {hoja}")
    
    try:
        df = pd.read_excel(EXCEL_FILE, sheet_name=hoja)
        # Limpiar nombres de columnas
        df.columns = df.columns.str.strip()
        
        filas_importadas = 0
        
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
            
            # CRITERIO: Solo si tiene título Y código válidos
            if not titulo:
                continue
                
            if not codigo_nuevo:
                tesis_sin_codigo += 1
                continue
            
            # Si ya vimos este código, es duplicado
            if codigo_nuevo in codigos_tesis_vistos:
                tesis_duplicadas += 1
                continue
            
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
                codigos_tesis_vistos.add(codigo_nuevo)
                tesis_creadas += 1
                filas_importadas += 1
            except Exception as e:
                print(f"      [ERROR] No se pudo crear tesis: {titulo[:50]} - {e}")
        
        print(f"      [OK] Importadas: {filas_importadas} tesis únicas")
        
    except Exception as e:
        print(f"      [ERROR] No se pudo leer la hoja: {e}")

print(f"\n   [OK] TESIS creadas: {tesis_creadas}")
print(f"   [INFO] TESIS duplicadas (omitidas): {tesis_duplicadas}")
print(f"   [INFO] TESIS sin código (omitidas): {tesis_sin_codigo}")

# ============================================================================
# PASO 3: IMPORTAR LIBROS (SOLO CÓDIGOS ÚNICOS)
# ============================================================================
print("\n[PASO 3] Importando LIBROS (solo códigos únicos)...")

codigos_libros_vistos = set()
libros_creados = 0
libros_duplicados = 0
libros_sin_codigo = 0

for hoja in HOJAS_LIBROS:
    print(f"\n   Procesando hoja: {hoja}")
    
    try:
        df = pd.read_excel(EXCEL_FILE, sheet_name=hoja)
        # Limpiar nombres de columnas
        df.columns = df.columns.str.strip()
        
        filas_importadas = 0
        
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
            
            # CRITERIO: Solo si tiene título Y código válidos
            if not titulo:
                continue
                
            if not codigo_nuevo:
                libros_sin_codigo += 1
                continue
            
            # Si ya vimos este código, es duplicado
            if codigo_nuevo in codigos_libros_vistos:
                libros_duplicados += 1
                continue
            
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
                codigos_libros_vistos.add(codigo_nuevo)
                libros_creados += 1
                filas_importadas += 1
            except Exception as e:
                print(f"      [ERROR] No se pudo crear libro: {titulo[:50]} - {e}")
        
        print(f"      [OK] Importados: {filas_importadas} libros únicos")
        
    except Exception as e:
        print(f"      [ERROR] No se pudo leer la hoja: {e}")

print(f"\n   [OK] LIBROS creados: {libros_creados}")
print(f"   [INFO] LIBROS duplicados (omitidos): {libros_duplicados}")
print(f"   [INFO] LIBROS sin código (omitidos): {libros_sin_codigo}")

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

print(f"\nCódigos únicos esperados del Excel:")
print(f"  Tesis:  {len(codigos_tesis_vistos)}")
print(f"  Libros: {len(codigos_libros_vistos)}")

print(f"\n¿Coinciden exactamente?")
print(f"  Tesis:  {'✅ SÍ' if tesis_bd == len(codigos_tesis_vistos) else '❌ NO'}")
print(f"  Libros: {'✅ SÍ' if libros_bd == len(codigos_libros_vistos) else '❌ NO'}")

print("\n" + "="*80)
print("IMPORTACIÓN COMPLETADA")
print("="*80)
