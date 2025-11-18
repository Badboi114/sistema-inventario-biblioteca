import { useState, useEffect } from 'react';
import axios from 'axios';
import { Search, MapPin, GraduationCap, AlertCircle, User, Users, Award, Trash2, Edit, Plus } from 'lucide-react';
import { Menu, Item, useContextMenu } from 'react-contexify';
import 'react-contexify/dist/ReactContexify.css';
import Swal from 'sweetalert2';
import FilterBar from './FilterBar';
import EditModal from './EditModal';

const Tesis = () => {
  const [tesis, setTesis] = useState([]);
  const [loading, setLoading] = useState(true);
  const [busqueda, setBusqueda] = useState('');
  const [filtrosActivos, setFiltrosActivos] = useState({});
  
  // Estado para edición
  const [editModalOpen, setEditModalOpen] = useState(false);
  const [selectedItem, setSelectedItem] = useState(null);
  
  // Selección múltiple
  const [selectedIds, setSelectedIds] = useState([]);

  // Menú Contextual
  const { show } = useContextMenu({ id: 'menu-tesis' });

  // Función para buscar en la API con filtros opcionales
  const fetchTesis = async (query = '', filters = {}) => {
    setLoading(true);
    try {
      const params = {
        search: query,
        ...filters
      };
      const response = await axios.get('http://127.0.0.1:8000/api/tesis/', { params });
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
    fetchTesis(busqueda, filtrosActivos);
  };

  const handleFilterApply = (newFilters) => {
    setFiltrosActivos(newFilters);
    fetchTesis(busqueda, newFilters);
  };

  // --- MENÚ CONTEXTUAL ---
  const handleContextMenu = (event, item) => {
    event.preventDefault();
    // Solo mostramos el menú, NO seleccionamos la fila
    show({ event, props: item });
  };

  // --- LÓGICA DE ELIMINAR ---
  const handleDelete = async (ids) => {
    const result = await Swal.fire({
      title: '¿Estás seguro?',
      text: `Se eliminarán ${ids.length} tesis/proyecto(s). Esta acción requiere autorización.`,
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
      await Promise.all(ids.map(id => axios.delete(`http://127.0.0.1:8000/api/tesis/${id}/`)));
      Swal.fire('¡Eliminado!', 'Los registros han sido eliminados correctamente.', 'success');
      fetchTesis(busqueda, filtrosActivos);
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
        await axios.patch(`http://127.0.0.1:8000/api/tesis/${id}/`, data);
        Swal.fire('¡Guardado!', 'La tesis ha sido actualizada correctamente.', 'success');
      } else {
        // MODO CREACIÓN (POST)
        await axios.post('http://127.0.0.1:8000/api/tesis/', data);
        Swal.fire('Creado', 'Nueva tesis registrada exitosamente.', 'success');
      }
      setEditModalOpen(false);
      fetchTesis(busqueda, filtrosActivos);
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
    if (selectedIds.length === tesis.length && tesis.length > 0) {
      setSelectedIds([]);
    } else {
      setSelectedIds(tesis.map(t => t.id));
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 relative">
      {/* Header con Buscador */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-6 gap-4">
        <div className="flex items-center gap-4">
          <h2 className="text-2xl font-bold text-gray-800 flex items-center">
            <GraduationCap className="mr-2 text-green-600" /> Proyectos de Grado y Tesis
          </h2>
          {selectedIds.length > 0 && (
            <button 
              onClick={() => handleDelete(selectedIds)}
              className="bg-red-100 text-red-600 px-3 py-1.5 rounded-lg text-sm font-bold flex items-center gap-1 hover:bg-red-200 transition-colors"
            >
              <Trash2 className="w-4 h-4" /> Eliminar ({selectedIds.length})
            </button>
          )}
          
          {/* --- BOTÓN NUEVO --- */}
          <button 
            onClick={handleCreateNew}
            className="bg-green-600 text-white px-4 py-2 rounded-lg text-sm font-bold flex items-center hover:bg-green-700 transition-colors shadow-sm"
          >
            <Plus className="w-4 h-4 mr-2" /> Nueva Tesis
          </button>
        </div>
        
        <div className="flex gap-2 w-full md:w-auto">
          <form onSubmit={handleSearch} className="relative flex-1 md:w-80">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
            <input 
              type="text" 
              placeholder="Búsqueda rápida..." 
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
              value={busqueda}
              onChange={(e) => setBusqueda(e.target.value)}
            />
          </form>
          
          {/* BOTÓN DE FILTRO */}
          <FilterBar type="tesis" onFilterApply={handleFilterApply} />
        </div>
      </div>

      {/* Tabla de Resultados */}
      {loading ? (
        <div className="text-center py-10 text-gray-500">Cargando investigaciones...</div>
      ) : (
        <div className="overflow-x-auto min-h-[400px]">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-green-50 text-gray-700 text-sm uppercase border-b border-green-100">
                <th className="p-4 w-10">
                  <input 
                    type="checkbox" 
                    onChange={toggleSelectAll}
                    checked={selectedIds.length === tesis.length && tesis.length > 0}
                    className="w-4 h-4 cursor-pointer"
                  />
                </th>
                <th className="p-4">Código</th>
                <th className="p-4">Título / Modalidad</th>
                <th className="p-4">Autor y Tutor</th>
                <th className="p-4">Carrera / Año</th>
                <th className="p-4">Estado</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100 text-sm text-gray-600">
              {tesis.map((item) => (
                <tr 
                  key={item.id} 
                  className={`hover:bg-green-50 transition-colors cursor-pointer ${selectedIds.includes(item.id) ? 'bg-green-100' : ''}`}
                  onContextMenu={(e) => handleContextMenu(e, item)}
                >
                  <td className="p-4" onClick={(e) => e.stopPropagation()}>
                    <input 
                      type="checkbox" 
                      checked={selectedIds.includes(item.id)} 
                      onChange={() => toggleSelect(item.id)}
                      className="w-4 h-4 cursor-pointer"
                    />
                  </td>
                  <td className="p-4 font-bold text-green-700 whitespace-nowrap">
                    {item.codigo_nuevo}
                  </td>
                  <td className="p-4 max-w-md">
                    <div className="font-medium text-gray-800 truncate mb-1" title={item.titulo}>
                      {item.titulo}
                    </div>
                    <div className="text-xs text-gray-500 flex items-center gap-1">
                      <span className="bg-gray-100 px-2 py-0.5 rounded border border-gray-200">
                        {item.modalidad}
                      </span>
                    </div>
                  </td>
                  <td className="p-4">
                    <div className="flex flex-col gap-1">
                      <div className="flex items-center gap-1 text-gray-800">
                        <User className="w-3 h-3 text-blue-500" /> 
                        <span className="font-medium text-xs">{item.autor}</span>
                      </div>
                      <div className="flex items-center gap-1 text-gray-500 text-xs">
                        <Users className="w-3 h-3" />
                        <span className="font-semibold">Tutor:</span> {item.tutor}
                      </div>
                    </div>
                  </td>
                  <td className="p-4">
                    <div className="flex flex-col gap-1">
                      <div className="flex items-center gap-1 text-xs">
                        <Award className="w-3 h-3 text-gray-400" />
                        {item.carrera}
                      </div>
                      <div className="text-gray-400 text-xs">
                        {item.anio}
                      </div>
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

      {/* Menú Click Derecho */}
      <Menu id="menu-tesis" theme="light">
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
        type="tesis" 
        onSave={handleEditSave} 
      />
    </div>
  );
};

export default Tesis;
