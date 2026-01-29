import { useState, useEffect } from 'react';
import axios from 'axios';
import { LayoutDashboard, BookOpen, GraduationCap, AlertCircle, Menu, LogOut, History, User, Clock, Users } from 'lucide-react';
import Libros from './components/Libros';
import Tesis from './components/Tesis';
import Historial from './components/Historial';
import Login from './components/Login';
import PerfilModal from './components/PerfilModal';
import Prestamos from './components/Prestamos';
import Estudiantes from './components/Estudiantes';
import ConsultaEstudiante from './components/ConsultaEstudiante';

function App() {
  // --- ESTADOS ---
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [tokenChecked, setTokenChecked] = useState(false);
  const [stats, setStats] = useState({ ultimos_agregados: [] });
  const [loading, setLoading] = useState(true);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [currentView, setCurrentView] = useState('dashboard');
  const [perfilOpen, setPerfilOpen] = useState(false);

  // --- EFECTOS ---

  // 1. Verificar sesión al cargar la página
  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      setIsAuthenticated(true);
    }
    setTokenChecked(true);
  }, []);

  // 2. Cargar estadísticas cuando se entra al Dashboard
  useEffect(() => {
    if (isAuthenticated && currentView === 'dashboard') {
      const fetchStats = async () => {
        try {
          const response = await axios.get('http://127.0.0.1:8000/api/dashboard/');
          setStats(response.data);
          setLoading(false);
        } catch (err) {
          console.error("Error cargando stats:", err);
          if (err.response && err.response.status === 401) {
             handleLogout(); // Si el token venció, salir
          }
          setLoading(false);
        }
      };
      fetchStats();
    }
  }, [isAuthenticated, currentView]);

  // --- FUNCIONES ---

  const handleLogout = () => {
    localStorage.removeItem('token');
    delete axios.defaults.headers.common['Authorization'];
    setIsAuthenticated(false);
    setCurrentView('dashboard');
  };

  const handleGoToPrestamos = () => {
    setCurrentView('prestamos');
  };

  // --- RENDERIZADO ---

  // Esperar a verificar token antes de mostrar nada
  if (!tokenChecked) return null;

  // Si no está logueado, mostrar Login
  if (!isAuthenticated) {
    return <Login onLogin={() => setIsAuthenticated(true)} />;
  }

  // Interfaz Principal
  return (
    <div className="min-h-screen flex bg-light">
      {/* Sidebar */}
      <aside className={`${sidebarOpen ? 'w-64' : 'w-20'} bg-dark text-white transition-all duration-300 flex flex-col fixed h-full z-10 shadow-xl`}>
        <div className="h-16 flex items-center justify-center border-b border-gray-700 font-bold tracking-wider bg-blue-900">
            {sidebarOpen ? 'BIBLIOTECA' : <BookOpen />}
        </div>
        
        <nav className="flex-1 py-6 px-3 space-y-2">
          <a
            href="/consulta"
            target="_blank"
            rel="noopener noreferrer"
            className="w-full flex items-center p-3 rounded-lg transition-colors text-gray-400 hover:bg-gray-800"
            style={{ textDecoration: 'none' }}
          >
            <BookOpen className="w-5 h-5" />
            {sidebarOpen && <span className="ml-3 font-medium">Consulta Estudiante</span>}
          </a>
          <button 
            onClick={() => setCurrentView('dashboard')}
            className={`w-full flex items-center p-3 rounded-lg transition-colors ${currentView === 'dashboard' ? 'bg-primary text-white shadow-lg' : 'text-gray-400 hover:bg-gray-800'}`}
          >
            <LayoutDashboard className="w-5 h-5" />
            {sidebarOpen && <span className="ml-3 font-medium">Dashboard</span>}
          </button>

          <button 
            onClick={() => setCurrentView('libros')}
            className={`w-full flex items-center p-3 rounded-lg transition-colors ${currentView === 'libros' ? 'bg-primary text-white shadow-lg' : 'text-gray-400 hover:bg-gray-800'}`}
          >
            <BookOpen className="w-5 h-5" />
            {sidebarOpen && <span className="ml-3 font-medium">Libros</span>}
          </button>
          
          <button 
            onClick={() => setCurrentView('tesis')}
            className={`w-full flex items-center p-3 rounded-lg transition-colors ${currentView === 'tesis' ? 'bg-primary text-white shadow-lg' : 'text-gray-400 hover:bg-gray-800'}`}
          >
            <GraduationCap className="w-5 h-5" />
            {sidebarOpen && <span className="ml-3 font-medium">Tesis</span>}
          </button>

          <button 
            onClick={() => setCurrentView('prestamos')}
            className={`w-full flex items-center p-3 rounded-lg transition-colors ${currentView === 'prestamos' ? 'bg-primary text-white shadow-lg' : 'text-gray-400 hover:bg-gray-800'}`}
          >
            <Clock className="w-5 h-5" />
            {sidebarOpen && <span className="ml-3 font-medium">Préstamos</span>}
          </button>

          <button 
            onClick={() => setCurrentView('estudiantes')}
            className={`w-full flex items-center p-3 rounded-lg transition-colors ${currentView === 'estudiantes' ? 'bg-primary text-white shadow-lg' : 'text-gray-400 hover:bg-gray-800'}`}
          >
            <Users className="w-5 h-5" />
            {sidebarOpen && <span className="ml-3 font-medium">Estudiantes</span>}
          </button>

          <button 
            onClick={() => setCurrentView('historial')}
            className={`w-full flex items-center p-3 rounded-lg transition-colors ${currentView === 'historial' ? 'bg-primary text-white shadow-lg' : 'text-gray-400 hover:bg-gray-800'}`}
          >
            <History className="w-5 h-5" />
            {sidebarOpen && <span className="ml-3 font-medium">Auditoría</span>}
          </button>
        </nav>

        {/* Footer Sidebar con Perfil y Logout */}
        <div className="p-4 border-t border-gray-700 bg-gray-900 space-y-2">
            {/* Botón Mi Perfil */}
            <button 
                onClick={() => setPerfilOpen(true)}
                className="w-full flex items-center justify-center p-2 text-blue-300 hover:bg-blue-900/50 rounded-lg transition-colors"
            >
                <User className="w-5 h-5" />
                {sidebarOpen && <span className="ml-3 font-medium">Mi Perfil</span>}
            </button>
            
            {/* Botón Cerrar Sesión */}
            <button 
                onClick={handleLogout}
                className="w-full flex items-center justify-center p-2 text-red-400 hover:bg-red-900/30 rounded-lg transition-colors"
            >
                <LogOut className="w-5 h-5" />
                {sidebarOpen && <span className="ml-3 font-medium">Cerrar Sesión</span>}
            </button>
        </div>
      </aside>

      {/* Contenido Principal */}
      <main className={`flex-1 ${sidebarOpen ? 'ml-64' : 'ml-20'} transition-all duration-300 p-8`}>
        <header className="flex justify-between items-center mb-8 bg-white p-4 rounded-xl shadow-sm">
            <div className="flex items-center">
                <button onClick={() => setSidebarOpen(!sidebarOpen)} className="p-2 hover:bg-gray-100 rounded-lg mr-4 text-gray-600">
                    <Menu className="w-6 h-6" />
                </button>
                <h1 className="text-2xl font-bold text-gray-800">
                  {currentView === 'dashboard' && 'Panel de Control'}
                  {currentView === 'libros' && 'Catálogo de Libros'}
                  {currentView === 'tesis' && 'Proyectos de Grado'}
                  {currentView === 'estudiantes' && 'Registro de Estudiantes'}
                  {currentView === 'prestamos' && 'Gestión de Préstamos'}
                  {currentView === 'historial' && 'Auditoría del Sistema'}
                </h1>
            </div>
            <div className="flex items-center gap-3">
                <div className="text-right hidden sm:block">
                    <p className="text-sm font-bold text-gray-800">Administrador</p>
                    <p className="text-xs text-blue-900 font-medium">● Sesión Activa</p>
                </div>
                <div className="w-10 h-10 rounded-full bg-primary flex items-center justify-center text-white font-bold shadow-md">
                    A
                </div>
            </div>
        </header>

        {/* VISTA: DASHBOARD */}
        {currentView === 'dashboard' && (
          <>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
              <div className="bg-white p-6 rounded-xl shadow-sm border-l-4 border-blue-600 flex justify-between items-center">
                  <div>
                      <p className="text-gray-500 text-sm font-medium">Libros Académicos</p>
                      <h3 className="text-3xl font-bold text-gray-800">{stats?.total_libros || '0'}</h3>
                  </div>
                  <div className="p-3 bg-blue-50 rounded-lg text-blue-600"><BookOpen /></div>
              </div>

              <div className="bg-white p-6 rounded-xl shadow-sm border-l-4 border-blue-900 flex justify-between items-center">
                  <div>
                      <p className="text-gray-500 text-sm font-medium">Proyectos y Tesis</p>
                      <h3 className="text-3xl font-bold text-gray-800">{stats?.total_tesis || '0'}</h3>
                  </div>
                  <div className="p-3 bg-blue-50 rounded-lg text-blue-900"><GraduationCap /></div>
              </div>

              <div className="bg-white p-6 rounded-xl shadow-sm border-l-4 border-red-500 flex justify-between items-center">
                  <div>
                      <p className="text-gray-500 text-sm font-medium">Requieren Atención</p>
                      <h3 className="text-3xl font-bold text-gray-800">{stats?.requieren_atencion || '0'}</h3>
                  </div>
                  <div className="p-3 bg-red-50 rounded-lg text-red-600"><AlertCircle /></div>
              </div>
            </div>

            <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
               <h3 className="font-bold text-gray-700 mb-4 text-lg">Últimos Ingresos al Sistema</h3>
               <div className="overflow-x-auto">
                <table className="w-full text-left text-sm text-gray-600">
                    <thead className="bg-gray-50 text-gray-700 font-semibold uppercase">
                        <tr>
                            <th className="px-4 py-3">Código</th>
                            <th className="px-4 py-3">Título</th>
                            <th className="px-4 py-3">Estado</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-100">
                        {Array.isArray(stats?.ultimos_agregados) && stats.ultimos_agregados.length > 0 ? (
                            stats.ultimos_agregados.map((item, index) => (
                            <tr key={index} className="hover:bg-gray-50">
                                <td className="px-4 py-3 font-medium text-primary">{item.codigo_nuevo}</td>
                                <td className="px-4 py-3">{item.titulo ? item.titulo.substring(0, 60) : "Sin título"}...</td>
                                <td className="px-4 py-3">
                                    <span className={`px-2 py-1 rounded-full text-xs font-semibold 
                                        ${item.estado === 'BUENO' ? 'bg-blue-100 text-blue-900' : 
                                          item.estado === 'REGULAR' ? 'bg-yellow-100 text-yellow-700' : 'bg-red-100 text-red-700'}`}>
                                        {item.estado}
                                    </span>
                                </td>
                            </tr>
                            ))
                        ) : (
                            <tr><td colSpan="3" className="px-4 py-6 text-center text-gray-500">Cargando datos recientes...</td></tr>
                        )}
                    </tbody>
                </table>
               </div>
            </div>
          </>
        )}

        {/* VISTA: LIBROS */}
        {currentView === 'libros' && <Libros onNavigateToPrestamos={handleGoToPrestamos} />}

        {/* VISTA: TESIS */}
        {currentView === 'tesis' && <Tesis onNavigateToPrestamos={handleGoToPrestamos} />}

        {/* VISTA: CONSULTA SOLO LECTURA ESTUDIANTE */}
        {currentView === 'consulta' && <ConsultaEstudiante />}

        {/* VISTA: PRÉSTAMOS */}
        {currentView === 'prestamos' && <Prestamos />}

        {/* VISTA: ESTUDIANTES */}
        {currentView === 'estudiantes' && <Estudiantes />}

        {/* VISTA: HISTORIAL */}
        {currentView === 'historial' && <Historial />}
      </main>

      {/* MODAL DE PERFIL */}
      <PerfilModal 
        isOpen={perfilOpen} 
        onClose={() => setPerfilOpen(false)} 
        onLogout={handleLogout} 
      />
    </div>
  );
}

export default App;

