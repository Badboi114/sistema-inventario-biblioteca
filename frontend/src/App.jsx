import { useState, useEffect } from 'react';
import axios from 'axios';
import { LayoutDashboard, BookOpen, GraduationCap, AlertCircle, Menu, Search } from 'lucide-react';
import Libros from './components/Libros';
import Tesis from './components/Tesis';

function App() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [currentView, setCurrentView] = useState('dashboard'); // Controla qué pantalla vemos

  // Conexión a la API - solo cargar stats si estamos en dashboard
  useEffect(() => {
    if (currentView === 'dashboard') {
      const fetchStats = async () => {
        setLoading(true);
        try {
          const response = await axios.get('http://127.0.0.1:8000/api/dashboard/');
          setStats(response.data);
          setLoading(false);
        } catch (err) {
          console.error("Error conectando al backend:", err);
          setError("No se pudo conectar al sistema. Verifica que el servidor Django esté activo.");
          setLoading(false);
        }
      };
      fetchStats();
    }
  }, [currentView]);

  // Componente de Tarjeta de Estadística
  const StatCard = ({ title, value, icon: Icon, colorClass, subtext }) => (
    <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 flex items-start justify-between hover:shadow-md transition-shadow">
      <div>
        <p className="text-sm font-medium text-gray-500 mb-1">{title}</p>
        <h3 className="text-3xl font-bold text-gray-800">{value}</h3>
        {subtext && <p className="text-xs text-gray-400 mt-2">{subtext}</p>}
      </div>
      <div className={`p-3 rounded-lg ${colorClass} bg-opacity-10`}>
        <Icon className={`w-6 h-6 ${colorClass.replace('bg-', 'text-')}`} />
      </div>
    </div>
  );

  if (loading) return (
    <div className="min-h-screen flex items-center justify-center bg-light">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      <span className="ml-3 text-gray-600 font-medium">Cargando Sistema Bibliotecario...</span>
    </div>
  );

  if (error) return (
    <div className="min-h-screen flex items-center justify-center bg-red-50">
      <div className="text-center p-8 bg-white rounded-lg shadow-lg max-w-md">
        <AlertCircle className="w-16 h-16 text-danger mx-auto mb-4" />
        <h2 className="text-xl font-bold text-gray-800 mb-2">Error de Conexión</h2>
        <p className="text-gray-600">{error}</p>
        <button 
          onClick={() => window.location.reload()}
          className="mt-6 px-4 py-2 bg-primary text-white rounded-lg hover:bg-blue-800 transition-colors"
        >
          Reintentar
        </button>
      </div>
    </div>
  );

  // Calcular libros que requieren atención
  const librosAtencion = (stats?.libros_por_estado?.MALO || 0) + (stats?.libros_por_estado?.['EN REPARACION'] || 0);
  
  // Obtener últimos libros agregados (mezclar libros y tesis)
  const ultimosItems = [...(stats?.ultimos_agregados?.libros || []), ...(stats?.ultimos_agregados?.tesis || [])]
    .sort((a, b) => new Date(b.fecha_creacion) - new Date(a.fecha_creacion))
    .slice(0, 5);

  return (
    <div className="min-h-screen flex bg-light">
      {/* Sidebar */}
      <aside className={`${sidebarOpen ? 'w-64' : 'w-20'} bg-dark text-white transition-all duration-300 flex flex-col fixed h-full z-10`}>
        <div className="h-16 flex items-center justify-center border-b border-gray-700">
            {sidebarOpen ? <span className="text-xl font-bold tracking-wider">BIBLIOTECA</span> : <BookOpen />}
        </div>
        
        <nav className="flex-1 py-6 space-y-2 px-3">
          <button 
            onClick={() => setCurrentView('dashboard')}
            className={`w-full flex items-center p-3 rounded-lg transition-colors ${currentView === 'dashboard' ? 'bg-primary text-white shadow-md' : 'text-gray-400 hover:bg-gray-800 hover:text-white'}`}
          >
            <LayoutDashboard className="w-5 h-5" />
            {sidebarOpen && <span className="ml-3 font-medium">Dashboard</span>}
          </button>
          
          <button 
            onClick={() => setCurrentView('libros')}
            className={`w-full flex items-center p-3 rounded-lg transition-colors ${currentView === 'libros' ? 'bg-primary text-white shadow-md' : 'text-gray-400 hover:bg-gray-800 hover:text-white'}`}
          >
            <BookOpen className="w-5 h-5" />
            {sidebarOpen && <span className="ml-3 font-medium">Libros</span>}
          </button>
          
          <button 
            onClick={() => setCurrentView('tesis')}
            className={`w-full flex items-center p-3 rounded-lg transition-colors ${currentView === 'tesis' ? 'bg-primary text-white shadow-md' : 'text-gray-400 hover:bg-gray-800 hover:text-white'}`}
          >
            <GraduationCap className="w-5 h-5" />
            {sidebarOpen && <span className="ml-3 font-medium">Tesis</span>}
          </button>
        </nav>

        <div className="p-4 border-t border-gray-700">
            <div className="flex items-center">
                <div className="w-8 h-8 rounded-full bg-secondary flex items-center justify-center text-dark font-bold">
                    A
                </div>
                {sidebarOpen && (
                    <div className="ml-3">
                        <p className="text-sm font-medium">Administrador</p>
                        <p className="text-xs text-gray-400">En línea</p>
                    </div>
                )}
            </div>
        </div>
      </aside>

      {/* Contenido Principal */}
      <main className={`flex-1 ${sidebarOpen ? 'ml-64' : 'ml-20'} transition-all duration-300 p-8`}>
        {/* Header */}
        <header className="flex justify-between items-center mb-8">
            <div className="flex items-center">
                <button onClick={() => setSidebarOpen(!sidebarOpen)} className="p-2 hover:bg-gray-200 rounded-lg text-gray-600 mr-4">
                    <Menu className="w-6 h-6" />
                </button>
                <h1 className="text-2xl font-bold text-gray-800">
                  {currentView === 'dashboard' ? 'Panel de Control' : 'Gestión de Inventario'}
                </h1>
            </div>
        </header>

        {/* VISTA: DASHBOARD */}
        {currentView === 'dashboard' && !loading && !error && (
          <>
            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <StatCard 
            title="Total Libros Académicos" 
            value={stats?.total_libros || 0} 
            icon={BookOpen} 
            colorClass="text-blue-600 bg-blue-600"
            subtext="Registrados en sistema"
          />
          <StatCard 
            title="Proyectos y Tesis" 
            value={stats?.total_tesis || 0} 
            icon={GraduationCap} 
            colorClass="text-green-600 bg-green-600"
            subtext="Investigaciones almacenadas"
          />
          <StatCard 
            title="Requieren Atención" 
            value={librosAtencion} 
            icon={AlertCircle} 
            colorClass="text-red-600 bg-red-600"
            subtext="Estado Malo o En Reparación"
          />
        </div>

        {/* Sección de Últimos Agregados */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
            <h2 className="text-lg font-bold text-gray-800 mb-4">Actividad Reciente</h2>
            <div className="overflow-x-auto">
                <table className="w-full text-left text-sm text-gray-600">
                    <thead className="bg-gray-50 text-gray-700 font-semibold uppercase text-xs">
                        <tr>
                            <th className="px-4 py-3">Código</th>
                            <th className="px-4 py-3">Título</th>
                            <th className="px-4 py-3">Estado</th>
                            <th className="px-4 py-3">Fecha</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-100">
                        {ultimosItems.map((item, index) => (
                            <tr key={index} className="hover:bg-gray-50">
                                <td className="px-4 py-3 font-medium text-primary">{item.codigo_nuevo}</td>
                                <td className="px-4 py-3">{item.titulo?.substring(0, 60)}{item.titulo?.length > 60 ? '...' : ''}</td>
                                <td className="px-4 py-3">
                                    <span className={`px-2 py-1 rounded-full text-xs font-semibold 
                                        ${item.estado === 'BUENO' ? 'bg-green-100 text-green-700' : 
                                          item.estado === 'REGULAR' ? 'bg-yellow-100 text-yellow-700' : 'bg-red-100 text-red-700'}`}>
                                        {item.estado}
                                    </span>
                                </td>
                                <td className="px-4 py-3">{new Date(item.fecha_creacion).toLocaleDateString('es-BO')}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
          </>
        )}

        {/* VISTA: LIBROS */}
        {currentView === 'libros' && <Libros />}

        {/* VISTA: TESIS */}
        {currentView === 'tesis' && <Tesis />}
      </main>
    </div>
  );
}

export default App;

