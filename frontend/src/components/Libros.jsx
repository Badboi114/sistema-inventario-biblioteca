import { useState, useEffect } from 'react';
import axios from 'axios';
import { Search, MapPin, Book, AlertCircle } from 'lucide-react';

const Libros = () => {
  const [libros, setLibros] = useState([]);
  const [loading, setLoading] = useState(true);
  const [busqueda, setBusqueda] = useState('');

  // Función para buscar en la API
  const fetchLibros = async (query = '') => {
    setLoading(true);
    try {
      // Django busca automáticamente en título, código y materia gracias a tu configuración
      const response = await axios.get(`http://127.0.0.1:8000/api/libros/?search=${query}`);
      // Maneja si la API devuelve paginación o lista directa
      const data = response.data.results ? response.data.results : response.data;
      setLibros(data);
    } catch (error) {
      console.error("Error cargando libros:", error);
    }
    setLoading(false);
  };

  // Cargar al inicio
  useEffect(() => {
    fetchLibros();
  }, []);

  const handleSearch = (e) => {
    e.preventDefault();
    fetchLibros(busqueda);
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
      {/* Header con Buscador */}
      <div className="flex flex-col md:flex-row justify-between items-center mb-6 gap-4">
        <h2 className="text-2xl font-bold text-gray-800 flex items-center">
          <Book className="mr-2 text-primary" /> Catálogo de Libros
        </h2>
        
        <form onSubmit={handleSearch} className="relative w-full md:w-96">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
          <input 
            type="text" 
            placeholder="Buscar por título, autor, materia o código..." 
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
            value={busqueda}
            onChange={(e) => setBusqueda(e.target.value)}
          />
        </form>
      </div>

      {/* Tabla de Resultados */}
      {loading ? (
        <div className="text-center py-10 text-gray-500">Cargando catálogo...</div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-gray-50 text-gray-700 text-sm uppercase border-b">
                <th className="p-4">Código</th>
                <th className="p-4">Título / Materia</th>
                <th className="p-4">Ubicación</th>
                <th className="p-4">Estado</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100 text-sm text-gray-600">
              {libros.map((libro) => (
                <tr key={libro.id} className="hover:bg-blue-50 transition-colors">
                  <td className="p-4 font-bold text-primary whitespace-nowrap">
                    {libro.codigo_nuevo}
                  </td>
                  <td className="p-4">
                    <div className="font-medium text-gray-800">{libro.titulo}</div>
                    <div className="text-xs text-gray-500 mt-1">
                      {libro.materia} • {libro.autor || 'Sin autor'}
                    </div>
                  </td>
                  <td className="p-4">
                    <div className="flex items-center gap-1">
                      <MapPin className="w-4 h-4 text-secondary" />
                      <span>{libro.ubicacion_seccion} - {libro.ubicacion_repisa}</span>
                    </div>
                  </td>
                  <td className="p-4">
                    <span className={`px-2 py-1 rounded-full text-xs font-semibold inline-flex items-center gap-1
                      ${libro.estado === 'BUENO' ? 'bg-green-100 text-green-700' : 
                        libro.estado === 'REGULAR' ? 'bg-yellow-100 text-yellow-700' : 
                        'bg-red-100 text-red-700'}`}>
                      {libro.estado !== 'BUENO' && libro.estado !== 'REGULAR' && <AlertCircle className="w-3 h-3" />}
                      {libro.estado}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {libros.length === 0 && (
            <div className="text-center py-10 text-gray-400">
              No se encontraron libros con esa búsqueda.
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default Libros;
