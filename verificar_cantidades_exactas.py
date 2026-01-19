import pandas as pd
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from inventario.models import TrabajoGrado, Libro

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
    """Limpia un valor del Excel"""
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

print("="*80)
print("VERIFICACIÓN EXACTA: EXCEL vs BASE DE DATOS")
print("="*80)

# ============================================================================
# ANÁLISIS DEL EXCEL - TESIS
# ============================================================================
print("\n[EXCEL] Analizando TESIS...")

tesis_excel_unicas = set()  # (titulo_norm, autor_norm)
tesis_excel_por_hoja = {}

for hoja in HOJAS_TESIS:
    df = pd.read_excel(EXCEL_FILE, sheet_name=hoja)
    df.columns = df.columns.str.strip()
    
    count_hoja = 0
    for _, row in df.iterrows():
        titulo = limpiar_valor(row.get('TITULO'))
        autor = limpiar_valor(row.get('AUTOR'))
        
        if not titulo:
            continue
        
        titulo_norm = normalizar_texto(titulo)
        autor_norm = normalizar_texto(autor)
        clave = (titulo_norm, autor_norm)
        
        tesis_excel_unicas.add(clave)
        count_hoja += 1
    
    tesis_excel_por_hoja[hoja] = count_hoja
    print(f"  {hoja}: {count_hoja} registros con título")

print(f"\n  TOTAL filas con título: {sum(tesis_excel_por_hoja.values())}")
print(f"  TOTAL únicas (título+autor): {len(tesis_excel_unicas)}")

# ============================================================================
# ANÁLISIS DEL EXCEL - LIBROS
# ============================================================================
print("\n[EXCEL] Analizando LIBROS...")

libros_excel_unicos = set()  # (titulo_norm, autor_norm)
libros_excel_por_hoja = {}

for hoja in HOJAS_LIBROS:
    df = pd.read_excel(EXCEL_FILE, sheet_name=hoja)
    df.columns = df.columns.str.strip()
    
    count_hoja = 0
    for _, row in df.iterrows():
        titulo = limpiar_valor(row.get('TITULO'))
        autor = limpiar_valor(row.get('AUTOR'))
        
        if not titulo:
            continue
        
        titulo_norm = normalizar_texto(titulo)
        autor_norm = normalizar_texto(autor)
        clave = (titulo_norm, autor_norm)
        
        libros_excel_unicos.add(clave)
        count_hoja += 1
    
    libros_excel_por_hoja[hoja] = count_hoja
    print(f"  {hoja}: {count_hoja} registros con título")

print(f"\n  TOTAL filas con título: {sum(libros_excel_por_hoja.values())}")
print(f"  TOTAL únicos (título+autor): {len(libros_excel_unicos)}")

# ============================================================================
# ANÁLISIS BASE DE DATOS
# ============================================================================
print("\n[BASE DE DATOS] Analizando registros...")

tesis_bd = TrabajoGrado.objects.all()
libros_bd = Libro.objects.all()

tesis_bd_unicas = set()
for tesis in tesis_bd:
    titulo_norm = normalizar_texto(tesis.titulo)
    autor_norm = normalizar_texto(tesis.autor)
    tesis_bd_unicas.add((titulo_norm, autor_norm))

libros_bd_unicos = set()
for libro in libros_bd:
    titulo_norm = normalizar_texto(libro.titulo)
    autor_norm = normalizar_texto(libro.autor)
    libros_bd_unicos.add((titulo_norm, autor_norm))

print(f"  Tesis en BD: {len(tesis_bd_unicas)}")
print(f"  Libros en BD: {len(libros_bd_unicos)}")

# ============================================================================
# COMPARACIÓN
# ============================================================================
print("\n" + "="*80)
print("COMPARACIÓN EXACTA")
print("="*80)

print("\nTESIS:")
print(f"  Excel (únicos):        {len(tesis_excel_unicas)}")
print(f"  Base de Datos:         {len(tesis_bd_unicas)}")
print(f"  ¿Coinciden?            {'✅ SÍ' if len(tesis_excel_unicas) == len(tesis_bd_unicas) else '❌ NO'}")

if len(tesis_excel_unicas) != len(tesis_bd_unicas):
    diferencia = len(tesis_excel_unicas) - len(tesis_bd_unicas)
    if diferencia > 0:
        print(f"  ⚠️  FALTAN {diferencia} tesis en la BD")
    else:
        print(f"  ⚠️  SOBRAN {abs(diferencia)} tesis en la BD")

print("\nLIBROS:")
print(f"  Excel (únicos):        {len(libros_excel_unicos)}")
print(f"  Base de Datos:         {len(libros_bd_unicos)}")
print(f"  ¿Coinciden?            {'✅ SÍ' if len(libros_excel_unicos) == len(libros_bd_unicos) else '❌ NO'}")

if len(libros_excel_unicos) != len(libros_bd_unicos):
    diferencia = len(libros_excel_unicos) - len(libros_bd_unicos)
    if diferencia > 0:
        print(f"  ⚠️  FALTAN {diferencia} libros en la BD")
    else:
        print(f"  ⚠️  SOBRAN {abs(diferencia)} libros en la BD")

# ============================================================================
# VERIFICAR TESIS FALTANTES O SOBRANTES
# ============================================================================
tesis_en_excel_no_bd = tesis_excel_unicas - tesis_bd_unicas
tesis_en_bd_no_excel = tesis_bd_unicas - tesis_excel_unicas

if tesis_en_excel_no_bd:
    print(f"\n⚠️  TESIS EN EXCEL PERO NO EN BD ({len(tesis_en_excel_no_bd)}):")
    for i, (titulo, autor) in enumerate(list(tesis_en_excel_no_bd)[:5], 1):
        print(f"  {i}. {titulo[:60]} - {autor[:30]}")
    if len(tesis_en_excel_no_bd) > 5:
        print(f"  ... y {len(tesis_en_excel_no_bd) - 5} más")

if tesis_en_bd_no_excel:
    print(f"\n⚠️  TESIS EN BD PERO NO EN EXCEL ({len(tesis_en_bd_no_excel)}):")
    for i, (titulo, autor) in enumerate(list(tesis_en_bd_no_excel)[:5], 1):
        print(f"  {i}. {titulo[:60]} - {autor[:30]}")
    if len(tesis_en_bd_no_excel) > 5:
        print(f"  ... y {len(tesis_en_bd_no_excel) - 5} más")

# ============================================================================
# VERIFICAR LIBROS FALTANTES O SOBRANTES
# ============================================================================
libros_en_excel_no_bd = libros_excel_unicos - libros_bd_unicos
libros_en_bd_no_excel = libros_bd_unicos - libros_excel_unicos

if libros_en_excel_no_bd:
    print(f"\n⚠️  LIBROS EN EXCEL PERO NO EN BD ({len(libros_en_excel_no_bd)}):")
    for i, (titulo, autor) in enumerate(list(libros_en_excel_no_bd)[:5], 1):
        print(f"  {i}. {titulo[:60]} - {autor[:30]}")
    if len(libros_en_excel_no_bd) > 5:
        print(f"  ... y {len(libros_en_excel_no_bd) - 5} más")

if libros_en_bd_no_excel:
    print(f"\n⚠️  LIBROS EN BD PERO NO EN EXCEL ({len(libros_en_bd_no_excel)}):")
    for i, (titulo, autor) in enumerate(list(libros_en_bd_no_excel)[:5], 1):
        print(f"  {i}. {titulo[:60]} - {autor[:30]}")
    if len(libros_en_bd_no_excel) > 5:
        print(f"  ... y {len(libros_en_bd_no_excel) - 5} más")

# ============================================================================
# CONCLUSIÓN
# ============================================================================
print("\n" + "="*80)
print("CONCLUSIÓN")
print("="*80)

if len(tesis_excel_unicas) == len(tesis_bd_unicas) and len(libros_excel_unicos) == len(libros_bd_unicos):
    if not tesis_en_excel_no_bd and not tesis_en_bd_no_excel and not libros_en_excel_no_bd and not libros_en_bd_no_excel:
        print("\n✅ PERFECTO: Las cantidades y los datos son EXACTAMENTE IGUALES")
        print("✅ Todos los libros y tesis del Excel están en la BD")
        print("✅ No hay registros extra en la BD")
    else:
        print("\n⚠️  Las cantidades coinciden PERO hay diferencias en los datos")
        print("⚠️  Algunos registros son diferentes entre Excel y BD")
else:
    print("\n❌ LAS CANTIDADES NO COINCIDEN")
    print("❌ Hay diferencias entre el Excel y la Base de Datos")
    print("\n📝 Recomendación: Ejecutar nuevamente la importación")

print("\n" + "="*80)
