import { useState, useEffect } from 'react';
import axios from 'axios';
import { Search, MapPin, Book, AlertCircle, Trash2, Edit, Plus, Hash, Layers, User, Calendar, Building2, BookOpen } from 'lucide-react';
import { Menu, Item, useContextMenu } from 'react-contexify';
import 'react-contexify/dist/ReactContexify.css';
import Swal from 'sweetalert2';
import FilterBar from './FilterBar';
import EditModal from './EditModal';
import { useCart } from '../context/CartContext';

const Libros = ({ onNavigateToPrestamos }) => {
  const [libros, setLibros] = useState([]);
  const [loading, setLoading] = useState(true);
  const [busqueda, setBusqueda] = useState('');
  const [filtrosActivos, setFiltrosActivos] = useState({});
  const [prestamosActivos, setPrestamosActivos] = useState([]);
  
  // Estado para edición
  const [editModalOpen, setEditModalOpen] = useState(false);
  const [selectedItem, setSelectedItem] = useState(null);
  
  // Carrito de préstamos (reemplaza selectedIds)
  const { cart, toggleItem } = useCart();

  // Menú Contextual
  const { show } = useContextMenu({ id: 'menu-libros' });

  // Función para buscar con filtros
  const fetchLibros = async (query = '', filters = {}) => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const config = { headers: { Authorization: `Bearer ${token}` } };
      
      // Construimos los parámetros
      const params = { search: query, ...filters };
      
      // Cargar libros Y préstamos activos en paralelo
      const [resLibros, resPrestamos] = await Promise.all([
        axios.get('http://127.0.0.1:8000/api/libros/', { params, ...config }),
        axios.get('http://127.0.0.1:8000/api/prestamos/?estado=VIGENTE', config)
      ]);
      
      const data = resLibros.data.results ? resLibros.data.results : resLibros.data;
      
      // 🎯 CONFIAMOS EN EL BACKEND - No reordenamos en el frontend
      // El backend ya envía los datos ordenados correctamente:
      // 1. Libros CON código de sección (ordenados por orden_importacion del Excel)
      // 2. Libros SIN código de sección al final
      
      setLibros(data);
      setPrestamosActivos(resPrestamos.data);
    } catch (error) {
      console.error("Error cargando libros:", error);
    }
    setLoading(false);
  };

  // Función para verificar si un libro está prestado
  const getEstadoPrestamo = (libroId) => {
    const prestamo = prestamosActivos.find(p => p.activo === libroId);
    if (!prestamo) return null;
    
    return {
      tipo: prestamo.tipo,
      label: prestamo.tipo === 'SALA' ? 'EN USO' : 'PRESTADO',
      estudiante: prestamo.estudiante_nombre
    };
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
          
          {/* BOTÓN PRESTAR SELECCIONADOS */}
          {cart.filter(item => item.tipo === 'LIBRO').length > 0 && (
            <button 
              onClick={onNavigateToPrestamos}
              className="bg-orange-500 text-white px-4 py-2 rounded-lg font-bold flex items-center shadow-lg hover:bg-orange-600 transition-all animate-pulse"
            >
              <BookOpen className="w-5 h-5 mr-2" /> 
              Prestar ({cart.filter(item => item.tipo === 'LIBRO').length}) Seleccionados
            </button>
          )}

          {/* BOTÓN NUEVO */}
          <button 
            onClick={handleCreateNew}
            className="bg-green-600 text-white px-4 py-2 rounded-lg text-sm font-bold flex items-center hover:bg-green-700 transition-colors shadow-sm"
          >
            <Plus className="w-4 h-4 mr-2" /> Nuevo Libro
          </button>
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

      {/* Tabla REDISEÑADA (Estilo Compacto como Tesis) */}
      {loading ? (
        <div className="text-center py-10 text-gray-500">Cargando catálogo...</div>
      ) : (
        <div className="overflow-x-auto min-h-[400px]">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-blue-50 text-gray-700 text-sm uppercase border-b border-blue-100 font-bold">
                <th className="p-4 w-10">
                    <BookOpen className="w-4 h-4 text-orange-500" title="Marcar para prestar" />
                </th>
                <th className="p-4">Códigos</th>
                <th className="p-4">Obra / Autor</th>
                <th className="p-4">Detalles Académicos</th>
                <th className="p-4">Ubicación</th>
                <th className="p-4 text-center">Estado</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100 text-sm text-gray-600">
              {libros.map((libro) => {
                const estadoPrestamo = getEstadoPrestamo(libro.id);
                const enCarrito = !!cart.find(c => c.id === libro.id);
                const isPrestado = !!estadoPrestamo;
                
                return (
                <tr 
                    key={libro.id} 
                    className={`transition-colors cursor-pointer ${
                      enCarrito ? 'bg-orange-50 border-l-4 border-orange-400' : 
                      isPrestado ? 'bg-red-50 opacity-75' : 
                      'hover:bg-blue-50'
                    }`}
                    onContextMenu={(e) => handleContextMenu(e, libro)}
                >
                  <td className="p-4 align-top" onClick={(e) => e.stopPropagation()}>
                      {!isPrestado ? (
                        <input 
                          type="checkbox" 
                          className="w-4 h-4 text-orange-600 border-gray-300 rounded focus:ring-orange-500"
                          checked={enCarrito} 
                          onChange={() => toggleItem({...libro, tipo: 'LIBRO'})} 
                          title="Marcar para prestar"
                        />
                      ) : (
                        <span className="text-red-500 text-xl font-bold" title="No disponible">✕</span>
                      )}
                  </td>
                  
                  {/* COLUMNA 1: CÓDIGOS (SIMPLIFICADA PARA VISUALIZACIÓN) */}
                  <td className={`p-4 align-top min-w-[180px] ${isPrestado ? 'text-red-700' : ''}`}>
                    <div className="flex flex-col gap-2">
                        {/* 1. Código Nuevo (Negrita Azul) */}
                        <div className={`font-bold text-base ${isPrestado ? 'text-red-700' : 'text-blue-700'}`}>
                            {libro.codigo_nuevo || 'S/C'}
                        </div>
                        
                        {isPrestado && (
                          <span className={`text-xs font-bold px-2 py-0.5 rounded ${
                            estadoPrestamo.tipo === 'SALA' 
                              ? 'bg-yellow-100 text-yellow-700 border border-yellow-300'
                              : 'bg-red-100 text-red-700 border border-red-300'
                          }`}>
                            {estadoPrestamo.tipo === 'SALA' ? 'EN USO' : 'PRESTADO'}
                          </span>
                        )}
                        
                        {/* 2. Código Antiguo (Gris pequeño) */}
                        <div className={`text-xs ${isPrestado ? 'text-red-400' : 'text-gray-500'}`}>
                            <Hash className="w-3 h-3 inline mr-1" />
                            Ant: {libro.codigo_antiguo || '-'}
                        </div>
                        
                        {/* 3. Ubicación Física (Código Sección - Destacado) */}
                        <div className={`text-sm font-mono px-2 py-1 rounded border font-bold inline-block ${
                          isPrestado ? 'bg-red-100 border-red-300 text-red-800' : 'bg-blue-100 border-blue-300 text-blue-800'
                        }`}>
                            <Layers className="w-3 h-3 inline mr-1" />
                            {libro.codigo_seccion_full || 'S/Ubicación'}
                        </div>
                    </div>
                  </td>

                  {/* COLUMNA 2: TÍTULO Y AUTOR */}
                  <td className={`p-4 align-top max-w-md ${isPrestado ? 'text-red-600' : ''}`}>
                    <div className={`font-medium text-base leading-tight mb-1 ${isPrestado ? 'text-red-600' : 'text-gray-800'}`}>
                        {libro.titulo}
                    </div>
                    {isPrestado && (
                      <div className="text-xs text-red-500 italic mt-1">
                        Por: {estadoPrestamo.estudiante}
                      </div>
                    )}
                    <div className={`flex items-center gap-1 text-xs font-medium mt-2 ${isPrestado ? 'text-red-500' : 'text-blue-600'}`}>
                        <User className="w-3 h-3" /> {libro.autor || 'Sin Autor'}
                    </div>
                    {libro.observaciones && (
                        <div className="text-[10px] text-gray-400 mt-1 italic bg-gray-50 p-1 rounded border border-gray-100 inline-block">
                            Obs: {libro.observaciones}
                        </div>
                    )}
                  </td>

                  {/* COLUMNA 3: DETALLES (Editorial, Edición, Materia, Año) */}
                  <td className={`p-4 align-top ${isPrestado ? 'text-red-600' : ''}`}>
                    <div className="flex flex-col gap-1 text-xs">
                        <div className={`font-semibold ${isPrestado ? 'text-red-600' : 'text-gray-700'}`}>{libro.editorial || 'S/Editorial'}</div>
                        <div className={isPrestado ? 'text-red-500' : 'text-gray-500'}>{libro.edicion || '-'}</div>
                        <div className={`flex items-center gap-1 mt-1 ${isPrestado ? 'text-red-600' : 'text-gray-600'}`}>
                            <Book className="w-3 h-3" /> {libro.materia || '-'}
                        </div>
                        <div className={`flex items-center gap-1 ${isPrestado ? 'text-red-500' : 'text-gray-500'}`}>
                            <Calendar className="w-3 h-3" /> {libro.anio || '-'}
                        </div>
                    </div>
                  </td>

                  {/* COLUMNA 4: UBICACIÓN */}
                  <td className={`p-4 align-top ${isPrestado ? 'text-red-600' : ''}`}>
                     <div className="flex flex-col gap-1 text-xs">
                        <div className={`flex items-center gap-1 font-bold ${isPrestado ? 'text-red-600' : 'text-gray-700'}`}>
                            <MapPin className="w-3 h-3 text-red-400" /> {libro.ubicacion_seccion || 'S/Ubicación'}
                        </div>
                        <div className={`pl-4 ${isPrestado ? 'text-red-500' : 'text-gray-500'}`}>{libro.ubicacion_repisa || '-'}</div>
                        {libro.facultad && (
                            <div className={`mt-1 flex items-center gap-1 text-[10px] border-t pt-1 ${isPrestado ? 'text-red-400' : 'text-gray-400'}`}>
                                <Building2 className="w-3 h-3" /> {libro.facultad}
                            </div>
                        )}
                     </div>
                  </td>

                  {/* COLUMNA 5: ESTADO */}
                  <td className="p-4 align-top text-center">
                    <span className={`px-2 py-1 rounded-full font-bold text-[10px] border inline-block
                      ${libro.estado === 'BUENO' ? 'bg-green-100 text-green-700 border-green-200' : 
                        libro.estado === 'REGULAR' ? 'bg-yellow-100 text-yellow-700 border-yellow-200' : 
                        'bg-red-100 text-red-700 border-red-200'}`}>
                      {libro.estado || 'REGULAR'}
                    </span>
                  </td>
                </tr>
                );
              })}
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
