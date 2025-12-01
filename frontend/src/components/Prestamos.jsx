import { useState, useEffect } from 'react';
import axios from 'axios';
import { Search, Clock, CheckCircle, AlertTriangle, Plus, X, Calendar, BookOpen, User as UserIcon } from 'lucide-react';
import Swal from 'sweetalert2';

const Prestamos = () => {
  const [prestamos, setPrestamos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [busqueda, setBusqueda] = useState('');
  const [modalOpen, setModalOpen] = useState(false);

  // Estado del formulario
  const [formData, setFormData] = useState({
    estudiante: '',
    activo: '',
    tipo: 'SALA',
    observaciones: ''
  });

  // Listas para seleccionar
  const [estudiantes, setEstudiantes] = useState([]);
  const [activos, setActivos] = useState([]);
  const [activoSeleccionado, setActivoSeleccionado] = useState(null);

  const fetchPrestamos = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const res = await axios.get(`http://127.0.0.1:8000/api/prestamos/?search=${busqueda}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setPrestamos(res.data);
    } catch (error) {
      console.error('Error cargando préstamos:', error);
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchPrestamos();
  }, [busqueda]);

  const cargarDatosModal = async () => {
    try {
      const token = localStorage.getItem('token');
      const config = { headers: { Authorization: `Bearer ${token}` } };

      // Cargar estudiantes
      const resEst = await axios.get('http://127.0.0.1:8000/api/estudiantes/', config);
      setEstudiantes(resEst.data);

      // Cargar activos (libros y tesis)
      const resAct = await axios.get('http://127.0.0.1:8000/api/activos/', config);
      setActivos(resAct.data);
    } catch (error) {
      console.error('Error cargando datos:', error);
    }
  };

  const handleOpenModal = () => {
    setFormData({
      estudiante: '',
      activo: '',
      tipo: 'SALA',
      observaciones: ''
    });
    setActivoSeleccionado(null);
    setModalOpen(true);
    cargarDatosModal();
  };

  const handleSelectActivo = (activoId) => {
    const activo = activos.find(a => a.id === parseInt(activoId));
    setActivoSeleccionado(activo);
    setFormData({ ...formData, activo: activoId, tipo: 'SALA' });

    // Si es tesis, mostrar alerta
    if (activo && activo.tipo === 'TESIS') {
      Swal.fire({
        icon: 'info',
        title: 'Atención',
        text: 'Has seleccionado una Tesis. Solo se puede prestar para consulta en SALA.',
        toast: true,
        position: 'top-end',
        timer: 3000,
        showConfirmButton: false
      });
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      const token = localStorage.getItem('token');
      await axios.post('http://127.0.0.1:8000/api/prestamos/', formData, {
        headers: { Authorization: `Bearer ${token}` }
      });

      const tipoGarantia = formData.tipo === 'SALA' ? 'Carnet Universitario' : 'Cédula de Identidad';

      Swal.fire({
        icon: 'success',
        title: '¡Préstamo Registrado!',
        html: `
          <p class="text-sm text-gray-600">No olvides solicitar:</p>
          <p class="font-bold text-lg text-blue-700">${tipoGarantia}</p>
        `,
        confirmButtonColor: '#1e40af'
      });

      setModalOpen(false);
      fetchPrestamos();
    } catch (error) {
      console.error('Error creando préstamo:', error);
      Swal.fire({
        icon: 'error',
        title: 'Error',
        text: error.response?.data?.tipo?.[0] || 'No se pudo registrar el préstamo',
        confirmButtonColor: '#dc2626'
      });
    }
  };

  const handleDevolucion = async (id) => {
    const result = await Swal.fire({
      title: '¿Confirmar devolución?',
      text: 'Se marcará el material como devuelto',
      icon: 'question',
      showCancelButton: true,
      confirmButtonColor: '#10b981',
      cancelButtonColor: '#6b7280',
      confirmButtonText: 'Sí, devolver',
      cancelButtonText: 'Cancelar'
    });

    if (result.isConfirmed) {
      try {
        const token = localStorage.getItem('token');
        const res = await axios.post(
          `http://127.0.0.1:8000/api/prestamos/${id}/devolver/`,
          {},
          { headers: { Authorization: `Bearer ${token}` } }
        );

        Swal.fire({
          icon: 'success',
          title: 'Devuelto',
          text: res.data.mensaje,
          confirmButtonColor: '#10b981'
        });

        fetchPrestamos();
      } catch (error) {
        Swal.fire('Error', 'No se pudo registrar la devolución', 'error');
      }
    }
  };

  const formatFecha = (fecha) => {
    return new Date(fecha).toLocaleDateString('es-BO', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const estaAtrasado = (prestamo) => {
    if (prestamo.estado === 'DEVUELTO') return false;
    return new Date() > new Date(prestamo.fecha_devolucion_estimada);
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-gray-800 flex items-center gap-2">
          <Clock className="text-orange-500" /> Gestión de Préstamos
        </h2>
        <button
          onClick={handleOpenModal}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg font-bold flex items-center hover:bg-blue-700 transition-colors"
        >
          <Plus className="w-4 h-4 mr-2" /> Nuevo Préstamo
        </button>
      </div>

      {/* Buscador */}
      <div className="mb-4 relative">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
        <input
          type="text"
          placeholder="Buscar por estudiante, código o título..."
          value={busqueda}
          onChange={(e) => setBusqueda(e.target.value)}
          className="w-full pl-10 pr-4 py-2 border rounded-lg outline-none focus:ring-2 focus:ring-orange-500"
        />
      </div>

      {/* Tabla */}
      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="bg-gray-50 text-gray-700 text-xs uppercase border-b">
              <th className="p-4">Estudiante</th>
              <th className="p-4">Material Prestado</th>
              <th className="p-4">Tipo / Garantía</th>
              <th className="p-4">Fechas</th>
              <th className="p-4">Estado</th>
              <th className="p-4">Acción</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100 text-sm">
            {loading ? (
              <tr>
                <td colSpan="6" className="p-6 text-center text-gray-500">Cargando...</td>
              </tr>
            ) : prestamos.length === 0 ? (
              <tr>
                <td colSpan="6" className="p-6 text-center text-gray-500">No hay préstamos registrados</td>
              </tr>
            ) : (
              prestamos.map((p) => (
                <tr
                  key={p.id}
                  className={`${p.estado === 'DEVUELTO' ? 'bg-gray-50 opacity-60' : ''} ${
                    estaAtrasado(p) ? 'bg-red-50' : ''
                  }`}
                >
                  {/* Estudiante */}
                  <td className="p-4">
                    <div className="font-bold text-gray-800">{p.estudiante_nombre}</div>
                    <div className="text-xs text-gray-500">{p.estudiante_carrera}</div>
                    <div className="text-xs text-blue-600">{p.estudiante_carnet}</div>
                  </td>

                  {/* Material */}
                  <td className="p-4">
                    <div className="flex items-center gap-2">
                      {p.activo_tipo === 'LIBRO' ? (
                        <BookOpen className="w-4 h-4 text-blue-500" />
                      ) : (
                        <BookOpen className="w-4 h-4 text-purple-500" />
                      )}
                      <div>
                        <div className="font-medium text-blue-700">{p.activo_codigo || 'S/C'}</div>
                        <div className="text-xs text-gray-600 truncate max-w-xs">{p.activo_titulo}</div>
                        <div className="text-[10px] text-gray-400 uppercase">{p.activo_tipo}</div>
                      </div>
                    </div>
                  </td>

                  {/* Tipo y Garantía */}
                  <td className="p-4">
                    <span
                      className={`px-2 py-1 rounded text-xs font-bold ${
                        p.tipo === 'SALA'
                          ? 'bg-purple-100 text-purple-700'
                          : 'bg-orange-100 text-orange-700'
                      }`}
                    >
                      {p.tipo}
                    </span>
                    <div className="text-[10px] mt-1 text-gray-500">
                      {p.tipo === 'SALA' ? '📇 Carnet Univ.' : '🪪 C.I.'}
                    </div>
                  </td>

                  {/* Fechas */}
                  <td className="p-4 text-xs">
                    <div className="space-y-1">
                      <div>
                        <span className="text-gray-500">Salida:</span>{' '}
                        <span className="font-medium">{formatFecha(p.fecha_prestamo)}</span>
                      </div>
                      <div>
                        <span className="text-gray-500">Límite:</span>{' '}
                        <span
                          className={`font-bold ${
                            estaAtrasado(p) ? 'text-red-600' : 'text-green-600'
                          }`}
                        >
                          {formatFecha(p.fecha_devolucion_estimada)}
                        </span>
                      </div>
                      {p.fecha_devolucion_real && (
                        <div>
                          <span className="text-gray-500">Devuelto:</span>{' '}
                          <span className="font-medium text-gray-700">
                            {formatFecha(p.fecha_devolucion_real)}
                          </span>
                        </div>
                      )}
                    </div>
                  </td>

                  {/* Estado */}
                  <td className="p-4">
                    {p.estado === 'VIGENTE' && !estaAtrasado(p) && (
                      <span className="text-green-600 font-bold flex items-center gap-1">
                        <Clock className="w-3 h-3" /> Activo
                      </span>
                    )}
                    {p.estado === 'VIGENTE' && estaAtrasado(p) && (
                      <span className="text-red-600 font-bold flex items-center gap-1">
                        <AlertTriangle className="w-3 h-3" /> Atrasado
                      </span>
                    )}
                    {p.estado === 'DEVUELTO' && (
                      <span className="text-gray-500 font-bold flex items-center gap-1">
                        <CheckCircle className="w-3 h-3" /> Cerrado
                      </span>
                    )}
                  </td>

                  {/* Acción */}
                  <td className="p-4">
                    {p.estado !== 'DEVUELTO' && (
                      <button
                        onClick={() => handleDevolucion(p.id)}
                        className="bg-green-500 text-white px-3 py-1 rounded text-xs hover:bg-green-600 transition-colors font-bold"
                      >
                        Devolver
                      </button>
                    )}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Modal de Nuevo Préstamo */}
      {modalOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl w-full max-w-2xl shadow-2xl">
            <div className="p-6 border-b bg-orange-600 rounded-t-2xl text-white flex justify-between items-center">
              <h3 className="text-xl font-bold flex items-center gap-2">
                <Clock className="w-5 h-5" /> Registrar Préstamo
              </h3>
              <button onClick={() => setModalOpen(false)} className="hover:bg-orange-700 rounded-full p-1">
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleSubmit} className="p-6 space-y-4">
              {/* Estudiante */}
              <div>
                <label className="block text-xs font-bold text-gray-500 uppercase mb-1">
                  <UserIcon className="w-3 h-3 inline mr-1" /> Estudiante *
                </label>
                <select
                  required
                  value={formData.estudiante}
                  onChange={(e) => setFormData({ ...formData, estudiante: e.target.value })}
                  className="w-full p-2 border rounded-lg outline-none focus:border-orange-500"
                >
                  <option value="">Seleccionar Estudiante...</option>
                  {estudiantes.map((e) => (
                    <option key={e.id} value={e.id}>
                      {e.nombre_completo} ({e.carnet_universitario}) - {e.carrera}
                    </option>
                  ))}
                </select>
                {estudiantes.length === 0 && (
                  <p className="text-xs text-red-500 mt-1">
                    No hay estudiantes registrados. Regístralos primero en la sección Estudiantes.
                  </p>
                )}
              </div>

              {/* Material (Libro o Tesis) */}
              <div>
                <label className="block text-xs font-bold text-gray-500 uppercase mb-1">
                  <BookOpen className="w-3 h-3 inline mr-1" /> Material a Prestar *
                </label>
                <select
                  required
                  value={formData.activo}
                  onChange={(e) => handleSelectActivo(e.target.value)}
                  className="w-full p-2 border rounded-lg outline-none focus:border-orange-500"
                >
                  <option value="">Buscar Libro o Tesis...</option>
                  {activos.map((a) => (
                    <option key={a.id} value={a.id}>
                      [{a.tipo}] {a.codigo_nuevo || 'S/C'} - {a.titulo.substring(0, 60)}...
                    </option>
                  ))}
                </select>
              </div>

              {/* Tipo de Préstamo */}
              <div>
                <label className="block text-xs font-bold text-gray-500 uppercase mb-2">
                  Tipo de Préstamo *
                </label>
                <div className="grid grid-cols-2 gap-4">
                  {/* En Sala */}
                  <div
                    onClick={() => setFormData({ ...formData, tipo: 'SALA' })}
                    className={`p-4 border-2 rounded-lg cursor-pointer text-center transition-all ${
                      formData.tipo === 'SALA'
                        ? 'bg-purple-100 border-purple-500 ring-2 ring-purple-200'
                        : 'hover:bg-gray-50 border-gray-200'
                    }`}
                  >
                    <div className="font-bold text-purple-700 text-lg">EN SALA</div>
                    <div className="text-xs text-gray-500 mt-1">📇 Deja Carnet Universitario</div>
                    <div className="text-[10px] text-gray-400 mt-2">Devuelve el mismo día</div>
                  </div>

                  {/* A Domicilio (Deshabilitado si es Tesis) */}
                  {activoSeleccionado?.tipo !== 'TESIS' ? (
                    <div
                      onClick={() => setFormData({ ...formData, tipo: 'DOMICILIO' })}
                      className={`p-4 border-2 rounded-lg cursor-pointer text-center transition-all ${
                        formData.tipo === 'DOMICILIO'
                          ? 'bg-orange-100 border-orange-500 ring-2 ring-orange-200'
                          : 'hover:bg-gray-50 border-gray-200'
                      }`}
                    >
                      <div className="font-bold text-orange-700 text-lg">DOMICILIO</div>
                      <div className="text-xs text-gray-500 mt-1">🪪 Deja Cédula de Identidad</div>
                      <div className="text-[10px] text-gray-400 mt-2">Máximo 2 días</div>
                    </div>
                  ) : (
                    <div className="p-4 border-2 rounded-lg bg-gray-100 border-gray-300 cursor-not-allowed text-center opacity-50">
                      <div className="font-bold text-gray-500 text-lg">DOMICILIO</div>
                      <div className="text-xs text-red-500 font-bold mt-1">
                        🚫 NO PERMITIDO (Tesis)
                      </div>
                      <div className="text-[10px] text-gray-400 mt-2">Solo consulta en sala</div>
                    </div>
                  )}
                </div>
              </div>

              {/* Observaciones */}
              <div>
                <label className="block text-xs font-bold text-gray-500 uppercase mb-1">
                  Observaciones
                </label>
                <textarea
                  value={formData.observaciones}
                  onChange={(e) => setFormData({ ...formData, observaciones: e.target.value })}
                  className="w-full p-2 border rounded-lg outline-none focus:border-orange-500"
                  rows="2"
                  placeholder="Notas adicionales (opcional)"
                />
              </div>

              {/* Botones */}
              <div className="flex justify-end gap-2 mt-6 pt-4 border-t">
                <button
                  type="button"
                  onClick={() => setModalOpen(false)}
                  className="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-orange-600 text-white font-bold rounded-lg hover:bg-orange-700 transition-colors"
                >
                  Registrar Salida
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Prestamos;
