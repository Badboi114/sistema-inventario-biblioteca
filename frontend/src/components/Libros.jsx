import { useState, useEffect } from 'react';
import axios from 'axios';
import { Search, MapPin, Book, AlertCircle, Trash2, Edit, Plus } from 'lucide-react';
import { Menu, Item, useContextMenu } from 'react-contexify';
import 'react-contexify/dist/ReactContexify.css';
import Swal from 'sweetalert2';
import FilterBar from './FilterBar';
import EditModal from './EditModal';

const Libros = () => {
  const [libros, setLibros] = useState([]);
  const [loading, setLoading] = useState(true);
  const [busqueda, setBusqueda] = useState('');
  const [filtrosActivos, setFiltrosActivos] = useState({});
  
  // Estado para edición
  const [editModalOpen, setEditModalOpen] = useState(false);
  const [selectedItem, setSelectedItem] = useState(null);
  
  // Selección múltiple
  const [selectedIds, setSelectedIds] = useState([]);

  // Menú Contextual
  const { show } = useContextMenu({ id: 'menu-libros' });

  // Función para buscar con filtros
  const fetchLibros = async (query = '', filters = {}) => {
    setLoading(true);
    try {
      // Construimos los parámetros
      const params = { search: query, ...filters };
      const response = await axios.get('http://127.0.0.1:8000/api/libros/', { params });
      
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
    fetchLibros(busqueda, filtrosActivos);
  };

  // Función que recibe los datos del FilterBar
  const handleFilterApply = (newFilters) => {
    setFiltrosActivos(newFilters);
    fetchLibros(busqueda, newFilters);
  };

  // --- MENÚ CONTEXTUAL ---
  const handleContextMenu = (event, libro) => {
    event.preventDefault();
    // Solo mostramos el menú, NO seleccionamos la fila
    show({ event, props: libro });
  };

  // --- LÓGICA DE ELIMINAR ---
  const handleDelete = async (ids) => {
    const result = await Swal.fire({
      title: '¿Estás seguro?',
      text: `Se eliminarán ${ids.length} libro(s). Esta acción requiere autorización.`,
      icon: 'warning',
      showCancelButton: true,
      confirmButtonColor: '#d33',
      cancelButtonColor: '#3085d6',
      confirmButtonText: 'Sí, eliminar',
      cancelButtonText: 'Cancelar'
    });

    if (!result.isConfirmed) return;

    const { value: password } = await Swal.fire({
      title: 'Seguridad requerida',
      input: 'password',
      inputLabel: 'Ingresa tu contraseña de administrador',
      inputPlaceholder: 'Contraseña',
      showCancelButton: true,
      inputValidator: (value) => {
        if (!value) return '¡Debes ingresar la contraseña!';
      }
    });

    if (!password) return;

    try {
      await Promise.all(ids.map(id => axios.delete(`http://127.0.0.1:8000/api/libros/${id}/`)));
      Swal.fire('¡Eliminado!', 'Los registros han sido eliminados correctamente.', 'success');
      fetchLibros(busqueda, filtrosActivos);
      setSelectedIds([]);
    } catch (error) {
      Swal.fire('Error', 'No se pudo eliminar. Verifica tus permisos.', 'error');
    }
  };

  // --- LÓGICA DE EDITAR/CREAR ---
  const handleEditSave = async (id, data) => {
    try {
      if (id) {
        // MODO EDICIÓN (PATCH)
        await axios.patch(`http://127.0.0.1:8000/api/libros/${id}/`, data);
        Swal.fire('¡Guardado!', 'El libro ha sido actualizado correctamente.', 'success');
      } else {
        // MODO CREACIÓN (POST)
        await axios.post('http://127.0.0.1:8000/api/libros/', data);
        Swal.fire('Creado', 'Nuevo libro registrado exitosamente.', 'success');
      }
      setEditModalOpen(false);
      fetchLibros(busqueda, filtrosActivos);
    } catch (error) {
      Swal.fire('Error', 'Hubo un problema al guardar. Verifica el código (debe ser único).', 'error');
    }
  };

  // --- NUEVA FUNCIÓN: ABRIR MODAL PARA CREAR ---
  const handleCreateNew = () => {
    setSelectedItem(null); // null indica que es CREACIÓN
    setEditModalOpen(true);
  };

  // --- SELECCIÓN MÚLTIPLE ---
  const toggleSelect = (id) => {
    if (selectedIds.includes(id)) {
      setSelectedIds(selectedIds.filter(item => item !== id));
    } else {
      setSelectedIds([...selectedIds, id]);
    }
  };

  const toggleSelectAll = () => {
    if (selectedIds.length === libros.length && libros.length > 0) {
      setSelectedIds([]);
    } else {
      setSelectedIds(libros.map(l => l.id));
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 relative">
      {/* Header con Buscador */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-6 gap-4">
        <div className="flex items-center gap-4">
          <h2 className="text-2xl font-bold text-gray-800 flex items-center">
            <Book className="mr-2 text-primary" /> Catálogo de Libros
          </h2>
          
          {/* --- BOTÓN NUEVO --- */}
          <button 
            onClick={handleCreateNew}
            className="bg-green-600 text-white px-4 py-2 rounded-lg text-sm font-bold flex items-center hover:bg-green-700 transition-colors shadow-sm"
          >
            <Plus className="w-4 h-4 mr-2" /> Nuevo Libro
          </button>

          {selectedIds.length > 0 && (
            <button 
              onClick={() => handleDelete(selectedIds)}
              className="bg-red-100 text-red-600 px-3 py-1.5 rounded-lg text-sm font-bold flex items-center gap-1 hover:bg-red-200 transition-colors"
            >
              <Trash2 className="w-4 h-4" /> Eliminar ({selectedIds.length})
            </button>
          )}
        </div>
        
        <div className="flex gap-2 w-full md:w-auto">
          <form onSubmit={handleSearch} className="relative flex-1 md:w-80">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
            <input 
              type="text" 
              placeholder="Búsqueda rápida..." 
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
              value={busqueda}
              onChange={(e) => setBusqueda(e.target.value)}
            />
          </form>
          
          {/* BOTÓN DE FILTRO */}
          <FilterBar type="libros" onFilterApply={handleFilterApply} />
        </div>
      </div>

      {/* Tabla de Resultados */}
      {loading ? (
        <div className="text-center py-10 text-gray-500">Cargando catálogo...</div>
      ) : (
        <div className="overflow-x-auto min-h-[400px]">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-gray-50 text-gray-700 text-sm uppercase border-b">
                <th className="p-4 w-10">
                  <input 
                    type="checkbox" 
                    onChange={toggleSelectAll}
                    checked={selectedIds.length === libros.length && libros.length > 0}
                    className="w-4 h-4 cursor-pointer"
                  />
                </th>
                <th className="p-4">Código</th>
                <th className="p-4">Título / Materia</th>
                <th className="p-4">Ubicación</th>
                <th className="p-4">Estado</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100 text-sm text-gray-600">
              {libros.map((libro) => (
                <tr 
                  key={libro.id} 
                  className={`hover:bg-blue-50 transition-colors cursor-pointer ${selectedIds.includes(libro.id) ? 'bg-blue-100' : ''}`}
                  onContextMenu={(e) => handleContextMenu(e, libro)}
                >
                  <td className="p-4" onClick={(e) => e.stopPropagation()}>
                    <input 
                      type="checkbox" 
                      checked={selectedIds.includes(libro.id)} 
                      onChange={() => toggleSelect(libro.id)}
                      className="w-4 h-4 cursor-pointer"
                    />
                  </td>
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

      {/* Menú Click Derecho */}
      <Menu id="menu-libros" theme="light">
        <Item onClick={({ props }) => { setSelectedItem(props); setEditModalOpen(true); }}>
          <Edit className="w-4 h-4 mr-2 inline-block" /> Editar
        </Item>
        <Item onClick={({ props }) => handleDelete([props.id])}>
          <Trash2 className="w-4 h-4 mr-2 inline-block text-red-500" /> Eliminar
        </Item>
      </Menu>

      {/* Modal de Edición */}
      <EditModal 
        isOpen={editModalOpen} 
        onClose={() => setEditModalOpen(false)} 
        item={selectedItem} 
        type="libros" 
        onSave={handleEditSave} 
      />
    </div>
  );
};

export default Libros;
