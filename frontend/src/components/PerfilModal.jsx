import { useState, useEffect } from 'react';
import axios from 'axios';
import { X, Save, User, Lock, Mail, AlertCircle } from 'lucide-react';
import Swal from 'sweetalert2';

const PerfilModal = ({ isOpen, onClose, onLogout }) => {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    first_name: '',
    last_name: '',
    password: '' // Solo se llena si quiere cambiarla
  });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (isOpen) {
      // Cargar datos actuales del usuario
      const token = localStorage.getItem('token');
      axios.get('http://127.0.0.1:8000/api/perfil/', {
        headers: { Authorization: `Bearer ${token}` }
      })
      .then(res => setFormData(prev => ({ ...prev, ...res.data, password: '' })))
      .catch(err => {
        console.error('Error al cargar perfil:', err);
        Swal.fire('Error', 'No se pudieron cargar los datos del perfil.', 'error');
      });
    }
  }, [isOpen]);

  if (!isOpen) return null;

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const token = localStorage.getItem('token');
      const response = await axios.patch('http://127.0.0.1:8000/api/perfil/', formData, {
        headers: { Authorization: `Bearer ${token}` }
      });

      Swal.fire({
        icon: 'success',
        title: '¡Éxito!',
        text: response.data.mensaje,
        confirmButtonColor: '#1e40af'
      });
      
      // Si cambió la contraseña, forzamos logout para que entre de nuevo
      if (response.data.password_changed) {
        setTimeout(() => {
          onLogout();
        }, 1500);
      } else {
        onClose();
      }
    } catch (error) {
      console.error('Error al actualizar perfil:', error);
      Swal.fire({
        icon: 'error',
        title: 'Error',
        text: 'No se pudieron guardar los cambios. Intenta nuevamente.',
        confirmButtonColor: '#dc2626'
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl w-full max-w-md shadow-2xl flex flex-col">
        {/* Header */}
        <div className="p-6 border-b flex justify-between items-center bg-blue-900 rounded-t-2xl text-white">
          <h2 className="text-xl font-bold flex items-center gap-2">
            <User className="w-5 h-5" /> Mi Perfil
          </h2>
          <button 
            onClick={onClose}
            className="hover:bg-blue-800 rounded-full p-1 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>
        
        {/* Form */}
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {/* Usuario */}
          <div>
            <label className="text-xs font-bold text-gray-500 uppercase mb-1 block">
              Usuario
            </label>
            <div className="flex items-center border rounded-lg p-2 bg-gray-50">
              <User className="w-4 h-4 text-gray-400 mr-2" />
              <input 
                name="username" 
                value={formData.username} 
                onChange={handleChange} 
                className="w-full bg-transparent outline-none"
                required
              />
            </div>
          </div>

          {/* Nombre y Apellido */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-xs font-bold text-gray-500 uppercase mb-1 block">
                Nombre
              </label>
              <input 
                name="first_name" 
                value={formData.first_name} 
                onChange={handleChange} 
                className="w-full border rounded-lg p-2 outline-none focus:border-blue-500 transition-colors"
                placeholder="Tu nombre"
              />
            </div>
            <div>
              <label className="text-xs font-bold text-gray-500 uppercase mb-1 block">
                Apellido
              </label>
              <input 
                name="last_name" 
                value={formData.last_name} 
                onChange={handleChange} 
                className="w-full border rounded-lg p-2 outline-none focus:border-blue-500 transition-colors"
                placeholder="Tu apellido"
              />
            </div>
          </div>

          {/* Email */}
          <div>
            <label className="text-xs font-bold text-gray-500 uppercase mb-1 block">
              Correo Electrónico
            </label>
            <div className="flex items-center border rounded-lg p-2">
              <Mail className="w-4 h-4 text-gray-400 mr-2" />
              <input 
                name="email" 
                type="email"
                value={formData.email} 
                onChange={handleChange} 
                className="w-full outline-none"
                placeholder="correo@ejemplo.com"
              />
            </div>
          </div>

          {/* Cambiar Contraseña */}
          <div className="pt-4 border-t">
            <label className="text-xs font-bold text-red-500 uppercase flex items-center gap-1 mb-2">
              <Lock className="w-3 h-3" /> Cambiar Contraseña
            </label>
            <input 
              type="password" 
              name="password" 
              value={formData.password} 
              onChange={handleChange} 
              placeholder="Escribe para cambiar (o deja vacío)" 
              className="w-full border rounded-lg p-2 outline-none focus:border-red-500 bg-red-50 transition-colors" 
            />
            <div className="flex items-start gap-1 mt-2 text-amber-600 bg-amber-50 p-2 rounded-lg">
              <AlertCircle className="w-4 h-4 mt-0.5 flex-shrink-0" />
              <p className="text-[10px]">
                Si cambias la contraseña, tendrás que iniciar sesión nuevamente.
              </p>
            </div>
          </div>

          {/* Botón Guardar */}
          <button 
            type="submit" 
            disabled={loading}
            className="w-full bg-blue-600 text-white py-3 rounded-lg font-bold hover:bg-blue-700 shadow-lg transition-all flex justify-center items-center gap-2 mt-6 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? (
              <>
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                <span>Guardando...</span>
              </>
            ) : (
              <>
                <Save className="w-5 h-5" />
                <span>Guardar Cambios</span>
              </>
            )}
          </button>
        </form>
      </div>
    </div>
  );
};

export default PerfilModal;
