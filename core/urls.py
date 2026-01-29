"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from inventario.views import (
    LibroViewSet, TrabajoGradoViewSet, DashboardStatsView, 
    HistorialView, RestaurarRegistroView, SiguienteCodigoView, ListaSeccionesView,
    PerfilUsuarioView, ActivoViewSet, EstudianteViewSet, PrestamoViewSet,
    activos_prestados_publico
)
# Importamos las vistas de Token
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

# Configurar router de DRF
router = DefaultRouter()
router.register(r'libros', LibroViewSet, basename='libro')
router.register(r'tesis', TrabajoGradoViewSet, basename='trabajogrado')
router.register(r'activos', ActivoViewSet, basename='activo')
router.register(r'estudiantes', EstudianteViewSet, basename='estudiante')
router.register(r'prestamos', PrestamoViewSet, basename='prestamo')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/dashboard/', DashboardStatsView.as_view(), name='dashboard-stats'),
    path('api/prestados-publico/', activos_prestados_publico, name='prestados-publico'),
    
    # RUTAS DE LOGIN
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # RUTA DE PERFIL DE USUARIO
    path('api/perfil/', PerfilUsuarioView.as_view(), name='perfil-usuario'),
    
    # RUTAS DE HISTORIAL Y RESTAURACIÓN
    path('api/historial/', HistorialView.as_view(), name='historial'),
    path('api/restaurar/<str:modelo>/<int:history_id>/', RestaurarRegistroView.as_view(), name='restaurar'),
    
    # RUTAS DE ASISTENTE DE UBICACIÓN INTELIGENTE
    path('api/siguiente-codigo/', SiguienteCodigoView.as_view(), name='siguiente-codigo'),
    path('api/secciones-disponibles/', ListaSeccionesView.as_view(), name='secciones-disponibles'),
]
