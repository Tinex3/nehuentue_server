import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { useAuthStore } from './stores/authStore';
import {
  Login,
  Register,
  Dashboard,
  Zones,
  Devices,
  Events,
  Evidences,
  Measurements,
} from './pages';

const PrivateRoute = ({ children }: { children: React.ReactNode }) => {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
  return isAuthenticated ? <>{children}</> : <Navigate to="/login" />;
};

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        
        <Route
          path="/dashboard"
          element={
            <PrivateRoute>
              <Dashboard />
            </PrivateRoute>
          }
        />
        
        <Route
          path="/zones"
          element={
            <PrivateRoute>
              <Zones />
            </PrivateRoute>
          }
        />
        
        <Route
          path="/devices"
          element={
            <PrivateRoute>
              <Devices />
            </PrivateRoute>
          }
        />
        
        <Route
          path="/events"
          element={
            <PrivateRoute>
              <Events />
            </PrivateRoute>
          }
        />
        
        <Route
          path="/evidences"
          element={
            <PrivateRoute>
              <Evidences />
            </PrivateRoute>
          }
        />
        
        <Route
          path="/measurements"
          element={
            <PrivateRoute>
              <Measurements />
            </PrivateRoute>
          }
        />
        
        <Route path="/" element={<Navigate to="/dashboard" />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
