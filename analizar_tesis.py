import pandas as pd

df = pd.read_excel('BASE DE EXISTENCIA DE LIBROS, PROYECTOS DE GRADO, TESIS Y TRABAJO DIRIGIDO.xlsx', 
                   sheet_name='LISTA DE PROYECTOS DE GRADO')
df.columns = df.columns.str.strip().str.upper()
df = df.fillna('')

# Buscar columna N°
n_col = df.get('N°', df.get('Nº', pd.Series()))

validos = 0
max_n = 0

for idx, val in enumerate(n_col):
    val_str = str(val).strip()
    if val_str and val_str.lower() != 'nan':
        try:
            n = int(float(val_str))
            if 1 <= n <= 599:
                validos += 1
            if n > max_n:
                max_n = n
        except:
            pass

print(f'Total filas con N° válido (1-599): {validos}')
print(f'Máximo N° encontrado: {max_n}')
print(f'Total filas en Excel: {len(df)}')
