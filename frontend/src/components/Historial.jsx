import { useState, useEffect } from 'react';
import axios from 'axios';
import { History, RotateCcw, Trash2, Edit3, PlusCircle } from 'lucide-react';
import Swal from 'sweetalert2';

const Historial = () => {
  const [registros, setRegistros] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchHistorial = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get('http://127.0.0.1:8000/api/historial/', {
        headers: { Authorization: `Bearer ${token}` }
      });
      setRegistros(response.data);
    } catch (error) {
      console.error("Error cargando historial", error);
    }
    setLoading(false);
  };

  useEffect(() => { fetchHistorial(); }, []);

  const handleRestaurar = async (item) => {
    // 1. Seguridad: Pedir contraseña
    const { value: password } = await Swal.fire({
        title: 'Restaurar Registro',
        text: `¿Deseas restaurar el ${item.tipo} "${item.titulo}" a este estado?`,
        icon: 'warning',
        input: 'password',
        inputLabel: 'Contraseña de Administrador requerida',
        showCancelButton: true,
        confirmButtonColor: '#10b981', // Verde
        confirmButtonText: 'Sí, Restaurar',
        cancelButtonText: 'Cancelar'
    });

    if (!password) return; // Si cancela o no pone pass

    try {
        // 2. Llamada a la API
        const token = localStorage.getItem('token');
        await axios.post(
          `http://127.0.0.1:8000/api/restaurar/${item.modelo}/${item.history_id}/`,
          {},
          { headers: { Authorization: `Bearer ${token}` } }
        );
        Swal.fire('Restaurado', 'El registro ha vuelto al inventario activo.', 'success');
        fetchHistorial(); // Recargar lista
    } catch (error) {
        Swal.fire('Error', 'No se pudo restaurar. Verifica la contraseña.', 'error');
    }
  };

  const getIcon = (accion) => {
    if (accion === 'Eliminado') return <Trash2 className="w-4 h-4 text-red-500" />;
    if (accion === 'Modificado') return <Edit3 className="w-4 h-4 text-orange-500" />;
    return <PlusCircle className="w-4 h-4 text-blue-900" />;
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
      <h2 className="text-2xl font-bold text-gray-800 flex items-center mb-6">
        <History className="mr-2 text-purple-600" /> Auditoría y Papelera
      </h2>

      {loading ? <p className="text-center py-10 text-gray-500">Cargando bitácora...</p> : (
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-gray-50 text-gray-700 text-xs uppercase border-b">
                <th className="p-4">Fecha / Hora</th>
                <th className="p-4">Usuario</th>
                <th className="p-4">Acción</th>
                <th className="p-4">Detalle (Título / Código)</th>
                <th className="p-4 text-center">Restaurar</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100 text-sm">
              {registros.map((item) => (
                <tr key={item.history_id} className="hover:bg-purple-50 transition-colors">
                  <td className="p-4 text-gray-500">
                    {new Date(item.fecha).toLocaleString()}
                  </td>
                  <td className="p-4 font-medium text-gray-700">{item.usuario}</td>
                  <td className="p-4">
                    <span className={`flex items-center gap-2 px-2 py-1 rounded-full text-xs font-bold w-max
                        ${item.accion === 'Eliminado' ? 'bg-red-100 text-red-700' : 
                          item.accion === 'Modificado' ? 'bg-orange-100 text-orange-700' : 'bg-blue-100 text-blue-900'}`}>
                        {getIcon(item.accion)} {item.accion}
                    </span>
                  </td>
                  <td className="p-4">
                    <div className="font-medium text-gray-800">{item.titulo}</div>
                    <div className="text-xs text-gray-500">{item.tipo} • {item.codigo}</div>
                  </td>
                  <td className="p-4 text-center">
                    {/* Solo mostramos botón restaurar si fue eliminado o modificado */}
                    {item.accion !== 'Creado' && (
                        <button 
                            onClick={() => handleRestaurar(item)}
                            title="Restaurar a este estado"
                            className="bg-white border border-gray-300 hover:bg-blue-50 hover:border-blue-900 hover:text-blue-900 text-gray-500 p-2 rounded-lg transition-all shadow-sm"
                        >
                            <RotateCcw className="w-4 h-4" />
                        </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default Historial;
