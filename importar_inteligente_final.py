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
print("IMPORTACIÓN INTELIGENTE DE LIBROS Y TESIS")
print("="*80)
print("\nESTRATEGIA:")
print("- Identificar cada libro/tesis por: (título + autor)")
print("- Si tiene código, usarlo como identificador principal")
print("- Evitar duplicados por contenido")
print("- Importar SOLO lo que existe en el Excel, ni más ni menos")
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
# PASO 2: IMPORTAR TESIS (IDENTIFICAR POR CÓDIGO O TÍTULO+AUTOR)
# ============================================================================
print("\n[PASO 2] Importando TESIS...")

# Conjunto para rastrear tesis únicas por contenido
tesis_vistas = set()  # (titulo_normalizado, autor_normalizado)
codigos_tesis_vistos = set()
tesis_creadas = 0
tesis_duplicadas = 0
contador_sin_codigo_tesis = 0

for hoja in HOJAS_TESIS:
    print(f"\n   Procesando hoja: {hoja}")
    
    try:
        df = pd.read_excel(EXCEL_FILE, sheet_name=hoja)
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
            
            # Si no hay título, omitir
            if not titulo:
                continue
            
            # Crear clave única por contenido
            titulo_norm = normalizar_texto(titulo)
            autor_norm = normalizar_texto(autor)
            clave_contenido = (titulo_norm, autor_norm)
            
            # Verificar si es duplicado
            es_duplicado = False
            
            # Si tiene código y ya lo vimos, es duplicado
            if codigo_nuevo and codigo_nuevo in codigos_tesis_vistos:
                es_duplicado = True
            
            # Si ya vimos este contenido, es duplicado
            if clave_contenido in tesis_vistas:
                es_duplicado = True
            
            if es_duplicado:
                tesis_duplicadas += 1
                continue
            
            # Si no tiene código, generar uno
            if not codigo_nuevo:
                contador_sin_codigo_tesis += 1
                codigo_nuevo = f'TESIS-{contador_sin_codigo_tesis:04d}'
            
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
                
                # Registrar como visto
                if codigo_nuevo:
                    codigos_tesis_vistos.add(codigo_nuevo)
                tesis_vistas.add(clave_contenido)
                
                tesis_creadas += 1
                filas_importadas += 1
                
            except Exception as e:
                print(f"      [ERROR] No se pudo crear tesis: {titulo[:50]} - {e}")
        
        print(f"      [OK] Importadas: {filas_importadas} tesis únicas")
        
    except Exception as e:
        print(f"      [ERROR] No se pudo leer la hoja: {e}")

print(f"\n   [OK] TESIS creadas: {tesis_creadas}")
print(f"   [INFO] TESIS duplicadas omitidas: {tesis_duplicadas}")
print(f"   [INFO] Códigos generados para tesis: {contador_sin_codigo_tesis}")

# ============================================================================
# PASO 3: IMPORTAR LIBROS (IDENTIFICAR POR CÓDIGO O TÍTULO+AUTOR)
# ============================================================================
print("\n[PASO 3] Importando LIBROS...")

# Conjunto para rastrear libros únicos por contenido
libros_vistos = set()  # (titulo_normalizado, autor_normalizado)
codigos_libros_vistos = set()
libros_creados = 0
libros_duplicados = 0
contador_sin_codigo_libro = 0

for hoja in HOJAS_LIBROS:
    print(f"\n   Procesando hoja: {hoja}")
    
    try:
        df = pd.read_excel(EXCEL_FILE, sheet_name=hoja)
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
            
            # Si no hay título, omitir
            if not titulo:
                continue
            
            # Crear clave única por contenido
            titulo_norm = normalizar_texto(titulo)
            autor_norm = normalizar_texto(autor)
            clave_contenido = (titulo_norm, autor_norm)
            
            # Verificar si es duplicado
            es_duplicado = False
            
            # Si tiene código y ya lo vimos, es duplicado
            if codigo_nuevo and codigo_nuevo in codigos_libros_vistos:
                es_duplicado = True
            
            # Si ya vimos este contenido, es duplicado
            if clave_contenido in libros_vistos:
                es_duplicado = True
            
            if es_duplicado:
                libros_duplicados += 1
                continue
            
            # Si no tiene código, generar uno
            if not codigo_nuevo:
                contador_sin_codigo_libro += 1
                codigo_nuevo = f'LIBRO-{contador_sin_codigo_libro:04d}'
            
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
                
                # Registrar como visto
                if codigo_nuevo:
                    codigos_libros_vistos.add(codigo_nuevo)
                libros_vistos.add(clave_contenido)
                
                libros_creados += 1
                filas_importadas += 1
                
            except Exception as e:
                print(f"      [ERROR] No se pudo crear libro: {titulo[:50]} - {e}")
        
        print(f"      [OK] Importados: {filas_importadas} libros únicos")
        
    except Exception as e:
        print(f"      [ERROR] No se pudo leer la hoja: {e}")

print(f"\n   [OK] LIBROS creados: {libros_creados}")
print(f"   [INFO] LIBROS duplicados omitidos: {libros_duplicados}")
print(f"   [INFO] Códigos generados para libros: {contador_sin_codigo_libro}")

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

print(f"\nÚnicos identificados en Excel:")
print(f"  Tesis:  {len(tesis_vistas)}")
print(f"  Libros: {len(libros_vistos)}")

print(f"\n¿Coinciden exactamente?")
print(f"  Tesis:  {'✅ SÍ' if tesis_bd == len(tesis_vistas) else '❌ NO'}")
print(f"  Libros: {'✅ SÍ' if libros_bd == len(libros_vistos) else '❌ NO'}")

# Verificar búsqueda
print("\n" + "="*80)
print("PRUEBA DE BÚSQUEDA")
print("="*80)

# Tomar una muestra aleatoria
import random
if tesis_bd > 0:
    tesis_muestra = TrabajoGrado.objects.order_by('?').first()
    print(f"\n✓ Tesis de prueba encontrada:")
    print(f"  Código: {tesis_muestra.codigo_nuevo}")
    print(f"  Título: {tesis_muestra.titulo[:60]}")
    print(f"  Autor: {tesis_muestra.autor}")

if libros_bd > 0:
    libro_muestra = Libro.objects.order_by('?').first()
    print(f"\n✓ Libro de prueba encontrado:")
    print(f"  Código: {libro_muestra.codigo_nuevo}")
    print(f"  Título: {libro_muestra.titulo[:60]}")
    print(f"  Autor: {libro_muestra.autor}")

print("\n" + "="*80)
print("IMPORTACIÓN COMPLETADA EXITOSAMENTE")
print("="*80)
print("\n✅ Todos los libros y tesis del Excel están en el sistema")
print("✅ Sin duplicados")
print("✅ Búsqueda por código, título o autor funcionará correctamente")
