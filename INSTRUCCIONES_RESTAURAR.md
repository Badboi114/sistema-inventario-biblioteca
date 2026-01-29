# Restaurar datos y entorno del sistema de inventario biblioteca

## 1. Requisitos previos
- Python 3.10+ y pip
- Node.js y npm
- (Opcional) Virtualenv para Python

## 2. Clonar el repositorio
```
git clone https://github.com/Badboi114/sistema-inventario-biblioteca.git
cd sistema-inventario-biblioteca
```

## 3. Instalar dependencias backend
```
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 4. Instalar dependencias frontend
```
cd frontend
npm install
cd ..
```

## 5. Restaurar la base de datos con datos reales
Coloca el archivo `respaldo_db_29ene2026.sqlite3` en la raíz del proyecto (junto a `manage.py`).

Renómbralo a `db.sqlite3`:
```
mv respaldo_db_29ene2026.sqlite3 db.sqlite3
```

## 6. Ejecutar el backend
```
source venv/bin/activate
python manage.py runserver
```

## 7. Ejecutar el frontend
En otra terminal:
```
cd frontend
npm run dev
```

## 8. Acceso
- Frontend: http://localhost:5173/
- Backend/API: http://localhost:8000/

---

**¡Listo! El sistema estará con todos los libros y tesis cargados, igual que el entorno original.**
