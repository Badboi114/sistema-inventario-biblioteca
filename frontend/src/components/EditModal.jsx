import { useState, useEffect } from 'react';
import axios from 'axios';
import { X, Save, AlertCircle, PlusCircle, MapPin, Hash } from 'lucide-react';

const EditModal = ({ isOpen, onClose, item, type, onSave }) => {
  const [formData, setFormData] = useState({});
  const [error, setError] = useState('');
  
  // Estados para la lógica de secciones inteligentes
  const [seccionesDisponibles, setSeccionesDisponibles] = useState([]);
  const [prefijoSeccion, setPrefijoSeccion] = useState(''); // Ej: S1-R1 para libros, ADM para tesis

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
            
            // Extraer prefijo si existe código
            if (type === 'libros' && cleanItem.codigo_seccion_full) {
                const partes = cleanItem.codigo_seccion_full.split('-');
                if (partes.length >= 3) {
                    setPrefijoSeccion(`${partes[0]}-${partes[1]}`);
                }
            } else if (type === 'tesis' && cleanItem.codigo_nuevo) {
                const match = cleanItem.codigo_nuevo.match(/^([A-Z]+)/);
                if (match) {
                    setPrefijoSeccion(match[1]);
                }
            }
        } else {
            // MODO CREACIÓN: Formulario limpio
            setFormData({}); 
            setPrefijoSeccion('');
        }
        
        // Cargar lista de secciones/prefijos para sugerir (PARA AMBOS TIPOS)
        axios.get(`http://127.0.0.1:8000/api/secciones-disponibles/?tipo=${type}`)
             .then(res => setSeccionesDisponibles(res.data))
             .catch(err => console.error('Error cargando secciones:', err));
    }
  }, [item, isOpen, type]);

  if (!isOpen) return null;

  // --- LÓGICA INTELIGENTE DE SECCIONES/CÓDIGOS ---
  const handlePrefijoChange = async (e) => {
    const nuevoPrefijo = e.target.value.toUpperCase();
    setPrefijoSeccion(nuevoPrefijo);
    
    // Si selecciona un prefijo, pedimos el siguiente número
    if (nuevoPrefijo && !item) { // Solo en modo creación sugerimos
        try {
            const res = await axios.get(`http://127.0.0.1:8000/api/siguiente-codigo/?tipo=${type}&prefijo=${nuevoPrefijo}`);
            if (res.data.siguiente) {
                if (type === 'libros') {
                    // --- LÓGICA BLINDADA PARA SEPARAR S1-R1 ---
                    let seccion = '';
                    let repisa = '';
                    
                    // Solo intentamos dividir si tiene el formato correcto (con guion)
                    if (nuevoPrefijo.includes('-')) {
                        const partes = nuevoPrefijo.split('-');
                        // Parte 1: S1 -> SECCION 1
                        if (partes[0]) {
                            const numeroSeccion = partes[0].replace(/S/i, '');
                            if (numeroSeccion) seccion = `SECCION ${numeroSeccion}`;
                        }
                        // Parte 2: R1 -> REPISA 1
                        if (partes[1]) {
                            const numeroRepisa = partes[1].replace(/R/i, '');
                            if (numeroRepisa) repisa = `REPISA ${numeroRepisa}`;
                        }
                    }

                    setFormData(prev => ({
                        ...prev,
                        codigo_seccion_full: res.data.siguiente,
                        ubicacion_seccion: seccion, // Si falla, queda vacío (no explota)
                        ubicacion_repisa: repisa
                    }));
                } else {
                    // Para Tesis, llenamos el CODIGO NUEVO
                    setFormData(prev => ({
                        ...prev,
                        codigo_nuevo: res.data.siguiente
                    }));
                }
            }
        } catch (error) {
            console.error("Error obteniendo sugerencia:", error);
        }
    }
  };

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

  // Campos dinámicos según tipo
  const fieldsLibros = [
    { name: 'titulo', label: 'Título del Libro', full: true },
    { name: 'autor', label: 'Autor(es)' },
    { name: 'codigo_nuevo', label: 'Código Inventario' },
    { name: 'materia', label: 'Materia' },
    { name: 'editorial', label: 'Editorial' },
    { name: 'edicion', label: 'Edición' },
    { name: 'anio', label: 'Año' },
    { name: 'facultad', label: 'Facultad' },
    { name: 'codigo_antiguo', label: 'Código Antiguo' },
    { name: 'ubicacion_seccion', label: 'Ubicación (Texto)' },
    { name: 'ubicacion_repisa', label: 'Repisa (Texto)' },
    { name: 'estado', label: 'Estado', type: 'select', options: ['BUENO', 'REGULAR', 'MALO', 'EN REPARACION'] },
    { name: 'observaciones', label: 'Observaciones', type: 'textarea' }
  ];

  const fieldsTesis = [
    { name: 'titulo', label: 'Título del Proyecto', full: true },
    { name: 'autor', label: 'Estudiante / Autor' },
    { name: 'tutor', label: 'Tutor Guía' },
    { name: 'carrera', label: 'Carrera' },
    { name: 'facultad', label: 'Facultad' },
    { name: 'anio', label: 'Año' },
    { name: 'modalidad', label: 'Modalidad', type: 'select', options: ['TESIS', 'PROYECTO DE GRADO', 'TRABAJO DIRIGIDO'] },
    { name: 'ubicacion_seccion', label: 'Ubicación' },
    { name: 'estado', label: 'Estado Físico', type: 'select', options: ['BUENO', 'REGULAR', 'MALO', 'EN REPARACION'] }
  ];

  const fields = type === 'libros' ? fieldsLibros : fieldsTesis;

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
                
                {/* ASISTENTE INTELIGENTE (PARA LIBROS Y TESIS) */}
                {!isEditing && (
                    <div className="md:col-span-2 bg-gradient-to-r from-blue-50 to-indigo-50 p-5 rounded-xl border-2 border-blue-200 mb-2 shadow-sm">
                        <label className="block text-sm font-bold text-blue-800 uppercase mb-3 flex items-center gap-2">
                            {type === 'libros' ? <MapPin className="w-5 h-5" /> : <Hash className="w-5 h-5" />}
                            🎯 Asistente Inteligente de {type === 'libros' ? 'Ubicación' : 'Códigos'}
                        </label>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div>
                                <label className="text-xs text-gray-600 font-semibold block mb-2">
                                    1️⃣ {type === 'libros' ? 'Elegir o Escribir Sección (ej: S1-R1)' : 'Elegir Prefijo (ej: ADM)'}
                                </label>
                                <input 
                                    list="secciones-list" 
                                    className="w-full p-3 border-2 border-blue-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white font-semibold text-blue-900"
                                    placeholder={type === 'libros' ? 'Ej: S1-R1, S2-R3...' : 'Ej: ADM, CPU, IND...'}
                                    value={prefijoSeccion}
                                    onChange={handlePrefijoChange}
                                />
                                <datalist id="secciones-list">
                                    {seccionesDisponibles.map(s => <option key={s} value={s} />)}
                                </datalist>
                                <p className="text-xs text-gray-500 mt-1">Selecciona de la lista o escribe {type === 'libros' ? 'una nueva sección' : 'un nuevo prefijo'}</p>
                            </div>
                            <div>
                                <label className="text-xs text-gray-600 font-semibold block mb-2">
                                    2️⃣ Código Generado Automáticamente (Editable)
                                </label>
                                <input 
                                    name={type === 'libros' ? 'codigo_seccion_full' : 'codigo_nuevo'}
                                    value={type === 'libros' ? (formData.codigo_seccion_full || '') : (formData.codigo_nuevo || '')}
                                    onChange={handleChange}
                                    className="w-full p-3 border-2 border-green-300 rounded-lg font-bold text-green-700 text-lg bg-green-50 focus:ring-2 focus:ring-green-500"
                                    placeholder="Se generará automáticamente..."
                                />
                                <p className="text-xs text-gray-500 mt-1">
                                    {(type === 'libros' ? formData.codigo_seccion_full : formData.codigo_nuevo) ? '✅ Código sugerido (puedes editarlo)' : `⏳ Esperando ${type === 'libros' ? 'sección' : 'prefijo'}...`}
                                </p>
                            </div>
                        </div>
                    </div>
                )}

                {/* RESTO DE CAMPOS */}
                {fields.map((field) => (
                    <div key={field.name} className={field.full || field.name === 'observaciones' ? 'md:col-span-2' : ''}>
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
                    ) : field.type === 'textarea' ? (
                        <textarea
                        name={field.name}
                        value={formData[field.name] || ''}
                        onChange={handleChange}
                        rows="3"
                        placeholder="Detalles adicionales..."
                        className="w-full p-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition-all resize-vertical"
                        />
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
