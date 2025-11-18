import { useState, useEffect } from 'react';
import { X, Save, AlertCircle, PlusCircle } from 'lucide-react';

const EditModal = ({ isOpen, onClose, item, type, onSave }) => {
  const [formData, setFormData] = useState({});
  const [error, setError] = useState('');

  useEffect(() => {
    if (isOpen) {
        setError('');
        if (item) {
            // MODO EDICIÓN: Cargar datos existentes
            const cleanItem = {};
            Object.keys(item).forEach(key => {
                cleanItem[key] = item[key] === null || item[key] === undefined ? '' : item[key];
            });
            setFormData(cleanItem);
        } else {
            // MODO CREACIÓN: Formulario limpio
            setFormData({}); 
        }
    }
  }, [item, isOpen]);

  if (!isOpen) return null;

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    // Solo validar título y código (campos realmente obligatorios)
    if (!formData.titulo || !formData.codigo_nuevo) {
      setError('El Título y el Código son obligatorios.');
      return;
    }
    setError('');
    // Si hay item, mandamos su ID, si no, mandamos null (crear)
    onSave(item ? item.id : null, formData);
  };

  // Campos dinámicos según tipo - TODOS OPCIONALES excepto título y código
  const fields = type === 'libros' ? [
    { name: 'titulo', label: 'Título del Libro' },
    { name: 'autor', label: 'Autor(es)' },
    { name: 'codigo_nuevo', label: 'Código Inventario' },
    { name: 'materia', label: 'Materia Asignada' },
    { name: 'editorial', label: 'Editorial' },
    { name: 'ubicacion_seccion', label: 'Ubicación (Sección)' },
    { name: 'ubicacion_repisa', label: 'Ubicación (Repisa)' },
    { name: 'anio', label: 'Año' },
    { name: 'estado', label: 'Estado Físico', type: 'select', options: ['BUENO', 'REGULAR', 'MALO', 'EN REPARACION'] }
  ] : [
    { name: 'titulo', label: 'Título del Proyecto' },
    { name: 'autor', label: 'Estudiante / Autor' },
    { name: 'tutor', label: 'Tutor Guía' },
    { name: 'carrera', label: 'Carrera' },
    { name: 'codigo_nuevo', label: 'Código Inventario' },
    { name: 'anio', label: 'Año' },
    { name: 'modalidad', label: 'Modalidad', type: 'select', options: ['TESIS', 'PROYECTO DE GRADO', 'TRABAJO DIRIGIDO'] },
    { name: 'ubicacion_seccion', label: 'Ubicación' },
    { name: 'estado', label: 'Estado Físico', type: 'select', options: ['BUENO', 'REGULAR', 'MALO', 'EN REPARACION'] }
  ];

  const isEditing = !!item;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl w-full max-w-2xl shadow-2xl max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="p-6 border-b flex justify-between items-center bg-gray-50 rounded-t-2xl">
          <div>
            <h2 className="text-xl font-bold text-gray-800 flex items-center gap-2">
                {isEditing ? <Save className="w-5 h-5 text-blue-600" /> : <PlusCircle className="w-5 h-5 text-green-600" />}
                {isEditing ? `Editar ${type === 'libros' ? 'Libro' : 'Tesis'}` : `Registrar Nuevo ${type === 'libros' ? 'Libro' : 'Tesis'}`}
            </h2>
            <p className="text-sm text-gray-500">
                {isEditing ? 'Modifica los detalles del registro.' : 'Completa la información para agregar al inventario.'}
            </p>
          </div>
          <button onClick={onClose} className="p-2 hover:bg-gray-200 rounded-full transition-colors">
            <X className="text-gray-600" />
          </button>
        </div>
        
        {/* Body */}
        <div className="p-6 overflow-y-auto">
            {error && (
                <div className="mb-4 p-3 bg-red-50 text-red-600 rounded-lg text-sm flex items-center">
                    <AlertCircle className="w-4 h-4 mr-2" /> {error}
                </div>
            )}
            
            <form id="edit-form" onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {fields.map((field) => (
                <div key={field.name} className={field.name === 'titulo' ? 'md:col-span-2' : ''}>
                <label className="block text-xs font-bold text-gray-500 uppercase mb-1 tracking-wider">
                  {field.label} {(field.name === 'titulo' || field.name === 'codigo_nuevo') && <span className="text-red-500">*</span>}
                </label>
                {field.type === 'select' ? (
                    <select 
                    name={field.name} 
                    value={formData[field.name] || ''} 
                    onChange={handleChange}
                    className="w-full p-2.5 border border-gray-300 rounded-lg bg-white focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition-all"
                    >
                    <option value="">-- Seleccionar --</option>
                    {field.options.map(opt => <option key={opt} value={opt}>{opt}</option>)}
                    </select>
                ) : (
                    <input
                    type={field.name === 'anio' ? 'number' : 'text'}
                    name={field.name}
                    value={formData[field.name] || ''}
                    onChange={handleChange}
                    placeholder={field.name === 'codigo_nuevo' ? 'Ej: IND-001' : ''}
                    className="w-full p-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition-all"
                    />
                )}
                </div>
            ))}
            </form>
        </div>

        {/* Footer */}
        <div className="p-6 border-t bg-gray-50 rounded-b-2xl flex justify-end gap-3">
            <button onClick={onClose} className="px-5 py-2.5 text-gray-600 font-semibold hover:bg-gray-200 rounded-lg transition-colors">
                Cancelar
            </button>
            <button type="submit" form="edit-form" className={`px-5 py-2.5 text-white font-bold rounded-lg shadow-lg hover:shadow-xl transition-all flex items-center gap-2 ${isEditing ? 'bg-blue-600 hover:bg-blue-700' : 'bg-green-600 hover:bg-green-700'}`}>
                <Save className="w-4 h-4" /> {isEditing ? 'Guardar Cambios' : 'Registrar Ahora'}
            </button>
        </div>
      </div>
    </div>
  );
};

export default EditModal;
