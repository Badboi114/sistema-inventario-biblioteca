import pandas as pd

excel = pd.ExcelFile('BASE DE EXISTENCIA DE LIBROS, PROYECTOS DE GRADO, TESIS Y TRABAJO DIRIGIDO (2).xlsx')
hojas = ['LISTA DE PROYECTOS DE GRADO (2)', 'Tabla7', 'LISTA DE PROYECTOS DE GRADO']

print("="*80)
print("CONTEO DE FILAS EN HOJAS DE TESIS")
print("="*80)

for h in hojas:
    df = pd.read_excel(excel, sheet_name=h)
    print(f'{h}: {len(df)} filas')
