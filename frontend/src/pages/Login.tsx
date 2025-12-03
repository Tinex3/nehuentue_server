import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useMutation } from '@tanstack/react-query';
import { authService } from '../services/authService';
import { useAuthStore } from '../stores/authStore';
import { Input } from '../components/ui/Input';
import { Button } from '../components/ui/Button';
import toast from 'react-hot-toast';

export const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const navigate = useNavigate();
  const setAuth = useAuthStore((state) => state.setAuth);

  const loginMutation = useMutation({
    mutationFn: (credentials: { email: string; password: string }) => 
      authService.login(credentials.email, credentials.password),
    onSuccess: (data) => {
      setAuth(data.user, data.access_token, data.refresh_token);
      toast.success('¡Bienvenido!');
      navigate('/dashboard');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.message || 'Error al iniciar sesión');
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    // BYPASS PARA PRUEBAS - Usuario hardcodeado
    if (email === 'benjamin@benjamin.cl' && password === '12345678') {
      const mockUser = {
        user_id: 1,
        username: 'benjamin',
        email: 'benjamin@benjamin.cl',
        created_at: new Date().toISOString(),
      };
      setAuth(mockUser, 'mock-access-token', 'mock-refresh-token');
      toast.success('¡Bienvenido Benjamin!');
      navigate('/dashboard');
      return;
    }
    
    // Login real con API
    loginMutation.mutate({ email, password });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-600 to-purple-700 flex items-center justify-center p-4">
      <div className="bg-white rounded-lg shadow-2xl p-8 w-full max-w-md">
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="text-6xl mb-4">🔐</div>
          <h1 className="text-3xl font-bold text-gray-800 mb-2">IoT Security</h1>
          <p className="text-gray-600">Sistema de Seguridad Inteligente</p>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-6">
          <Input
            type="email"
            label="Correo Electrónico"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="usuario@ejemplo.com"
            required
          />

          <Input
            type="password"
            label="Contraseña"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="••••••••"
            required
          />

          <Button
            type="submit"
            variant="primary"
            size="lg"
            className="w-full"
            isLoading={loginMutation.isPending}
          >
            Iniciar Sesión
          </Button>
        </form>

        {/* Register Link */}
        <div className="mt-6 text-center">
          <p className="text-gray-600">
            ¿No tienes cuenta?{' '}
            <Link to="/register" className="text-blue-600 hover:text-blue-700 font-medium">
              Regístrate aquí
            </Link>
          </p>
        </div>
        
        {/* Test credentials hint */}
        <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
          <p className="text-xs text-yellow-800 text-center">
            <strong>Pruebas:</strong> benjamin@benjamin.cl / 12345678
          </p>
        </div>
      </div>
    </div>
  );
};
