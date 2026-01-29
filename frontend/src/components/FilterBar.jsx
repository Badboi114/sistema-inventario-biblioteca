import { useState } from 'react';
import { Filter, X, RotateCcw } from 'lucide-react';

const FilterBar = ({ type, onFilterApply }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [activeCount, setActiveCount] = useState(0);
  
  // Estado inicial dinámico
  const initialState = type === 'libros' ? {
    codigo_nuevo__icontains: '',
    titulo__icontains: '',
    materia__icontains: '',
    ubicacion_seccion: '',
    anio: '',
    estado: ''
  } : {
    codigo_nuevo__icontains: '',
    titulo__icontains: '',
    autor__icontains: '',
    carrera__icontains: '',
    tutor__icontains: '',
    modalidad: '',
    anio: '',
    estado: ''
  };

  const [filters, setFilters] = useState(initialState);

  const handleChange = (e) => {
    setFilters({ ...filters, [e.target.name]: e.target.value });
  };

  const handleReset = () => {
    setFilters(initialState);
    setActiveCount(0);
    onFilterApply({}); // Limpia en el padre
    setIsOpen(false);
  };

  const handleApply = (e) => {
    e.preventDefault();
    // Contar cuántos filtros tienen texto
    const count = Object.values(filters).filter(val => val !== '').length;
    setActiveCount(count);
    
    // Enviar solo los filtros que tienen valor
    const cleanFilters = {};
    Object.keys(filters).forEach(key => {
      if (filters[key]) cleanFilters[key] = filters[key];
    });
    
    onFilterApply(cleanFilters);
    setIsOpen(false);
  };

  // Lógica del botón de color
  const buttonColor = activeCount > 0 ? 'bg-red-500 hover:bg-red-600' : 'bg-blue-900 hover:bg-blue-950';
  const buttonText = activeCount > 0 ? 'Reiniciar Filtros' : 'Filtros Avanzados';

  return (
    <div className="relative">
      {/* Botón Principal */}
      <button
        onClick={() => activeCount > 0 ? handleReset() : setIsOpen(!isOpen)}
        className={`${buttonColor} text-white px-4 py-2 rounded-lg flex items-center gap-2 transition-all shadow-sm font-medium`}
      >
        {activeCount > 0 ? <RotateCcw className="w-4 h-4" /> : <Filter className="w-4 h-4" />}
        {buttonText}
        {activeCount > 0 && <span className="bg-white text-red-500 text-xs px-1.5 rounded-full font-bold">{activeCount}</span>}
      </button>

      {/* Menú Desplegable */}
      {isOpen && activeCount === 0 && (
        <div className="absolute right-0 top-12 w-80 bg-white p-5 rounded-xl shadow-2xl border border-gray-200 z-50">
          <div className="flex justify-between items-center mb-4 border-b pb-2">
            <h3 className="font-bold text-gray-700">Filtrar {type === 'libros' ? 'Libros' : 'Tesis'}</h3>
            <button onClick={() => setIsOpen(false)} className="text-gray-400 hover:text-gray-600"><X className="w-5 h-5" /></button>
          </div>

          <form onSubmit={handleApply} className="space-y-3">
            {/* CAMPOS COMUNES */}
            <div>
                <label className="text-xs font-bold text-gray-500 uppercase">Código</label>
                <input name="codigo_nuevo__icontains" value={filters.codigo_nuevo__icontains} onChange={handleChange} placeholder="Ej: IND-001" className="w-full p-2 border rounded text-sm focus:ring-2 focus:ring-primary" />
            </div>
            
            <div>
                <label className="text-xs font-bold text-gray-500 uppercase">Título</label>
                <input name="titulo__icontains" value={filters.titulo__icontains} onChange={handleChange} placeholder="Palabra clave..." className="w-full p-2 border rounded text-sm focus:ring-2 focus:ring-primary" />
            </div>

            {/* CAMPOS ESPECÍFICOS LIBROS */}
            {type === 'libros' && (
              <>
                <div>
                    <label className="text-xs font-bold text-gray-500 uppercase">Materia</label>
                    <input name="materia__icontains" value={filters.materia__icontains} onChange={handleChange} placeholder="Ej: Calculo" className="w-full p-2 border rounded text-sm focus:ring-2 focus:ring-primary" />
                </div>
                <div>
                    <label className="text-xs font-bold text-gray-500 uppercase">Ubicación (Sección)</label>
                    <input name="ubicacion_seccion" value={filters.ubicacion_seccion} onChange={handleChange} placeholder="Ej: SECCION 1" className="w-full p-2 border rounded text-sm focus:ring-2 focus:ring-primary" />
                </div>
                <div>
                    <label className="text-xs font-bold text-gray-500 uppercase">Año</label>
                    <input name="anio" value={filters.anio} onChange={handleChange} placeholder="Ej: 2020" className="w-full p-2 border rounded text-sm focus:ring-2 focus:ring-primary" type="number" min="1900" max="2100" />
                </div>
              </>
            )}

            {/* CAMPOS ESPECÍFICOS TESIS */}
            {type === 'tesis' && (
              <>
                <div className="grid grid-cols-2 gap-2">
                  <div>
                    <label className="text-xs font-bold text-gray-500 uppercase">Carrera</label>
                    <input name="carrera__icontains" value={filters.carrera__icontains} onChange={handleChange} className="w-full p-2 border rounded text-sm" />
                  </div>
                  <div>
                    <label className="text-xs font-bold text-gray-500 uppercase">Tutor</label>
                    <input name="tutor__icontains" value={filters.tutor__icontains} onChange={handleChange} className="w-full p-2 border rounded text-sm" />
                  </div>
                </div>
                <div>
                  <label className="text-xs font-bold text-gray-500 uppercase">Modalidad</label>
                  <select name="modalidad" value={filters.modalidad} onChange={handleChange} className="w-full p-2 border rounded text-sm bg-white">
                    <option value="">Todas</option>
                    <option value="TESIS">Tesis</option>
                    <option value="PROYECTO DE GRADO">Proyecto de Grado</option>
                    <option value="TRABAJO DIRIGIDO">Trabajo Dirigido</option>
                  </select>
                </div>
                <div>
                  <label className="text-xs font-bold text-gray-500 uppercase">Año</label>
                  <input name="anio" value={filters.anio} onChange={handleChange} placeholder="Ej: 2020" className="w-full p-2 border rounded text-sm focus:ring-2 focus:ring-primary" type="number" min="1900" max="2100" />
                </div>
              </>
            )}

            {/* ESTADO (COMÚN) */}
            <div>
                <label className="text-xs font-bold text-gray-500 uppercase">Estado</label>
                <select name="estado" value={filters.estado} onChange={handleChange} className="w-full p-2 border rounded text-sm bg-white">
                    <option value="">Todos</option>
                    <option value="BUENO">Bueno</option>
                    <option value="REGULAR">Regular</option>
                    <option value="MALO">Malo</option>
                </select>
            </div>

            <button type="submit" className="w-full bg-primary text-white py-2 rounded-lg font-bold hover:bg-blue-800 mt-4">
                Aplicar Filtros
            </button>
          </form>
        </div>
      )}
    </div>
  );
};

export default FilterBar;
