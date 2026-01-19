import pandas as pd
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

# Ruta al archivo Excel
EXCEL_FILE = r"C:\Users\4dm1n\OneDrive - Universidad Privada Domingo Savio\Escritorio\a\SISTEMA DE INVENTARIO DE BIBLIOTECA\BASE DE EXISTENCIA DE LIBROS, PROYECTOS DE GRADO, TESIS Y TRABAJO DIRIGIDO (2).xlsx"

print("="*80)
print("ANÁLISIS DETALLADO DEL ARCHIVO EXCEL")
print("="*80)

# Hojas de TESIS
hojas_tesis = [
    'LISTA DE PROYECTOS DE GRADO (2)',
    'Tabla7',
    'LISTA DE PROYECTOS DE GRADO'
]

# Hojas de LIBROS
hojas_libros = [
    'LISTA DE LIBROS ACADEMICOS',
    'LIBROS DE LECTURA',
    'PARA REPORTE'
]

def limpiar_valor(valor):
    """Limpia un valor del Excel"""
    if pd.isna(valor):
        return None
    valor_str = str(valor).strip()
    if valor_str.lower() in ['nan', '', 'none']:
        return None
    return valor_str

print("\n" + "="*80)
print("ANÁLISIS DE TESIS")
print("="*80)

total_filas_tesis = 0
codigos_unicos_tesis = set()
registros_tesis = []

for hoja in hojas_tesis:
    try:
        df = pd.read_excel(EXCEL_FILE, sheet_name=hoja)
        # Limpiar nombres de columnas
        df.columns = df.columns.str.strip()
        
        print(f"\n[{hoja}]")
        print(f"  Filas totales: {len(df)}")
        
        filas_hoja = 0
        for _, row in df.iterrows():
            codigo = limpiar_valor(row.get('CODIGO NUEVO'))
            titulo = limpiar_valor(row.get('TITULO'))
            autor = limpiar_valor(row.get('AUTOR'))
            
            if titulo:
                filas_hoja += 1
                total_filas_tesis += 1
                if codigo:
                    codigos_unicos_tesis.add(codigo)
                    
                registros_tesis.append({
                    'hoja': hoja,
                    'codigo': codigo or '(sin código)',
                    'titulo': titulo[:50] if titulo else '',
                    'autor': autor[:30] if autor else ''
                })
        
        print(f"  Filas con título válido: {filas_hoja}")
        
    except Exception as e:
        print(f"  ERROR: {e}")

print(f"\nRESUMEN TESIS:")
print(f"  Total filas con título: {total_filas_tesis}")
print(f"  Códigos únicos: {len(codigos_unicos_tesis)}")

print("\n" + "="*80)
print("ANÁLISIS DE LIBROS")
print("="*80)

total_filas_libros = 0
codigos_unicos_libros = set()
libros_unicos_contenido = set()
registros_libros = []

for hoja in hojas_libros:
    try:
        df = pd.read_excel(EXCEL_FILE, sheet_name=hoja)
        # Limpiar nombres de columnas
        df.columns = df.columns.str.strip()
        
        print(f"\n[{hoja}]")
        print(f"  Filas totales: {len(df)}")
        
        filas_hoja = 0
        for _, row in df.iterrows():
            codigo = limpiar_valor(row.get('CODIGO NUEVO'))
            titulo = limpiar_valor(row.get('TITULO'))
            autor = limpiar_valor(row.get('AUTOR'))
            editorial = limpiar_valor(row.get('EDITORIAL'))
            anio = limpiar_valor(row.get('AÑO'))
            
            if titulo:
                filas_hoja += 1
                total_filas_libros += 1
                
                # Códigos únicos
                if codigo:
                    codigos_unicos_libros.add(codigo)
                
                # Contenido único (título, autor, editorial, año)
                clave_contenido = (titulo, autor, editorial, anio)
                libros_unicos_contenido.add(clave_contenido)
                    
                registros_libros.append({
                    'hoja': hoja,
                    'codigo': codigo or '(sin código)',
                    'titulo': titulo[:50] if titulo else '',
                    'autor': autor[:30] if autor else ''
                })
        
        print(f"  Filas con título válido: {filas_hoja}")
        
    except Exception as e:
        print(f"  ERROR: {e}")

print(f"\nRESUMEN LIBROS:")
print(f"  Total filas con título: {total_filas_libros}")
print(f"  Códigos únicos: {len(codigos_unicos_libros)}")
print(f"  Únicos por contenido (título+autor+editorial+año): {len(libros_unicos_contenido)}")

print("\n" + "="*80)
print("ANÁLISIS DETALLADO: LIBROS CON Y SIN CÓDIGO")
print("="*80)

libros_con_codigo = []
libros_sin_codigo = []
libros_sin_codigo_unicos = set()

for hoja in hojas_libros:
    try:
        df = pd.read_excel(EXCEL_FILE, sheet_name=hoja)
        df.columns = df.columns.str.strip()
        
        for _, row in df.iterrows():
            codigo = limpiar_valor(row.get('CODIGO NUEVO'))
            titulo = limpiar_valor(row.get('TITULO'))
            autor = limpiar_valor(row.get('AUTOR'))
            editorial = limpiar_valor(row.get('EDITORIAL'))
            anio = limpiar_valor(row.get('AÑO'))
            
            if titulo:
                clave_contenido = (titulo, autor, editorial, anio)
                
                if codigo:
                    libros_con_codigo.append(clave_contenido)
                else:
                    libros_sin_codigo.append(clave_contenido)
                    libros_sin_codigo_unicos.add(clave_contenido)
        
    except Exception as e:
        print(f"  ERROR en {hoja}: {e}")

print(f"\nLibros CON código:")
print(f"  Total registros: {len(libros_con_codigo)}")
print(f"  Únicos: {len(set(libros_con_codigo))}")

print(f"\nLibros SIN código:")
print(f"  Total registros: {len(libros_sin_codigo)}")
print(f"  Únicos: {len(libros_sin_codigo_unicos)}")

# Verificar cuántos libros sin código YA EXISTEN con código
libros_con_codigo_set = set(libros_con_codigo)
sin_codigo_pero_existe_con_codigo = 0
sin_codigo_realmente_nuevos = 0

for libro_sin_cod in libros_sin_codigo_unicos:
    if libro_sin_cod in libros_con_codigo_set:
        sin_codigo_pero_existe_con_codigo += 1
    else:
        sin_codigo_realmente_nuevos += 1

print(f"\nDe los libros SIN código:")
print(f"  Ya existe la misma versión CON código: {sin_codigo_pero_existe_con_codigo}")
print(f"  Son realmente nuevos (no tienen versión con código): {sin_codigo_realmente_nuevos}")

print("\n" + "="*80)
print("CÁLCULO FINAL: ¿CUÁNTOS LIBROS ÚNICOS HAY?")
print("="*80)

# Opción 1: Solo códigos únicos
opcion1 = len(codigos_unicos_libros)
print(f"\nOpción 1 - Solo códigos únicos: {opcion1}")

# Opción 2: Códigos únicos + libros sin código que no tienen versión con código
opcion2 = len(codigos_unicos_libros) + sin_codigo_realmente_nuevos
print(f"Opción 2 - Códigos + libros nuevos sin código: {opcion2}")

# Opción 3: Todos los únicos por contenido
opcion3 = len(libros_unicos_contenido)
print(f"Opción 3 - Todos únicos por contenido: {opcion3}")

print("\n" + "="*80)
print("RESUMEN FINAL")
print("="*80)
print(f"\nTESIS:")
print(f"  Total filas: {total_filas_tesis}")
print(f"  Códigos únicos: {len(codigos_unicos_tesis)}")

print(f"\nLIBROS:")
print(f"  Total filas: {total_filas_libros}")
print(f"  Códigos únicos: {len(codigos_unicos_libros)}")
print(f"  Únicos por contenido: {len(libros_unicos_contenido)}")
print(f"  IMPORTADOS (códigos + nuevos sin código): {opcion2}")

print("\n" + "="*80)
print("COMPARACIÓN CON BASE DE DATOS")
print("="*80)

from inventario.models import TrabajoGrado, Libro

tesis_bd = TrabajoGrado.objects.count()
libros_bd = Libro.objects.count()

print(f"\nBase de Datos:")
print(f"  Tesis:  {tesis_bd}")
print(f"  Libros: {libros_bd}")

print(f"\nExcel (códigos únicos):")
print(f"  Tesis:  {len(codigos_unicos_tesis)}")
print(f"  Libros: {len(codigos_unicos_libros)}")

print(f"\nExcel (importados con estrategia contenido):")
print(f"  Tesis:  {len(codigos_unicos_tesis)}")
print(f"  Libros: {opcion2} (códigos + libros nuevos sin código)")

print(f"\n¿Coinciden?")
print(f"  Tesis:  {'✅ SÍ' if tesis_bd == len(codigos_unicos_tesis) else '❌ NO'}")
print(f"  Libros: {'✅ SÍ' if libros_bd == opcion2 else '❌ NO'}")

print("\n" + "="*80)
