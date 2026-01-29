import { useState, useEffect } from 'react';
import axios from 'axios';
import { Search, User, Plus, Edit2, Trash2, Mail, Phone, CreditCard, GraduationCap } from 'lucide-react';
import Swal from 'sweetalert2';

const Estudiantes = () => {
  const [estudiantes, setEstudiantes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [busqueda, setBusqueda] = useState('');
  const [modalOpen, setModalOpen] = useState(false);
  const [editMode, setEditMode] = useState(false);
  const [formData, setFormData] = useState({
    id: null,
    nombre_completo: '',
    carnet_universitario: '',
    ci: '',
    carrera: '',
    email: '',
    telefono: ''
  });

  const fetchEstudiantes = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const res = await axios.get(`http://127.0.0.1:8000/api/estudiantes/?search=${busqueda}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setEstudiantes(res.data);
    } catch (error) {
      console.error('Error cargando estudiantes:', error);
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchEstudiantes();
  }, [busqueda]);

  const handleOpenModal = (estudiante = null) => {
    if (estudiante) {
      setFormData(estudiante);
      setEditMode(true);
    } else {
      setFormData({
        id: null,
        nombre_completo: '',
        carnet_universitario: '',
        ci: '',
        carrera: '',
        email: '',
        telefono: ''
      });
      setEditMode(false);
    }
    setModalOpen(true);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const token = localStorage.getItem('token');
      const config = { headers: { Authorization: `Bearer ${token}` } };

      if (editMode) {
        await axios.put(`http://127.0.0.1:8000/api/estudiantes/${formData.id}/`, formData, config);
        Swal.fire('¡Actualizado!', 'Estudiante actualizado correctamente', 'success');
      } else {
        await axios.post('http://127.0.0.1:8000/api/estudiantes/', formData, config);
        Swal.fire('¡Registrado!', 'Estudiante registrado correctamente', 'success');
      }

      setModalOpen(false);
      fetchEstudiantes();
    } catch (error) {
      console.error('Error guardando estudiante:', error);
      Swal.fire('Error', error.response?.data?.ci?.[0] || error.response?.data?.carnet_universitario?.[0] || 'No se pudo guardar el estudiante', 'error');
    }
  };

  const handleDelete = async (id, nombre) => {
    const result = await Swal.fire({
      title: '¿Eliminar estudiante?',
      text: `Se eliminará a ${nombre}`,
      icon: 'warning',
      showCancelButton: true,
      confirmButtonColor: '#d33',
      cancelButtonColor: '#3085d6',
      confirmButtonText: 'Sí, eliminar',
      cancelButtonText: 'Cancelar'
    });

    if (result.isConfirmed) {
      try {
        const token = localStorage.getItem('token');
        await axios.delete(`http://127.0.0.1:8000/api/estudiantes/${id}/`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        Swal.fire('Eliminado', 'Estudiante eliminado correctamente', 'success');
        fetchEstudiantes();
      } catch (error) {
        Swal.fire('Error', 'No se pudo eliminar el estudiante', 'error');
      }
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-gray-800 flex items-center gap-2">
          <User className="text-blue-500" /> Estudiantes
        </h2>
        <button
          onClick={() => handleOpenModal()}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg font-bold flex items-center hover:bg-blue-700 transition-colors"
        >
          <Plus className="w-4 h-4 mr-2" /> Nuevo Estudiante
        </button>
      </div>

      {/* Buscador */}
      <div className="mb-4 relative">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
        <input
          type="text"
          placeholder="Buscar por nombre, carnet o CI..."
          value={busqueda}
          onChange={(e) => setBusqueda(e.target.value)}
          className="w-full pl-10 pr-4 py-2 border rounded-lg outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      {/* Tabla */}
      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="bg-gray-50 text-gray-700 text-xs uppercase border-b">
              <th className="p-4">Nombre Completo</th>
              <th className="p-4">Carnet</th>
              <th className="p-4">CI</th>
              <th className="p-4">Carrera</th>
              <th className="p-4">Contacto</th>
              <th className="p-4">Préstamos</th>
              <th className="p-4">Acciones</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100 text-sm">
            {loading ? (
              <tr>
                <td colSpan="7" className="p-6 text-center text-gray-500">Cargando...</td>
              </tr>
            ) : estudiantes.length === 0 ? (
              <tr>
                <td colSpan="7" className="p-6 text-center text-gray-500">No se encontraron estudiantes</td>
              </tr>
            ) : (
              estudiantes.map((est) => (
                <tr key={est.id} className="hover:bg-gray-50">
                  <td className="p-4 font-medium text-gray-800">{est.nombre_completo}</td>
                  <td className="p-4">
                    <span className="bg-blue-100 text-blue-700 px-2 py-1 rounded text-xs font-bold">
                      {est.carnet_universitario}
                    </span>
                  </td>
                  <td className="p-4 text-gray-600">{est.ci}</td>
                  <td className="p-4 text-gray-600">{est.carrera}</td>
                  <td className="p-4">
                    <div className="text-xs text-gray-600 space-y-1">
                      {est.email && (
                        <div className="flex items-center gap-1">
                          <Mail className="w-3 h-3" /> {est.email}
                        </div>
                      )}
                      {est.telefono && (
                        <div className="flex items-center gap-1">
                          <Phone className="w-3 h-3" /> {est.telefono}
                        </div>
                      )}
                    </div>
                  </td>
                  <td className="p-4">
                    <span className={`px-2 py-1 rounded text-xs font-bold ${
                      est.prestamos_activos > 0 ? 'bg-orange-100 text-orange-700' : 'bg-gray-100 text-gray-600'
                    }`}>
                      {est.prestamos_activos || 0} activos
                    </span>
                  </td>
                  <td className="p-4">
                    <div className="flex gap-2">
                      <button
                        onClick={() => handleOpenModal(est)}
                        className="text-blue-600 hover:bg-blue-50 p-2 rounded transition-colors"
                        title="Editar"
                      >
                        <Edit2 className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => handleDelete(est.id, est.nombre_completo)}
                        className="text-red-600 hover:bg-red-50 p-2 rounded transition-colors"
                        title="Eliminar"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Modal */}
      {modalOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl w-full max-w-2xl shadow-2xl">
            <div className="p-6 border-b bg-blue-900 rounded-t-2xl text-white">
              <h3 className="text-xl font-bold flex items-center gap-2">
                <User className="w-5 h-5" />
                {editMode ? 'Editar Estudiante' : 'Nuevo Estudiante'}
              </h3>
            </div>

            <form onSubmit={handleSubmit} className="p-6 space-y-4">
              {/* Nombre Completo */}
              <div>
                <label className="block text-xs font-bold text-gray-500 uppercase mb-1">
                  Nombre Completo *
                </label>
                <input
                  type="text"
                  required
                  value={formData.nombre_completo}
                  onChange={(e) => setFormData({ ...formData, nombre_completo: e.target.value })}
                  className="w-full border rounded-lg p-2 outline-none focus:border-blue-500"
                  placeholder="Ej: Juan Pérez García"
                />
              </div>

              {/* Carnet y CI */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-bold text-gray-500 uppercase mb-1">
                    <CreditCard className="w-3 h-3 inline mr-1" /> Carnet Universitario *
                  </label>
                  <input
                    type="text"
                    required
                    value={formData.carnet_universitario}
                    onChange={(e) => setFormData({ ...formData, carnet_universitario: e.target.value })}
                    className="w-full border rounded-lg p-2 outline-none focus:border-blue-500"
                    placeholder="Ej: 202312345"
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold text-gray-500 uppercase mb-1">
                    Cédula de Identidad *
                  </label>
                  <input
                    type="text"
                    required
                    value={formData.ci}
                    onChange={(e) => setFormData({ ...formData, ci: e.target.value })}
                    className="w-full border rounded-lg p-2 outline-none focus:border-blue-500"
                    placeholder="Ej: 12345678"
                  />
                </div>
              </div>

              {/* Carrera */}
              <div>
                <label className="block text-xs font-bold text-gray-500 uppercase mb-1">
                  <GraduationCap className="w-3 h-3 inline mr-1" /> Carrera (opcional)
                </label>
                <input
                  type="text"
                  value={formData.carrera}
                  onChange={(e) => setFormData({ ...formData, carrera: e.target.value })}
                  className="w-full border rounded-lg p-2 outline-none focus:border-blue-500"
                  placeholder="Ej: Ingeniería Comercial"
                />
              </div>

              {/* Email y Teléfono */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-bold text-gray-500 uppercase mb-1">
                    <Mail className="w-3 h-3 inline mr-1" /> Correo Electrónico
                  </label>
                  <input
                    type="email"
                    value={formData.email}
                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                    className="w-full border rounded-lg p-2 outline-none focus:border-blue-500"
                    placeholder="correo@ejemplo.com"
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold text-gray-500 uppercase mb-1">
                    <Phone className="w-3 h-3 inline mr-1" /> Teléfono
                  </label>
                  <input
                    type="tel"
                    value={formData.telefono}
                    onChange={(e) => setFormData({ ...formData, telefono: e.target.value })}
                    className="w-full border rounded-lg p-2 outline-none focus:border-blue-500"
                    placeholder="77123456"
                  />
                </div>
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
                  className="px-4 py-2 bg-blue-600 text-white font-bold rounded-lg hover:bg-blue-700 transition-colors"
                >
                  {editMode ? 'Actualizar' : 'Registrar'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Estudiantes;
