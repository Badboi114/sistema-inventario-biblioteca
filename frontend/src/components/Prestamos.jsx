import { useState, useEffect } from 'react';
import axios from 'axios';
import { Search, User, BookOpen, CheckCircle, Clock, AlertTriangle, Plus, X, FileText, PenTool, Save, Hash } from 'lucide-react';
import Swal from 'sweetalert2';

const Prestamos = () => {
  const [prestamos, setPrestamos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [busqueda, setBusqueda] = useState('');
  const [modalOpen, setModalOpen] = useState(false);
  
  // Datos del formulario
  const [tipoPrestamo, setTipoPrestamo] = useState('SALA');
  const [observaciones, setObservaciones] = useState('');
  const [requisitosVerificados, setRequisitosVerificados] = useState(false);

  // ESTADOS INTELIGENTES PARA ESTUDIANTE
  const [ciInput, setCiInput] = useState('');      // Lo que el usuario escribe en CI
  const [nombreInput, setNombreInput] = useState(''); // Lo que el usuario escribe en Nombre
  const [estudianteEncontrado, setEstudianteEncontrado] = useState(null); // Si hallamos uno existente

  // Buscador Libro
  const [busquedaLibro, setBusquedaLibro] = useState('');
  const [libroSeleccionado, setLibroSeleccionado] = useState(null);
  
  // Catálogos
  const [estudiantesDisponibles, setEstudiantesDisponibles] = useState([]);
  const [librosDisponibles, setLibrosDisponibles] = useState([]);

  // Cargar lista inicial de préstamos
  const fetchPrestamos = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const res = await axios.get(`http://127.0.0.1:8000/api/prestamos/?search=${busqueda}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setPrestamos(res.data);
    } catch (error) { console.error(error); }
    setLoading(false);
  };

  // Cargar catálogos para los buscadores
  const cargarCatalogos = async () => {
      const token = localStorage.getItem('token');
      const config = { headers: { Authorization: `Bearer ${token}` } };
      
      try {
        const [resEst, resLib] = await Promise.all([
            axios.get('http://127.0.0.1:8000/api/estudiantes/', config),
            axios.get('http://127.0.0.1:8000/api/activos/', config)
        ]);
        setEstudiantesDisponibles(resEst.data);
        setLibrosDisponibles(resLib.data);
      } catch (error) { console.error("Error cargando catálogos", error); }
  };

  useEffect(() => { fetchPrestamos(); }, [busqueda]);

  // --- MAGIA: DETECTAR SI EL ESTUDIANTE YA EXISTE AL ESCRIBIR EL CI ---
  useEffect(() => {
      if (!ciInput) {
          setEstudianteEncontrado(null);
          setNombreInput('');
          return;
      }

      // Buscamos en la lista local si el CI coincide
      const encontrado = estudiantesDisponibles.find(e => e.ci.trim() === ciInput.trim());

      if (encontrado) {
          // ¡ENCONTRADO! Rellenamos todo
          setEstudianteEncontrado(encontrado);
          setNombreInput(encontrado.nombre_completo);
      } else {
          // NO ENCONTRADO
          // Truco: Solo borramos el nombre si ANTES teníamos a alguien seleccionado.
          // Esto evita que se borre el nombre mientras escribes uno nuevo,
          // pero SÍ lo borra si pasaste de un carnet válido (123) a uno nuevo (1234).
          if (estudianteEncontrado) {
              setNombreInput('');
              setEstudianteEncontrado(null);
          }
          // Si nunca hubo nadie seleccionado (estás creando uno desde cero), no borramos nada.
      }
  }, [ciInput, estudiantesDisponibles, estudianteEncontrado]);

  // Resetear modal al abrir
  const abrirModal = () => {
      setModalOpen(true);
      setCiInput('');
      setNombreInput('');
      setEstudianteEncontrado(null);
      setLibroSeleccionado(null);
      setTipoPrestamo('SALA');
      setRequisitosVerificados(false);
      setBusquedaLibro('');
      setObservaciones('');
      cargarCatalogos();
  };

  const handleCrearPrestamo = async (e) => {
      e.preventDefault();
      
      if (!ciInput || !nombreInput || !libroSeleccionado) {
          Swal.fire('Faltan datos', 'Ingresa CI, Nombre y selecciona un Libro.', 'warning');
          return;
      }

      try {
          const token = localStorage.getItem('token');
          const payload = {
              activo: libroSeleccionado.id,
              tipo: tipoPrestamo,
              observaciones: observaciones
          };
          
          // Si encontramos uno existente, mandamos su ID. Si no, mandamos datos para crear
          if (estudianteEncontrado) {
              payload.estudiante = estudianteEncontrado.id;
          } else {
              payload.nuevo_nombre = nombreInput;
              payload.nuevo_ci = ciInput;
              // nuevo_carrera: NO SE ENVÍA (El backend pondrá "No especificada")
          }
          
          await axios.post('http://127.0.0.1:8000/api/prestamos/', payload, {
              headers: { Authorization: `Bearer ${token}` }
          });
          
          Swal.fire({
              title: '¡Listo!',
              text: estudianteEncontrado ? 'Préstamo registrado.' : 'Estudiante nuevo registrado y préstamo creado.',
              icon: 'success',
              timer: 2000
          });
          setModalOpen(false);
          fetchPrestamos();
      } catch (error) {
          console.error('Error:', error);
          const errorMsg = error.response?.data?.error || 
                          error.response?.data?.tipo?.[0] || 
                          'Error al registrar el préstamo.';
          Swal.fire('Atención', String(errorMsg), 'error');
      }
  };

  const handleDevolucion = async (id) => {
      try {
          const token = localStorage.getItem('token');
          const res = await axios.post(`http://127.0.0.1:8000/api/prestamos/${id}/devolver/`, {}, {
             headers: { Authorization: `Bearer ${token}` }
          });
          Swal.fire('Libro Devuelto', 'Entrega el documento de garantía al estudiante.', 'success');
          fetchPrestamos();
      } catch (error) { console.error(error); }
  };

  // --- FILTRADO MEJORADO ---
  
  // Filtrar libros por Título o CÓDIGO (Prioridad al código)
  const librosFiltrados = busquedaLibro.length > 0
      ? librosDisponibles.filter(l => {
          const termino = busquedaLibro.toLowerCase();
          const codigo = l.codigo_nuevo ? l.codigo_nuevo.toLowerCase() : '';
          const titulo = l.titulo.toLowerCase();
          
          // Busca coincidencia en código o título
          return codigo.includes(termino) || titulo.includes(termino);
        }).slice(0, 10) // Aumentamos a 10 sugerencias para mayor visibilidad
      : [];

  const formatFecha = (fecha) => {
    return new Date(fecha).toLocaleDateString('es-BO', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 relative min-h-[80vh]">
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-gray-800 flex items-center gap-2">
            <Clock className="text-orange-500" /> Circulación y Préstamos
        </h2>
        <button onClick={abrirModal} className="bg-blue-600 text-white px-4 py-2 rounded-lg font-bold flex items-center hover:bg-blue-700 shadow-lg transition-all">
            <Plus className="w-5 h-5 mr-2" /> Nuevo Préstamo
        </button>
      </div>

      {/* Buscador */}
      <div className="mb-4 relative">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
        <input
          type="text"
          placeholder="Buscar préstamos..."
          value={busqueda}
          onChange={(e) => setBusqueda(e.target.value)}
          className="w-full pl-10 pr-4 py-2 border rounded-lg outline-none focus:ring-2 focus:ring-orange-500"
        />
      </div>

      {/* Tabla de Préstamos */}
      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse">
            <thead>
                <tr className="bg-gray-50 text-gray-700 text-xs uppercase border-b font-bold">
                    <th className="p-4">Estudiante / Identificación</th>
                    <th className="p-4">Material Prestado (Código)</th>
                    <th className="p-4">Tipo / Garantía</th>
                    <th className="p-4">Fechas</th>
                    <th className="p-4">Estado</th>
                    <th className="p-4 text-center">Acción</th>
                </tr>
            </thead>
            <tbody className="divide-y divide-gray-100 text-sm">
                {loading ? (
                  <tr><td colSpan="5" className="p-8 text-center text-gray-500">Cargando...</td></tr>
                ) : prestamos.length === 0 ? (
                  <tr><td colSpan="5" className="p-8 text-center text-gray-400">No hay préstamos registrados.</td></tr>
                ) : (
                  prestamos.map((p) => {
                    const vencido = new Date() > new Date(p.fecha_devolucion_estimada) && p.estado === 'VIGENTE';
                    return (
                    <tr key={p.id} className={p.estado === 'DEVUELTO' ? 'bg-gray-50 opacity-60' : 'hover:bg-blue-50'}>
                        <td className="p-4">
                            <div className="font-bold text-gray-800">{p.estudiante_nombre}</div>
                            <div className="text-xs text-gray-500 font-mono flex gap-2">
                                {p.estudiante?.carnet_universitario && <span>CU: {p.estudiante.carnet_universitario}</span>}
                                <span>CI: {p.estudiante?.ci || 'S/D'}</span>
                            </div> 
                            <div className="text-xs text-blue-600">{p.estudiante_carrera}</div>
                        </td>
                        <td className="p-4">
                            <div className="flex items-center gap-2">
                                <span className={`px-1.5 py-0.5 rounded text-[10px] font-bold border ${p.activo_tipo === 'TESIS' ? 'bg-green-100 text-green-700 border-green-200' : 'bg-blue-100 text-blue-700 border-blue-200'}`}>
                                    {p.activo_tipo || 'LIBRO'}
                                </span>
                                <span className="font-mono text-sm font-bold text-gray-800 bg-yellow-100 px-1 rounded">{p.activo_codigo || 'S/C'}</span>
                            </div>
                            <div className="text-xs text-gray-600 truncate w-64 mt-1" title={p.activo_titulo}>{p.activo_titulo}</div>
                        </td>
                        <td className="p-4">
                            <span className={`px-2 py-1 rounded-full text-xs font-bold ${p.tipo === 'SALA' ? 'bg-purple-100 text-purple-700' : 'bg-orange-100 text-orange-700'}`}>
                                {p.tipo}
                            </span>
                            <div className="text-[10px] mt-1 text-gray-500 font-bold">
                                {p.tipo === 'SALA' ? 'Deja Carnet Univ.' : 'Deja C.I.'}
                            </div>
                        </td>
                        <td className="p-4 text-xs">
                            <div>Salida: {new Date(p.fecha_prestamo).toLocaleDateString()}</div>
                            <div className={`font-bold ${new Date() > new Date(p.fecha_devolucion_estimada) && p.estado !== 'DEVUELTO' ? 'text-red-600' : 'text-green-600'}`}>
                                Límite: {new Date(p.fecha_devolucion_estimada).toLocaleDateString()}
                            </div>
                        </td>
                        <td className="p-4">
                            {p.estado === 'VIGENTE' && <span className="text-green-600 font-bold flex items-center gap-1"><Clock className="w-3 h-3" /> Activo</span>}
                            {p.estado === 'DEVUELTO' && <span className="text-gray-500 font-bold flex items-center gap-1"><CheckCircle className="w-3 h-3" /> Cerrado</span>}
                        </td>
                        <td className="p-4 text-center">
                            {p.estado !== 'DEVUELTO' && (
                                <button 
                                    onClick={() => handleDevolucion(p.id)} 
                                    className="bg-green-500 hover:bg-green-600 text-white px-3 py-1.5 rounded-lg text-xs font-bold shadow-sm transition-all flex items-center gap-1 mx-auto"
                                >
                                    <CheckCircle className="w-3 h-3" /> DEVOLVER
                                </button>
                            )}
                        </td>
                    </tr>
                )}))}
                {prestamos.length === 0 && <tr><td colSpan="6" className="p-8 text-center text-gray-400">No hay préstamos registrados.</td></tr>}
            </tbody>
        </table>
      </div>

      {/* ================= MODAL DE NUEVO PRÉSTAMO ================= */}
      {modalOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-70 backdrop-blur-sm flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-2xl w-full max-w-2xl shadow-2xl flex flex-col max-h-[90vh]">
                {/* Header Modal */}
                <div className="p-6 border-b bg-blue-50 rounded-t-2xl flex justify-between items-center">
                    <div>
                        <h3 className="text-xl font-bold text-blue-900 flex items-center gap-2">
                            <PenTool className="w-5 h-5" /> Registrar Salida
                        </h3>
                        <p className="text-sm text-blue-600">Busca un estudiante o regístralo al instante.</p>
                    </div>
                    <button onClick={() => setModalOpen(false)} className="p-2 hover:bg-blue-100 rounded-full transition-colors text-blue-800">
                        <X className="w-6 h-6" />
                    </button>
                </div>

                <div className="p-6 overflow-y-auto space-y-6">
                    
                    {/* 1. DATOS DEL ESTUDIANTE (Autodetección por CI) */}
                    <div className="space-y-3">
                        <label className="block text-xs font-bold text-gray-500 uppercase">1. Estudiante</label>
                        
                        {/* Input CI */}
                        <div className="relative">
                            <Hash className="absolute left-3 top-2.5 w-4 h-4 text-gray-400" />
                            <input 
                                type="text"
                                className={`w-full pl-10 pr-4 py-2 border-2 rounded-xl outline-none focus:ring-2 transition-all ${
                                    estudianteEncontrado 
                                        ? 'border-green-400 bg-green-50 focus:border-green-500 focus:ring-green-100' 
                                        : 'border-gray-200 bg-gray-50 focus:border-blue-500 focus:ring-blue-100'
                                }`}
                                placeholder="Carnet Universitario / C.I. del Estudiante"
                                value={ciInput}
                                onChange={(e) => setCiInput(e.target.value)}
                                autoFocus
                            />
                        </div>

                        {/* Input Nombre */}
                        <div className="relative">
                            <User className="absolute left-3 top-2.5 w-4 h-4 text-gray-400" />
                            <input 
                                type="text"
                                className={`w-full pl-10 pr-4 py-2 border-2 rounded-xl outline-none transition-all ${
                                    estudianteEncontrado 
                                        ? 'border-green-400 bg-green-50 text-green-900 cursor-not-allowed' 
                                        : 'border-gray-200 bg-gray-50 focus:border-blue-500 focus:ring-2 focus:ring-blue-100'
                                }`}
                                placeholder="Nombre Completo del Estudiante"
                                value={nombreInput}
                                onChange={(e) => setNombreInput(e.target.value)}
                                readOnly={!!estudianteEncontrado}
                            />
                            {estudianteEncontrado && (
                                <span className="absolute right-3 top-2.5 flex items-center gap-1 text-xs font-bold text-green-600">
                                    <CheckCircle className="w-3 h-3" /> Registrado
                                </span>
                            )}
                        </div>

                        {!estudianteEncontrado && ciInput && (
                            <p className="text-xs text-amber-600 flex items-center gap-1">
                                <AlertTriangle className="w-3 h-3" /> 
                                Estudiante nuevo • Se registrará automáticamente
                            </p>
                        )}
                    </div>

                    {/* 2. BUSCADOR DE LIBRO/TESIS */}
                    <div className="relative">
                        <label className="block text-xs font-bold text-gray-500 uppercase mb-1">2. Material (Código o Título)</label>
                        {!libroSeleccionado ? (
                            <>
                                <div className="flex items-center border-2 border-gray-200 rounded-xl p-2 focus-within:border-blue-500 focus-within:ring-2 focus-within:ring-blue-100 transition-all bg-gray-50">
                                    <BookOpen className="w-5 h-5 text-gray-400 mr-2" />
                                    <input 
                                        type="text" 
                                        className="w-full bg-transparent outline-none text-gray-700 placeholder-gray-400"
                                        placeholder="Ej: S1-R1-0039 o Álgebra..."
                                        value={busquedaLibro}
                                        onChange={(e) => setBusquedaLibro(e.target.value)}
                                    />
                                </div>
                                {librosFiltrados.length > 0 && (
                                    <div className="absolute top-full left-0 right-0 bg-white border rounded-xl shadow-xl mt-2 z-20 overflow-hidden max-h-60 overflow-y-auto">
                                        {librosFiltrados.map(l => (
                                            <div 
                                                key={l.id} 
                                                className="p-3 hover:bg-blue-50 cursor-pointer border-b last:border-0 transition-colors"
                                                onClick={() => { 
                                                    setLibroSeleccionado(l); 
                                                    setBusquedaLibro('');
                                                    if(l.tipo === 'TESIS') {
                                                        setTipoPrestamo('SALA');
                                                        Swal.fire({ toast: true, position: 'center', icon: 'info', title: 'Las tesis solo se prestan en SALA', timer: 3000, showConfirmButton: false });
                                                    }
                                                }}
                                            >
                                                {/* Encabezado: Tipo + Código */}
                                                <div className="flex justify-between items-start mb-1">
                                                    <span className={`text-[10px] font-bold px-2 py-0.5 rounded border ${
                                                        l.tipo === 'TESIS' 
                                                            ? 'bg-green-100 text-green-700 border-green-200' 
                                                            : 'bg-blue-100 text-blue-700 border-blue-200'
                                                    }`}>
                                                        {l.tipo}
                                                    </span>
                                                    <span className="font-mono text-xs font-bold text-gray-600 bg-gray-100 px-2 rounded">
                                                        {l.codigo_nuevo || 'SIN CÓDIGO'}
                                                    </span>
                                                </div>
                                                
                                                {/* Título */}
                                                <div className="font-bold text-gray-800 text-sm leading-tight mb-1">
                                                    {l.titulo}
                                                </div>
                                                
                                                {/* Autor */}
                                                <div className="text-xs text-gray-500 mt-1 flex items-center gap-1">
                                                    <User className="w-3 h-3" /> {l.autor || 'Sin Autor'}
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                )}
                            </>
                        ) : (
                            <div className="flex items-center justify-between bg-blue-50 border border-blue-200 p-3 rounded-xl animate-fade-in">
                                <div className="flex-1 min-w-0">
                                    {/* Código + Tipo */}
                                    <div className="flex items-center gap-2 mb-1">
                                        <span className="font-mono font-bold text-blue-900 bg-white px-2 rounded text-sm border border-blue-100">
                                            {libroSeleccionado.codigo_nuevo || 'S/C'}
                                        </span>
                                        <span className="text-[10px] font-bold text-blue-600 border border-blue-200 px-1 rounded">
                                            {libroSeleccionado.tipo}
                                        </span>
                                    </div>
                                    {/* Título */}
                                    <div className="text-xs text-gray-700 font-medium truncate">
                                        {libroSeleccionado.titulo}
                                    </div>
                                    {/* Autor */}
                                    <div className="text-[10px] text-gray-500 mt-1 flex items-center gap-1">
                                        <User className="w-3 h-3" /> {libroSeleccionado.autor || 'Sin Autor'}
                                    </div>
                                </div>
                                <button 
                                    onClick={() => setLibroSeleccionado(null)} 
                                    className="text-red-500 hover:bg-red-50 p-2 rounded-full transition-colors ml-2"
                                >
                                    <X className="w-4 h-4" />
                                </button>
                            </div>
                        )}
                    </div>

                    {/* 3. TIPO Y REQUISITOS (ALERTA VISUAL) */}
                    <div className="bg-yellow-50 border-2 border-yellow-200 p-4 rounded-xl">
                        <label className="block text-xs font-bold text-yellow-800 uppercase mb-3 text-center">3. Tipo de Préstamo y Requisito</label>
                        
                        <div className="grid grid-cols-2 gap-4 mb-4">
                            <button 
                                type="button"
                                onClick={() => setTipoPrestamo('SALA')}
                                className={`p-3 rounded-lg border-2 transition-all text-center ${tipoPrestamo === 'SALA' ? 'border-purple-500 bg-purple-100 text-purple-800 ring-2 ring-purple-200' : 'border-gray-300 hover:bg-white'}`}
                            >
                                <div className="font-bold">EN SALA</div>
                                <div className="text-[10px] mt-1">Devuelve HOY</div>
                            </button>

                            <button 
                                type="button"
                                disabled={libroSeleccionado?.tipo === 'TESIS'}
                                onClick={() => setTipoPrestamo('DOMICILIO')}
                                className={`p-3 rounded-lg border-2 transition-all text-center 
                                    ${tipoPrestamo === 'DOMICILIO' ? 'border-orange-500 bg-orange-100 text-orange-800 ring-2 ring-orange-200' : 'border-gray-300 hover:bg-white'}
                                    ${libroSeleccionado?.tipo === 'TESIS' ? 'opacity-40 cursor-not-allowed' : ''}
                                `}
                            >
                                <div className="font-bold">DOMICILIO</div>
                                <div className="text-[10px] mt-1">{libroSeleccionado?.tipo === 'TESIS' ? '🚫 NO PERMITIDO' : 'Devuelve en 2 DÍAS'}</div>
                            </button>
                        </div>

                        {/* INSTRUCCIÓN OBLIGATORIA */}
                        <div className="flex items-start gap-3 bg-white p-3 rounded-lg border-2 border-yellow-300">
                            <FileText className="w-8 h-8 text-yellow-600 flex-shrink-0" />
                            <div>
                                <p className="font-bold text-gray-800 text-sm">GARANTÍA REQUERIDA:</p>
                                <p className="text-sm text-gray-700 mt-1">
                                    Debes retener el <span className="font-bold text-red-600 underline">{tipoPrestamo === 'SALA' ? 'CARNET UNIVERSITARIO' : 'CÉDULA DE IDENTIDAD (C.I.)'}</span> del estudiante como garantía y solicitar su <span className="font-bold text-red-600">FIRMA</span> en el registro físico.
                                </p>
                            </div>
                        </div>
                    </div>

                    {/* Observaciones */}
                    <div>
                        <label className="block text-xs font-bold text-gray-500 uppercase mb-1">
                            Observaciones (opcional)
                        </label>
                        <textarea
                            value={observaciones}
                            onChange={(e) => setObservaciones(e.target.value)}
                            className="w-full p-2 border rounded-lg outline-none focus:border-blue-500"
                            rows="2"
                            placeholder="Notas adicionales..."
                        />
                    </div>

                    {/* CHECKBOX DE SEGURIDAD */}
                    <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg border-2 border-gray-200">
                        <input 
                            type="checkbox" 
                            id="check-seguridad" 
                            className="w-5 h-5 text-blue-600 rounded focus:ring-blue-500 cursor-pointer"
                            checked={requisitosVerificados}
                            onChange={(e) => setRequisitosVerificados(e.target.checked)}
                        />
                        <label htmlFor="check-seguridad" className="text-sm font-bold text-gray-700 cursor-pointer select-none">
                            ✓ Confirmo que recibí el documento y el estudiante firmó
                        </label>
                    </div>

                </div>

                {/* Footer Buttons */}
                <div className="p-6 border-t bg-gray-50 rounded-b-2xl flex justify-end gap-3">
                    <button onClick={() => setModalOpen(false)} className="px-5 py-2.5 text-gray-600 font-semibold hover:bg-gray-200 rounded-lg transition-colors">Cancelar</button>
                    <button 
                        onClick={handleCrearPrestamo} 
                        disabled={!ciInput || !nombreInput || !libroSeleccionado || !requisitosVerificados}
                        className={`px-5 py-2.5 text-white font-bold rounded-lg shadow-lg flex items-center gap-2 transition-all
                            ${(!ciInput || !nombreInput || !libroSeleccionado || !requisitosVerificados) 
                                ? 'bg-gray-400 cursor-not-allowed' 
                                : 'bg-blue-600 hover:bg-blue-700 hover:shadow-xl'}`}
                    >
                        <Save className="w-5 h-5" /> Registrar Préstamo
                    </button>
                </div>
            </div>
        </div>
      )}
    </div>
  );
};

export default Prestamos;
