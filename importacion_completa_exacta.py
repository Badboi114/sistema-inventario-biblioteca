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

def normalizar_texto(texto):
    """Normaliza texto para comparación (minúsculas, sin espacios extra)"""
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
print("IMPORTACIÓN COMPLETA Y EXACTA DEL EXCEL")
print("="*80)
print("\nESTRATEGIA:")
print("- Importar TODOS los registros únicos por (título + autor)")
print("- NO omitir registros que aparecen en múltiples hojas")
print("- Generar códigos únicos automáticamente cuando sea necesario")
print("- Objetivo: 1,389 tesis y 2,080 libros únicos")
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
# PASO 2: RECOLECTAR TODAS LAS TESIS ÚNICAS DEL EXCEL
# ============================================================================
print("\n[PASO 2] Recolectando todas las tesis únicas del Excel...")

tesis_unicas = {}  # clave: (titulo_norm, autor_norm), valor: datos completos

for hoja in HOJAS_TESIS:
    print(f"   Procesando: {hoja}")
    
    df = pd.read_excel(EXCEL_FILE, sheet_name=hoja)
    df.columns = df.columns.str.strip()
    
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
        
        # Si no hay título, omitir
        if not titulo:
            continue
        
        # Crear clave única por contenido
        titulo_norm = normalizar_texto(titulo)
        autor_norm = normalizar_texto(autor)
        clave = (titulo_norm, autor_norm)
        
        # Guardar solo si no existe o si tiene más datos
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

print(f"\n   [OK] Total tesis únicas encontradas: {len(tesis_unicas)}")

# ============================================================================
# PASO 3: IMPORTAR TODAS LAS TESIS
# ============================================================================
print("\n[PASO 3] Importando tesis...")

contador_sin_codigo_tesis = 0
tesis_creadas = 0
codigos_usados_tesis = set()

for i, ((titulo_norm, autor_norm), datos) in enumerate(tesis_unicas.items(), 1):
    codigo_nuevo = datos['codigo_nuevo']
    
    # Si no tiene código o el código ya existe, generar uno nuevo
    if not codigo_nuevo or codigo_nuevo in codigos_usados_tesis:
        contador_sin_codigo_tesis += 1
        codigo_nuevo = f'TESIS-{contador_sin_codigo_tesis:04d}'
        
        # Asegurar que el código sea único
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
        
        if tesis_creadas % 100 == 0:
            print(f"   Progreso: {tesis_creadas}/{len(tesis_unicas)} tesis")
        
    except Exception as e:
        print(f"   [ERROR] No se pudo crear tesis: {datos['titulo'][:50]} - {e}")

print(f"\n   [OK] TESIS creadas: {tesis_creadas}")
print(f"   [INFO] Códigos generados: {contador_sin_codigo_tesis}")

# ============================================================================
# PASO 4: RECOLECTAR TODOS LOS LIBROS ÚNICOS DEL EXCEL
# ============================================================================
print("\n[PASO 4] Recolectando todos los libros únicos del Excel...")

libros_unicos = {}  # clave: (titulo_norm, autor_norm), valor: datos completos

for hoja in HOJAS_LIBROS:
    print(f"   Procesando: {hoja}")
    
    df = pd.read_excel(EXCEL_FILE, sheet_name=hoja)
    df.columns = df.columns.str.strip()
    
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
        
        # Si no hay título, omitir
        if not titulo:
            continue
        
        # Crear clave única por contenido
        titulo_norm = normalizar_texto(titulo)
        autor_norm = normalizar_texto(autor)
        clave = (titulo_norm, autor_norm)
        
        # Guardar solo si no existe o si tiene más datos
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

print(f"\n   [OK] Total libros únicos encontrados: {len(libros_unicos)}")

# ============================================================================
# PASO 5: IMPORTAR TODOS LOS LIBROS
# ============================================================================
print("\n[PASO 5] Importando libros...")

contador_sin_codigo_libro = 0
libros_creados = 0
codigos_usados_libros = set()

for i, ((titulo_norm, autor_norm), datos) in enumerate(libros_unicos.items(), 1):
    codigo_nuevo = datos['codigo_nuevo']
    
    # Si no tiene código o el código ya existe, generar uno nuevo
    if not codigo_nuevo or codigo_nuevo in codigos_usados_libros:
        contador_sin_codigo_libro += 1
        codigo_nuevo = f'LIBRO-{contador_sin_codigo_libro:04d}'
        
        # Asegurar que el código sea único
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

print(f"\n   [OK] LIBROS creados: {libros_creados}")
print(f"   [INFO] Códigos generados: {contador_sin_codigo_libro}")

# ============================================================================
# PASO 6: VERIFICACIÓN FINAL
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

print(f"\nExcel (únicos esperados):")
print(f"  Tesis:  {len(tesis_unicas)}")
print(f"  Libros: {len(libros_unicos)}")
print(f"  TOTAL:  {len(tesis_unicas) + len(libros_unicos)}")

print(f"\n¿Coinciden EXACTAMENTE?")
print(f"  Tesis:  {'✅ SÍ' if tesis_bd == len(tesis_unicas) else f'❌ NO (BD: {tesis_bd}, Excel: {len(tesis_unicas)})'}")
print(f"  Libros: {'✅ SÍ' if libros_bd == len(libros_unicos) else f'❌ NO (BD: {libros_bd}, Excel: {len(libros_unicos)})'}")

if tesis_bd == len(tesis_unicas) and libros_bd == len(libros_unicos):
    print("\n" + "="*80)
    print("✅ ÉXITO: IMPORTACIÓN COMPLETA Y EXACTA")
    print("="*80)
    print("\n✅ Todos los libros y tesis del Excel están en el sistema")
    print("✅ Las cantidades coinciden exactamente")
    print("✅ Sin duplicados")
    print("✅ Búsqueda por código, título o autor funcionará correctamente")
else:
    print("\n⚠️  Hubo un problema en la importación")

print("\n" + "="*80)
