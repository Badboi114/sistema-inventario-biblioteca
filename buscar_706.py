import pandas as pd

excel_file = 'BASE DE EXISTENCIA DE LIBROS, PROYECTOS DE GRADO, TESIS Y TRABAJO DIRIGIDO (2).xlsx'

print("="*80)
print("ANÁLISIS DETALLADO DE TESIS - BUSCANDO 706 REGISTROS")
print("="*80)

# Analizar cada hoja
hojas = ['LISTA DE PROYECTOS DE GRADO (2)', 'Tabla7', 'LISTA DE PROYECTOS DE GRADO']

for nombre_hoja in hojas:
    print(f"\n{'='*80}")
    print(f"HOJA: {nombre_hoja}")
    print(f"{'='*80}")
    
    df = pd.read_excel(excel_file, sheet_name=nombre_hoja)
    df.columns = df.columns.str.strip().str.upper()
    
    print(f"Total de filas: {len(df)}")
    
    # Contar títulos válidos
    titulos_validos = df['TITULO'].notna() & (df['TITULO'] != '')
    print(f"Filas con título: {titulos_validos.sum()}")
    
    # Buscar columna de código
    codigo_col = None
    for col in ['CODIGO NUEVO', 'CODIGO NUEVO ']:
        if col in df.columns:
            codigo_col = col
            break
    
    if codigo_col:
        # Contar códigos únicos
        codigos_no_vacios = df[codigo_col].notna() & (df[codigo_col] != '')
        print(f"Filas con código: {codigos_no_vacios.sum()}")
        
        # Ver códigos únicos
        codigos_unicos = df[df[codigo_col].notna()][codigo_col].nunique()
        print(f"Códigos únicos: {codigos_unicos}")
        
        # Ver duplicados
        duplicados = df[df[codigo_col].notna()][codigo_col].duplicated().sum()
        print(f"Códigos duplicados: {duplicados}")
        
        # Contar por modalidad
        if 'MODALIDAD' in df.columns:
            print(f"\nPor modalidad:")
            modalidades = df['MODALIDAD'].value_counts()
            for mod, count in modalidades.items():
                print(f"  {mod}: {count}")

print("\n" + "="*80)
print("RECOMENDACIÓN")
print("="*80)

# Intentar encontrar la combinación correcta
df_grado2 = pd.read_excel(excel_file, sheet_name='LISTA DE PROYECTOS DE GRADO (2)')
df_grado2.columns = df_grado2.columns.str.strip().str.upper()

# Verificar si quitando duplicados llegamos a 706
for col in ['CODIGO NUEVO', 'CODIGO NUEVO ']:
    if col in df_grado2.columns:
        unicos = df_grado2[df_grado2[col].notna()].drop_duplicates(subset=[col])
        print(f"Sin duplicados de código en 'LISTA DE PROYECTOS DE GRADO (2)': {len(unicos)}")
        break

# Verificar LISTA DE PROYECTOS DE GRADO
df_grado = pd.read_excel(excel_file, sheet_name='LISTA DE PROYECTOS DE GRADO')
df_grado.columns = df_grado.columns.str.strip().str.upper()

for col in ['CODIGO NUEVO', 'CODIGO NUEVO ']:
    if col in df_grado.columns:
        unicos = df_grado[df_grado[col].notna()].drop_duplicates(subset=[col])
        print(f"Sin duplicados de código en 'LISTA DE PROYECTOS DE GRADO': {len(unicos)}")
        
        # Ver si llegamos a 706
        con_titulo = df_grado[df_grado['TITULO'].notna()]
        print(f"Con título en 'LISTA DE PROYECTOS DE GRADO': {len(con_titulo)}")
        break
