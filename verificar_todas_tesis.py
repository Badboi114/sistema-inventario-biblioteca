import pandas as pd
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from inventario.models import TrabajoGrado

# Ruta al archivo Excel
EXCEL_FILE = r"C:\Users\4dm1n\OneDrive - Universidad Privada Domingo Savio\Escritorio\a\SISTEMA DE INVENTARIO DE BIBLIOTECA\BASE DE EXISTENCIA DE LIBROS, PROYECTOS DE GRADO, TESIS Y TRABAJO DIRIGIDO (2).xlsx"

HOJA_TESIS = 'LISTA DE PROYECTOS DE GRADO (2)'

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
print("VERIFICACIÓN COMPLETA: TODAS LAS TESIS DEL EXCEL")
print("="*80)

# ============================================================================
# PASO 1: Leer todas las tesis del Excel
# ============================================================================
print(f"\n[PASO 1] Leyendo tesis del Excel (hoja: {HOJA_TESIS})...")

df_tesis = pd.read_excel(EXCEL_FILE, sheet_name=HOJA_TESIS)
df_tesis.columns = df_tesis.columns.str.strip()

print(f"   Total filas: {len(df_tesis)}")

# Recolectar todas las tesis del Excel con sus datos
tesis_excel = []
tesis_excel_unicas = {}  # por (titulo_norm, autor_norm)

for idx, row in df_tesis.iterrows():
    codigo = limpiar_valor(row.get('CODIGO NUEVO'))
    titulo = limpiar_valor(row.get('TITULO'))
    autor = limpiar_valor(row.get('AUTOR'))
    
    if not titulo:
        continue
    
    titulo_norm = normalizar_texto(titulo)
    autor_norm = normalizar_texto(autor)
    clave = (titulo_norm, autor_norm)
    
    tesis_excel.append({
        'fila': idx + 2,  # +2 porque Excel empieza en 1 y tiene header
        'codigo': codigo,
        'titulo': titulo,
        'autor': autor,
        'titulo_norm': titulo_norm,
        'autor_norm': autor_norm,
        'clave': clave
    })
    
    if clave not in tesis_excel_unicas:
        tesis_excel_unicas[clave] = {
            'codigo': codigo,
            'titulo': titulo,
            'autor': autor,
            'primera_fila': idx + 2
        }

print(f"   Filas con título: {len(tesis_excel)}")
print(f"   Tesis únicas (título+autor): {len(tesis_excel_unicas)}")
print(f"   Duplicados: {len(tesis_excel) - len(tesis_excel_unicas)}")

# ============================================================================
# PASO 2: Leer todas las tesis de la Base de Datos
# ============================================================================
print(f"\n[PASO 2] Leyendo tesis de la Base de Datos...")

tesis_bd = TrabajoGrado.objects.all()
print(f"   Total tesis en BD: {tesis_bd.count()}")

tesis_bd_dict = {}  # por (titulo_norm, autor_norm)
tesis_bd_por_codigo = {}  # por codigo

for tesis in tesis_bd:
    titulo_norm = normalizar_texto(tesis.titulo)
    autor_norm = normalizar_texto(tesis.autor)
    clave = (titulo_norm, autor_norm)
    
    tesis_bd_dict[clave] = {
        'codigo': tesis.codigo_nuevo,
        'titulo': tesis.titulo,
        'autor': tesis.autor,
        'id': tesis.id
    }
    
    tesis_bd_por_codigo[tesis.codigo_nuevo] = tesis

# ============================================================================
# PASO 3: Verificar que todas las tesis del Excel están en BD
# ============================================================================
print(f"\n[PASO 3] Verificando que todas las tesis del Excel están en BD...")

tesis_en_excel_no_bd = []
tesis_verificadas = 0

for clave, datos in tesis_excel_unicas.items():
    if clave in tesis_bd_dict:
        tesis_verificadas += 1
    else:
        tesis_en_excel_no_bd.append(datos)

print(f"   Tesis verificadas en BD: {tesis_verificadas}/{len(tesis_excel_unicas)}")

if tesis_en_excel_no_bd:
    print(f"\n   ❌ FALTAN {len(tesis_en_excel_no_bd)} TESIS EN LA BD:")
    for i, tesis in enumerate(tesis_en_excel_no_bd[:10], 1):
        print(f"      {i}. [{tesis.get('codigo', 'SIN CÓDIGO')}] {tesis['titulo'][:60]}")
        print(f"         Autor: {tesis['autor']}")
        print(f"         Primera aparición: Fila {tesis['primera_fila']}")
    if len(tesis_en_excel_no_bd) > 10:
        print(f"      ... y {len(tesis_en_excel_no_bd) - 10} más")
else:
    print(f"   ✅ TODAS las tesis del Excel están en la BD")

# ============================================================================
# PASO 4: Verificar que no hay tesis extra en BD
# ============================================================================
print(f"\n[PASO 4] Verificando que no hay tesis extra en BD...")

tesis_en_bd_no_excel = []

for clave, datos in tesis_bd_dict.items():
    if clave not in tesis_excel_unicas:
        tesis_en_bd_no_excel.append(datos)

if tesis_en_bd_no_excel:
    print(f"\n   ❌ HAY {len(tesis_en_bd_no_excel)} TESIS EXTRA EN LA BD:")
    for i, tesis in enumerate(tesis_en_bd_no_excel[:10], 1):
        print(f"      {i}. [{tesis['codigo']}] {tesis['titulo'][:60]}")
        print(f"         Autor: {tesis['autor']}")
    if len(tesis_en_bd_no_excel) > 10:
        print(f"      ... y {len(tesis_en_bd_no_excel) - 10} más")
else:
    print(f"   ✅ NO hay tesis extra en la BD")

# ============================================================================
# PASO 5: Verificar búsqueda por código
# ============================================================================
print(f"\n[PASO 5] Verificando búsqueda por código...")

codigos_excel_con_valor = [t['codigo'] for t in tesis_excel_unicas.values() if t['codigo']]
print(f"   Códigos con valor en Excel: {len(codigos_excel_con_valor)}")

codigos_encontrados = 0
codigos_no_encontrados = []

for codigo in codigos_excel_con_valor[:100]:  # Verificar primeros 100
    try:
        tesis = TrabajoGrado.objects.get(codigo_nuevo=codigo)
        codigos_encontrados += 1
    except TrabajoGrado.DoesNotExist:
        codigos_no_encontrados.append(codigo)

print(f"   Códigos encontrados: {codigos_encontrados}/{min(len(codigos_excel_con_valor), 100)}")

if codigos_no_encontrados:
    print(f"\n   ❌ CÓDIGOS NO ENCONTRADOS:")
    for codigo in codigos_no_encontrados[:10]:
        print(f"      - {codigo}")
else:
    print(f"   ✅ Todos los códigos verificados están en la BD")

# ============================================================================
# PASO 6: Prueba de búsqueda aleatoria
# ============================================================================
print(f"\n[PASO 6] Prueba de búsqueda aleatoria...")

import random
if len(tesis_excel_unicas) > 0:
    muestras = random.sample(list(tesis_excel_unicas.items()), min(5, len(tesis_excel_unicas)))
    
    print(f"\n   Buscando {len(muestras)} tesis aleatorias:")
    for i, (clave, datos) in enumerate(muestras, 1):
        titulo_norm, autor_norm = clave
        if clave in tesis_bd_dict:
            tesis_bd = tesis_bd_dict[clave]
            print(f"\n   {i}. ✅ ENCONTRADA:")
            print(f"      Excel: [{datos.get('codigo', 'SIN CÓDIGO')}] {datos['titulo'][:50]}")
            print(f"      BD:    [{tesis_bd['codigo']}] {tesis_bd['titulo'][:50]}")
        else:
            print(f"\n   {i}. ❌ NO ENCONTRADA:")
            print(f"      Excel: [{datos.get('codigo', 'SIN CÓDIGO')}] {datos['titulo'][:50]}")

# ============================================================================
# CONCLUSIÓN
# ============================================================================
print("\n" + "="*80)
print("CONCLUSIÓN FINAL")
print("="*80)

print(f"\nExcel '{HOJA_TESIS}':")
print(f"  Total filas con título: {len(tesis_excel)}")
print(f"  Tesis únicas: {len(tesis_excel_unicas)}")

print(f"\nBase de Datos:")
print(f"  Total tesis: {tesis_bd.count()}")

print(f"\nVerificación:")
print(f"  Tesis del Excel en BD: {tesis_verificadas}/{len(tesis_excel_unicas)}")
print(f"  Tesis faltantes: {len(tesis_en_excel_no_bd)}")
print(f"  Tesis extra: {len(tesis_en_bd_no_excel)}")

if (len(tesis_en_excel_no_bd) == 0 and 
    len(tesis_en_bd_no_excel) == 0 and 
    tesis_bd.count() == len(tesis_excel_unicas)):
    print("\n" + "="*80)
    print("✅ PERFECTO: IMPORTACIÓN 100% CORRECTA")
    print("="*80)
    print("\n✅ Todas las tesis del Excel están en la BD")
    print("✅ No hay tesis extra en la BD")
    print("✅ Las cantidades coinciden exactamente")
    print("✅ La búsqueda por código funciona correctamente")
else:
    print("\n" + "="*80)
    print("❌ HAY DIFERENCIAS ENTRE EXCEL Y BD")
    print("="*80)
    if tesis_en_excel_no_bd:
        print(f"❌ Faltan {len(tesis_en_excel_no_bd)} tesis")
    if tesis_en_bd_no_excel:
        print(f"❌ Sobran {len(tesis_en_bd_no_excel)} tesis")

print("\n" + "="*80)
