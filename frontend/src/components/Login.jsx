import { useState } from 'react';
import axios from 'axios';
import { Lock, User, KeyRound } from 'lucide-react';

const Login = ({ onLogin }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      // Pedimos el token al backend
      const response = await axios.post('http://127.0.0.1:8000/api/token/', {
        username,
        password
      });
      
      // Si las credenciales son correctas:
      const token = response.data.access;
      // 1. Guardamos el token en el navegador
      localStorage.setItem('token', token);
      // 2. Configuramos axios para usarlo en el futuro
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      // 3. Avisamos a la App que ya entramos
      onLogin();

    } catch (err) {
      console.error(err);
      setError('Usuario o contraseña incorrectos.');
    }
    setLoading(false);
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100 p-4">
      <div className="bg-white p-8 rounded-2xl shadow-xl w-full max-w-md border border-gray-200">
        <div className="text-center mb-8">
          <div className="bg-primary w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4 text-white shadow-lg">
            <Lock className="w-8 h-8" />
          </div>
          <h2 className="text-2xl font-bold text-gray-800">Acceso Restringido</h2>
          <p className="text-gray-500 text-sm mt-2">Sistema de Inventario Bibliotecario</p>
        </div>

        {error && (
          <div className="bg-red-50 text-red-600 p-3 rounded-lg mb-6 text-sm text-center border border-red-200 flex items-center justify-center">
            <KeyRound className="w-4 h-4 mr-2" /> {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Usuario Administrador</label>
            <div className="relative">
              <User className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <input
                type="text"
                required
                className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition-all"
                placeholder="Ej: admin"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Contraseña</label>
            <div className="relative">
              <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <input
                type="password"
                required
                className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition-all"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className={`w-full py-3 rounded-lg text-white font-bold shadow-md transition-colors
              ${loading ? 'bg-gray-400 cursor-not-allowed' : 'bg-primary hover:bg-blue-800'}`}
          >
            {loading ? 'Verificando...' : 'INGRESAR AL SISTEMA'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default Login;
