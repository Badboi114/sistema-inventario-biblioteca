import pandas as pd

excel_file = 'BASE DE EXISTENCIA DE LIBROS, PROYECTOS DE GRADO, TESIS Y TRABAJO DIRIGIDO (2).xlsx'
excel = pd.ExcelFile(excel_file)

print("="*80)
print("ANÁLISIS DEL ARCHIVO EXCEL")
print("="*80)

for sheet in excel.sheet_names:
    df = pd.read_excel(excel, sheet_name=sheet)
    print(f"\nHoja: {sheet}")
    print(f"  Filas: {len(df)}")
    print(f"  Columnas: {list(df.columns)}")
