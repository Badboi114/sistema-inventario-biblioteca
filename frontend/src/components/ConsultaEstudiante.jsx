import { useState, useEffect } from 'react';
import axios from 'axios';
import { Search } from 'lucide-react';
import FilterBar from './FilterBar';

// Utilidad para obtener ids de activos prestados
const getPrestadosIds = (prestamos) => {
  return prestamos.filter(p => p.estado === 'VIGENTE').map(p => p.activo);
};

const ConsultaEstudiante = () => {
  const [libros, setLibros] = useState([]);
  const [tesis, setTesis] = useState([]);
  const [loading, setLoading] = useState(true);
  const [busqueda, setBusqueda] = useState('');
  const [filtros, setFiltros] = useState({});
  const [tab, setTab] = useState('libros');
  const [prestadosIds, setPrestadosIds] = useState([]);

  useEffect(() => {
    fetchData();
  }, [tab, busqueda, filtros]);

  // Cargar ids de activos prestados desde endpoint público
  useEffect(() => {
    const fetchPrestados = async () => {
      try {
        const res = await axios.get('http://127.0.0.1:8000/api/prestados-publico/');
        setPrestadosIds(res.data.prestados || []);
      } catch (e) {
        setPrestadosIds([]);
      }
    };
    fetchPrestados();
  }, [tab]);

  const fetchData = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const config = { headers: { Authorization: `Bearer ${token}` } };
      if (tab === 'libros') {
        const params = { search: busqueda, ...filtros };
        const res = await axios.get('http://127.0.0.1:8000/api/libros/', { params, ...config });
        setLibros(res.data.results ? res.data.results : res.data);
      } else {
        const params = { search: busqueda, ...filtros };
        const res = await axios.get('http://127.0.0.1:8000/api/tesis/', { params, ...config });
        setTesis(res.data.results ? res.data.results : res.data);
      }
    } catch (error) {
      // eslint-disable-next-line
      console.error('Error cargando datos:', error);
    }
    setLoading(false);
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
      <div className="flex gap-4 mb-6">
        <button onClick={() => setTab('libros')} className={`px-4 py-2 rounded font-bold ${tab === 'libros' ? 'bg-blue-900 text-white' : 'bg-gray-100 text-blue-900'}`}>Libros</button>
        <button onClick={() => setTab('tesis')} className={`px-4 py-2 rounded font-bold ${tab === 'tesis' ? 'bg-blue-900 text-white' : 'bg-gray-100 text-blue-900'}`}>Tesis</button>
      </div>
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-6 gap-4">
        <form onSubmit={e => { e.preventDefault(); fetchData(); }} className="relative flex-1 md:w-80">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
          <input
            type="text"
            placeholder="Búsqueda rápida..."
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-900 focus:border-transparent"
            value={busqueda}
            onChange={e => setBusqueda(e.target.value)}
          />
        </form>
        <FilterBar type={tab} onFilterApply={setFiltros} />
      </div>
      {loading ? (
        <div className="text-center py-10 text-gray-500">Cargando {tab}...</div>
      ) : tab === 'libros' ? (
        <div className="overflow-x-auto min-h-[300px]">
          <table className="w-full text-left border-collapse">
            <thead className="bg-blue-50 text-gray-700 text-sm uppercase border-b border-blue-100 font-bold sticky top-0 z-20">
              <tr>
                <th className="p-4">Código</th>
                <th className="p-4">Título</th>
                <th className="p-4">Autor</th>
                <th className="p-4">Materia</th>
                <th className="p-4">Año</th>
                <th className="p-4">Estado</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100 text-sm text-gray-600">
              {libros.map(libro => (
                <tr key={libro.id} className={prestadosIds.includes(libro.id) ? 'bg-pink-200' : ''}>
                  <td className="p-4 font-bold text-blue-900 whitespace-nowrap">{libro.codigo_nuevo || 'S/C'}</td>
                  <td className="p-4 max-w-md">{libro.titulo}</td>
                  <td className="p-4">{libro.autor}</td>
                  <td className="p-4">{libro.materia}</td>
                  <td className="p-4">{libro.anio}</td>
                  <td className="p-4">{libro.estado}</td>
                </tr>
              ))}
            </tbody>
          </table>
          {libros.length === 0 && <div className="text-center py-10 text-gray-400">No se encontraron libros.</div>}
        </div>
      ) : (
        <div className="overflow-x-auto min-h-[300px]">
          <table className="w-full text-left border-collapse">
            <thead className="bg-blue-50 text-gray-700 text-sm uppercase border-b border-blue-100 font-bold sticky top-0 z-20">
              <tr>
                <th className="p-4">Código</th>
                <th className="p-4">Título</th>
                <th className="p-4">Autor</th>
                <th className="p-4">Modalidad</th>
                <th className="p-4">Tutor</th>
                <th className="p-4">Año</th>
                <th className="p-4">Estado</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100 text-sm text-gray-600">
              {tesis.map(t => (
                <tr key={t.id} className={prestadosIds.includes(t.id) ? 'bg-pink-200' : ''}>
                  <td className="p-4 font-bold text-blue-900 whitespace-nowrap">{t.codigo_nuevo || 'S/C'}</td>
                  <td className="p-4 max-w-md">{t.titulo}</td>
                  <td className="p-4">{t.autor}</td>
                  <td className="p-4">{t.modalidad}</td>
                  <td className="p-4">{t.tutor}</td>
                  <td className="p-4">{t.anio}</td>
                  <td className="p-4">{t.estado}</td>
                </tr>
              ))}
            </tbody>
          </table>
          {tesis.length === 0 && <div className="text-center py-10 text-gray-400">No se encontraron tesis.</div>}
        </div>
      )}
    </div>
  );
};

export default ConsultaEstudiante;
