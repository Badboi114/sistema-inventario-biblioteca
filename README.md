# Sistema de Inventario de Biblioteca

Sistema completo de gestión de inventario bibliográfico desarrollado con Django REST Framework y React + Vite para la Universidad Privada Domingo Savio (UPDS) - Cochabamba.

## 🚀 Características

- **Dashboard Estadístico**: Visualización de métricas en tiempo real (1,703 libros y 705 tesis/proyectos de grado)
- **Catálogo de Libros**: Búsqueda y filtrado por título, autor, materia y código
- **Catálogo de Tesis**: Gestión de trabajos de grado con información de tutor, carrera y modalidad
- **Panel de Administración**: Sistema completo de auditoría con django-simple-history
- **Generación de Etiquetas QR**: Exportación de códigos QR en PDF para etiquetado físico
- **API REST**: Endpoints completos para integración con otros sistemas
- **Base de datos precargada**: Incluye todos los 1,703 libros y 705 proyectos de grado ya cargados

## 🛠️ Tecnologías

### Backend
- Python 3.13+
- Django 5.2.8
- Django REST Framework 3.16.1
- django-simple-history (auditoría)
- django-cors-headers
- pandas + openpyxl (importación de datos)
- reportlab + qrcode + pillow (generación de PDF/QR)

### Frontend
- React 18
- Vite 7
- Tailwind CSS 3.4
- Axios
- Lucide React (iconos)

## 📋 Requisitos Previos

- Python 3.10 o superior
- Node.js 18 o superior
- npm

## ⚡ Inicio Rápido

> **La base de datos ya viene precargada con todos los datos (1,703 libros y 705 tesis). No necesitas importar nada.**

### 1. Clonar el repositorio
```bash
git clone https://github.com/Badboi114/sistema-inventario-biblioteca.git
cd sistema-inventario-biblioteca
```

### 2. Backend (Django)
```bash
python3 -m venv venv
source venv/bin/activate        # Linux/Mac
# venv\Scripts\activate         # Windows
pip install -r requirements.txt
python manage.py runserver
```
El backend estará en `http://127.0.0.1:8000/`

### 3. Frontend (React) — en otra terminal
```bash
cd frontend
npm install
npm run dev
```
El frontend estará en `http://localhost:5173/`

### 4. Acceder al sistema
- **Frontend**: http://localhost:5173/
- **Admin Django**: http://127.0.0.1:8000/admin/
- **Usuario**: `admin`
- **Contraseña**: `admin123`

> ¡Eso es todo! El sistema está listo para usar con todos los datos precargados.

## 📊 Datos del Sistema

Los datos provienen exclusivamente del archivo Excel: `BASE DE EXISTENCIA DE LIBROS, PROYECTOS DE GRADO, TESIS Y TRABAJO DIRIGIDO (2).xlsx`

| Sección | Cantidad | Hoja del Excel |
|---------|----------|----------------|
| Libros Académicos | 1,703 | LISTA DE LIBROS ACADEMICOS |
| Tesis/Proyectos de Grado | 705 | LISTA DE PROYECTOS DE GRADO |
| **Total** | **2,408** | |

> La base de datos (`db.sqlite3`) ya está incluida en el repositorio con todos estos datos precargados.

## 🔑 Acceso al Sistema

### Panel de Administración Django
- URL: `http://127.0.0.1:8000/admin/`
- **Usuario:** `admin`
- **Contraseña:** `admin123`

### Dashboard Principal
- URL: `http://localhost:5173/`
- Funcionalidades:
  - Dashboard con estadísticas
  - Catálogo de libros con búsqueda
  - Catálogo de tesis con búsqueda
  - Generación de etiquetas QR

## 📁 Estructura del Proyecto

```
SISTEMA-DE-INVENTARIO-DE-BIBLIOTECA/
├── core/                      # Configuración principal de Django
│   ├── settings.py
│   └── urls.py
├── inventario/               # App principal
│   ├── models.py            # Modelos (Libro, TrabajoGrado)
│   ├── views.py             # API endpoints
│   ├── serializers.py       # Serializers de DRF
│   ├── admin.py             # Panel de administración
│   └── management/
│       └── commands/
│           └── importar_data.py
├── frontend/                 # Aplicación React
│   ├── src/
│   │   ├── components/
│   │   │   ├── Libros.jsx
│   │   │   └── Tesis.jsx
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── tailwind.config.js
│   └── package.json
├── db.sqlite3               # Base de datos SQLite
└── manage.py
```

## 🌐 API Endpoints

### Estadísticas
- `GET /api/dashboard/` - Estadísticas generales del sistema

### Libros
- `GET /api/libros/` - Lista todos los libros
- `GET /api/libros/?search=query` - Búsqueda de libros
- `GET /api/libros/{id}/` - Detalle de un libro
- `POST /api/libros/` - Crear libro
- `PUT /api/libros/{id}/` - Actualizar libro
- `DELETE /api/libros/{id}/` - Eliminar libro

### Tesis
- `GET /api/tesis/` - Lista todas las tesis
- `GET /api/tesis/?search=query` - Búsqueda de tesis
- `GET /api/tesis/{id}/` - Detalle de una tesis
- `POST /api/tesis/` - Crear tesis
- `PUT /api/tesis/{id}/` - Actualizar tesis
- `DELETE /api/tesis/{id}/` - Eliminar tesis

## 🎨 Características del Frontend

- **Dashboard**: Visualización de métricas con tarjetas estadísticas
- **Navegación**: Sidebar colapsable con menú interactivo
- **Búsqueda en tiempo real**: Filtrado instantáneo en catálogos
- **Diseño responsivo**: Adaptado para escritorio y tablet
- **Estados visuales**: Colores diferenciados por estado (Bueno/Regular/Malo)
- **Ubicaciones**: Visualización de sección y repisa para cada ítem

## 🔒 Auditoría

El sistema incluye auditoría automática mediante `django-simple-history`:
- Registro de todos los cambios en libros y tesis
- Historial completo con usuario y timestamp
- Accesible desde el panel de administración

## 📄 Generación de QR

Desde el panel de administración:
1. Selecciona uno o más libros/tesis
2. Elige la acción "Imprimir etiquetas QR seleccionadas"
3. Se generará un PDF con códigos QR de 5x3cm

## 🤝 Contribución

Las contribuciones son bienvenidas. Por favor:
1. Haz fork del proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Licencia

Este proyecto fue desarrollado para la gestión de inventario bibliográfico universitario.

## 👤 Autor

Sistema desarrollado para Universidad Privada Domingo Savio

## 🙏 Agradecimientos

- Django REST Framework por la API robusta
- React + Vite por el frontend moderno
- Tailwind CSS por el diseño elegante
