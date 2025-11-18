import { useState, useEffect } from 'react';
import axios from 'axios';
import { Search, MapPin, GraduationCap, AlertCircle, User, Users, Award } from 'lucide-react';

const Tesis = () => {
  const [tesis, setTesis] = useState([]);
  const [loading, setLoading] = useState(true);
  const [busqueda, setBusqueda] = useState('');

  // Función para buscar en la API
  const fetchTesis = async (query = '') => {
    setLoading(true);
    try {
      // Django busca en título, autor, tutor y carrera
      const response = await axios.get(`http://127.0.0.1:8000/api/tesis/?search=${query}`);
      const data = response.data.results ? response.data.results : response.data;
      setTesis(data);
    } catch (error) {
      console.error("Error cargando tesis:", error);
    }
    setLoading(false);
  };

  // Cargar al inicio
  useEffect(() => {
    fetchTesis();
  }, []);

  const handleSearch = (e) => {
    e.preventDefault();
    fetchTesis(busqueda);
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
      {/* Header con Buscador */}
      <div className="flex flex-col md:flex-row justify-between items-center mb-6 gap-4">
        <h2 className="text-2xl font-bold text-gray-800 flex items-center">
          <GraduationCap className="mr-2 text-green-600" /> Proyectos de Grado y Tesis
        </h2>
        
        <form onSubmit={handleSearch} className="relative w-full md:w-96">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
          <input 
            type="text" 
            placeholder="Buscar por título, autor, tutor o carrera..." 
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
            value={busqueda}
            onChange={(e) => setBusqueda(e.target.value)}
          />
        </form>
      </div>

      {/* Estadísticas Rápidas */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs text-green-600 font-medium uppercase">Total</p>
              <p className="text-2xl font-bold text-green-700">{tesis.length}</p>
            </div>
            <GraduationCap className="w-8 h-8 text-green-500" />
          </div>
        </div>
      </div>

      {/* Tabla de Resultados */}
      {loading ? (
        <div className="text-center py-10 text-gray-500">Cargando investigaciones...</div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-gray-50 text-gray-700 text-sm uppercase border-b">
                <th className="p-4">Código</th>
                <th className="p-4">Título / Autor</th>
                <th className="p-4">Carrera</th>
                <th className="p-4">Tutor / Modalidad</th>
                <th className="p-4">Ubicación</th>
                <th className="p-4">Estado</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100 text-sm text-gray-600">
              {tesis.map((item) => (
                <tr key={item.id} className="hover:bg-green-50 transition-colors">
                  <td className="p-4 font-bold text-green-600 whitespace-nowrap">
                    {item.codigo_nuevo}
                  </td>
                  <td className="p-4">
                    <div className="font-medium text-gray-800 mb-1">{item.titulo}</div>
                    <div className="flex items-center gap-1 text-xs text-gray-500">
                      <User className="w-3 h-3" />
                      {item.autor || 'Sin autor'}
                    </div>
                  </td>
                  <td className="p-4">
                    <div className="flex items-center gap-1">
                      <Award className="w-4 h-4 text-green-500" />
                      <span className="text-xs font-medium">{item.carrera || 'No especificada'}</span>
                    </div>
                  </td>
                  <td className="p-4">
                    <div className="space-y-1">
                      <div className="flex items-center gap-1 text-xs">
                        <Users className="w-3 h-3 text-gray-400" />
                        <span>{item.tutor || 'Sin tutor'}</span>
                      </div>
                      {item.modalidad && (
                        <span className="inline-block px-2 py-0.5 bg-purple-100 text-purple-700 rounded text-xs font-semibold">
                          {item.modalidad}
                        </span>
                      )}
                    </div>
                  </td>
                  <td className="p-4">
                    <div className="flex items-center gap-1 text-xs">
                      <MapPin className="w-4 h-4 text-secondary" />
                      <span>{item.ubicacion_seccion} - {item.ubicacion_repisa}</span>
                    </div>
                  </td>
                  <td className="p-4">
                    <span className={`px-2 py-1 rounded-full text-xs font-semibold inline-flex items-center gap-1
                      ${item.estado === 'BUENO' ? 'bg-green-100 text-green-700' : 
                        item.estado === 'REGULAR' ? 'bg-yellow-100 text-yellow-700' : 
                        'bg-red-100 text-red-700'}`}>
                      {item.estado !== 'BUENO' && item.estado !== 'REGULAR' && <AlertCircle className="w-3 h-3" />}
                      {item.estado}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {tesis.length === 0 && (
            <div className="text-center py-10 text-gray-400">
              No se encontraron tesis con esa búsqueda.
            </div>
          )}
        </div>
      )}

      {/* Información adicional */}
      <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
        <p className="text-sm text-blue-800">
          <strong>Tip:</strong> Puedes buscar por título del proyecto, nombre del autor, tutor asignado o carrera específica.
        </p>
      </div>
    </div>
  );
};

export default Tesis;
