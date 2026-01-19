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

# SOLO estas hojas específicas
HOJA_TESIS = 'LISTA DE PROYECTOS DE GRADO (2)'
HOJA_LIBROS = 'LISTA DE LIBROS ACADEMICOS'

def limpiar_valor(valor):
    """Limpia un valor del Excel, retorna None si está vacío"""
    if pd.isna(valor):
        return None
    valor_str = str(valor).strip()
    if valor_str.lower() in ['nan', '', 'none']:
        return None
    return valor_str

def normalizar_texto(texto):
    """Normaliza texto para comparación"""
    if not texto:
        return ""
    return " ".join(str(texto).lower().strip().split())

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
print("IMPORTACIÓN DE HOJAS ESPECÍFICAS")
print("="*80)
print(f"\nSOLO se importarán:")
print(f"  - TESIS: '{HOJA_TESIS}'")
print(f"  - LIBROS: '{HOJA_LIBROS}'")
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
# PASO 2: IMPORTAR TESIS DE "LISTA DE PROYECTOS DE GRADO (2)"
# ============================================================================
print(f"\n[PASO 2] Importando TESIS de '{HOJA_TESIS}'...")

df_tesis = pd.read_excel(EXCEL_FILE, sheet_name=HOJA_TESIS)
df_tesis.columns = df_tesis.columns.str.strip()

print(f"   Total filas en la hoja: {len(df_tesis)}")

tesis_unicas = {}  # clave: (titulo_norm, autor_norm), valor: datos
contador_sin_codigo_tesis = 0

for _, row in df_tesis.iterrows():
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
    
    # Si no hay título, omitir
    if not titulo:
        continue
    
    # Crear clave única por contenido
    titulo_norm = normalizar_texto(titulo)
    autor_norm = normalizar_texto(autor)
    clave = (titulo_norm, autor_norm)
    
    # Guardar solo la primera ocurrencia de cada tesis única
    if clave not in tesis_unicas:
        tesis_unicas[clave] = {
            'codigo_nuevo': codigo_nuevo,
            'titulo': titulo,
            'autor': autor,
            'anio': anio,
            'estado': estado,
            'ubicacion_seccion': ubicacion_seccion,
            'ubicacion_repisa': ubicacion_repisa,
            'facultad': facultad,
            'observaciones': observaciones,
            'modalidad': modalidad,
            'tutor': tutor,
            'carrera': carrera
        }

print(f"   Tesis únicas (título+autor): {len(tesis_unicas)}")

# Importar tesis
tesis_creadas = 0
codigos_usados_tesis = set()

for (titulo_norm, autor_norm), datos in tesis_unicas.items():
    codigo_nuevo = datos['codigo_nuevo']
    
    # Si no tiene código o el código ya existe, generar uno nuevo
    if not codigo_nuevo or codigo_nuevo in codigos_usados_tesis:
        contador_sin_codigo_tesis += 1
        codigo_nuevo = f'TESIS-{contador_sin_codigo_tesis:04d}'
        
        while codigo_nuevo in codigos_usados_tesis:
            contador_sin_codigo_tesis += 1
            codigo_nuevo = f'TESIS-{contador_sin_codigo_tesis:04d}'
    
    try:
        TrabajoGrado.objects.create(
            codigo_nuevo=codigo_nuevo,
            titulo=datos['titulo'],
            autor=datos['autor'],
            anio=datos['anio'],
            estado=datos['estado'],
            ubicacion_seccion=datos['ubicacion_seccion'],
            ubicacion_repisa=datos['ubicacion_repisa'],
            facultad=datos['facultad'],
            observaciones=datos['observaciones'],
            modalidad=datos['modalidad'],
            tutor=datos['tutor'],
            carrera=datos['carrera']
        )
        
        codigos_usados_tesis.add(codigo_nuevo)
        tesis_creadas += 1
        
    except Exception as e:
        print(f"   [ERROR] No se pudo crear tesis: {datos['titulo'][:50]} - {e}")

print(f"   [OK] TESIS creadas: {tesis_creadas}")
print(f"   [INFO] Códigos generados: {contador_sin_codigo_tesis}")

# ============================================================================
# PASO 3: IMPORTAR LIBROS DE "LISTA DE LIBROS ACADEMICOS"
# ============================================================================
print(f"\n[PASO 3] Importando LIBROS de '{HOJA_LIBROS}'...")

df_libros = pd.read_excel(EXCEL_FILE, sheet_name=HOJA_LIBROS)
df_libros.columns = df_libros.columns.str.strip()

print(f"   Total filas en la hoja: {len(df_libros)}")

libros_unicos = {}  # clave: (titulo_norm, autor_norm), valor: datos
contador_sin_codigo_libro = 0

for _, row in df_libros.iterrows():
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
    
    # Si no hay título, omitir
    if not titulo:
        continue
    
    # Crear clave única por contenido
    titulo_norm = normalizar_texto(titulo)
    autor_norm = normalizar_texto(autor)
    clave = (titulo_norm, autor_norm)
    
    # Guardar solo la primera ocurrencia de cada libro único
    if clave not in libros_unicos:
        libros_unicos[clave] = {
            'codigo_nuevo': codigo_nuevo,
            'titulo': titulo,
            'autor': autor,
            'anio': anio,
            'estado': estado,
            'ubicacion_seccion': ubicacion_seccion,
            'ubicacion_repisa': ubicacion_repisa,
            'facultad': facultad,
            'observaciones': observaciones,
            'materia': materia,
            'editorial': editorial,
            'edicion': edicion
        }

print(f"   Libros únicos (título+autor): {len(libros_unicos)}")

# Importar libros
libros_creados = 0
codigos_usados_libros = set()

for (titulo_norm, autor_norm), datos in libros_unicos.items():
    codigo_nuevo = datos['codigo_nuevo']
    
    # Si no tiene código o el código ya existe, generar uno nuevo
    if not codigo_nuevo or codigo_nuevo in codigos_usados_libros:
        contador_sin_codigo_libro += 1
        codigo_nuevo = f'LIBRO-{contador_sin_codigo_libro:04d}'
        
        while codigo_nuevo in codigos_usados_libros:
            contador_sin_codigo_libro += 1
            codigo_nuevo = f'LIBRO-{contador_sin_codigo_libro:04d}'
    
    try:
        Libro.objects.create(
            codigo_nuevo=codigo_nuevo,
            titulo=datos['titulo'],
            autor=datos['autor'],
            anio=datos['anio'],
            estado=datos['estado'],
            ubicacion_seccion=datos['ubicacion_seccion'],
            ubicacion_repisa=datos['ubicacion_repisa'],
            facultad=datos['facultad'],
            observaciones=datos['observaciones'],
            materia=datos['materia'],
            editorial=datos['editorial'],
            edicion=datos['edicion']
        )
        
        codigos_usados_libros.add(codigo_nuevo)
        libros_creados += 1
        
        if libros_creados % 200 == 0:
            print(f"   Progreso: {libros_creados}/{len(libros_unicos)} libros")
        
    except Exception as e:
        print(f"   [ERROR] No se pudo crear libro: {datos['titulo'][:50]} - {e}")

print(f"   [OK] LIBROS creados: {libros_creados}")
print(f"   [INFO] Códigos generados: {contador_sin_codigo_libro}")

# ============================================================================
# VERIFICACIÓN FINAL
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

print(f"\nExcel (hojas específicas):")
print(f"  Tesis únicos de '{HOJA_TESIS}': {len(tesis_unicas)}")
print(f"  Libros únicos de '{HOJA_LIBROS}': {len(libros_unicos)}")
print(f"  TOTAL:  {len(tesis_unicas) + len(libros_unicos)}")

print(f"\n¿Coinciden EXACTAMENTE?")
print(f"  Tesis:  {'✅ SÍ' if tesis_bd == len(tesis_unicas) else f'❌ NO'}")
print(f"  Libros: {'✅ SÍ' if libros_bd == len(libros_unicos) else f'❌ NO'}")

if tesis_bd == len(tesis_unicas) and libros_bd == len(libros_unicos):
    print("\n" + "="*80)
    print("✅ ÉXITO: IMPORTACIÓN COMPLETADA")
    print("="*80)
    print(f"\n✅ Solo se importaron las hojas especificadas")
    print(f"✅ Tesis de '{HOJA_TESIS}'")
    print(f"✅ Libros de '{HOJA_LIBROS}'")
    print(f"✅ Sin duplicados")

print("\n" + "="*80)
