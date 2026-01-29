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
    if (accion === 'Estado Anterior') return <RotateCcw className="w-4 h-4 text-gray-500" />;
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
                <th className="p-4">Detalle Completo</th>
                <th className="p-4 text-center">Restaurar</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100 text-sm">
              {registros.map((item) => (
                <tr key={item.history_id + (item.accion === 'Estado Anterior' ? '-anterior' : '')}
                  className={`transition-colors ${
                    item.accion === 'Estado Anterior' ? 'bg-gray-50 border-l-4 border-gray-300' : 'hover:bg-purple-50'
                  }`}>
                  <td className="p-4 text-gray-500">
                    {new Date(item.fecha).toLocaleString()}
                  </td>
                  <td className="p-4 font-medium text-gray-700">{item.usuario}</td>
                  <td className="p-4">
                    <span className={`flex items-center gap-2 px-2 py-1 rounded-full text-xs font-bold w-max
                        ${item.accion === 'Eliminado' ? 'bg-red-100 text-red-700' : 
                          item.accion === 'Modificado' ? 'bg-orange-100 text-orange-700' : 
                          item.accion === 'Estado Anterior' ? 'bg-gray-200 text-gray-700 border border-gray-400' : 'bg-blue-100 text-blue-900'}`}>
                        {getIcon(item.accion)} {item.accion}
                    </span>
                  </td>
                  <td className="p-4">
                    <div className="font-medium text-gray-800 mb-1">{item.titulo}</div>
                    <div className="text-xs text-gray-500 mb-1">{item.tipo} • {item.codigo}</div>
                    <div className="grid grid-cols-2 gap-x-4 gap-y-1 text-xs text-gray-600">
                      <span><b>Autor:</b> {item.autor || '-'}</span>
                      <span><b>Año:</b> {item.anio || '-'}</span>
                      <span><b>Facultad:</b> {item.facultad || '-'}</span>
                      <span><b>Estado:</b> {item.estado || '-'}</span>
                      <span><b>Observaciones:</b> {item.observaciones || '-'}</span>
                      <span><b>Sección:</b> {item.ubicacion_seccion || '-'}</span>
                      <span><b>Repisa:</b> {item.ubicacion_repisa || '-'}</span>
                      <span><b>Fecha Registro:</b> {item.fecha_registro ? new Date(item.fecha_registro).toLocaleString() : '-'}</span>
                      {item.tipo === 'Libro' && <><span><b>Materia:</b> {item.materia || '-'}</span>
                      <span><b>Editorial:</b> {item.editorial || '-'}</span>
                      <span><b>Edición:</b> {item.edicion || '-'}</span>
                      <span><b>Código Sección Full:</b> {item.codigo_seccion_full || '-'}</span>
                      <span><b>Orden Importación:</b> {item.orden_importacion || '-'}</span></>}
                      {item.tipo === 'Tesis' && <><span><b>Modalidad:</b> {item.modalidad || '-'}</span>
                      <span><b>Tutor:</b> {item.tutor || '-'}</span>
                      <span><b>Carrera:</b> {item.carrera || '-'}</span></>}
                    </div>
                    {item.accion === 'Estado Anterior' && (
                      <div className="text-xs text-gray-400 italic mt-1">Estado previo antes de la edición</div>
                    )}
                  </td>
                    <td className="p-4 text-center">
                    {/* Mostrar botón restaurar si no es 'Creado' */}
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
