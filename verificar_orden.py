import pandas as pd
from inventario.models import Libro

# Leer Excel
df = pd.read_excel('BASE DE EXISTENCIA DE LIBROS, PROYECTOS DE GRADO, TESIS Y TRABAJO DIRIGIDO.xlsx', 
                   sheet_name='LISTA DE LIBROS ACADEMICOS')
df.columns = df.columns.str.strip().str.upper()

# Obtener primer libro con título del Excel
for idx, row in df.iterrows():
    titulo_excel = str(row.get('TITULO', '')).strip()
    if titulo_excel and titulo_excel.lower() != 'nan':
        print(f"📖 PRIMER LIBRO EN EXCEL (fila {idx}):")
        print(f"   Título: {titulo_excel[:60]}")
        break

# Obtener primer libro del sistema
primer_libro_sistema = Libro.objects.first()
print(f"\n📚 PRIMER LIBRO EN SISTEMA:")
print(f"   Título: {primer_libro_sistema.titulo[:60]}")
print(f"   Orden: {primer_libro_sistema.orden_importacion}")

# Comparar
if titulo_excel[:50] == primer_libro_sistema.titulo[:50]:
    print("\n✅ ¡COINCIDEN! El orden es correcto.")
else:
    print("\n❌ NO COINCIDEN. Hay un problema de orden.")
