import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'sonner';
import { useAuthStore } from './store/authStore';

// Layout & Pages
import MainLayout from './layouts/MainLayout';
import LoginPage from './pages/LoginPage';
import Dashboard from './pages/Dashboard';
import StrategicMap from './pages/StrategicMap';
import DiagnosticsCenter from './pages/DiagnosticsCenter';
import TacticalAlerts from './pages/TacticalAlerts';
import SimulationLab from './pages/SimulationLab';

// Protected Route Wrapper
const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const { isAuthenticated } = useAuthStore();
  if (!isAuthenticated) return <Navigate to="/login" replace />;
  return <>{children}</>;
};

export default function App() {
  return (
    <BrowserRouter>
      <Toaster position="top-right" richColors />
      <Routes>
        <Route path="/login" element={<LoginPage />} />

        {/* Protected Routes inside MainLayout */}
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <MainLayout />
            </ProtectedRoute>
          }
        >
          <Route index element={<Dashboard />} />
          <Route path="map" element={<StrategicMap />} />
          <Route path="diagnostics" element={<DiagnosticsCenter />} />
          <Route path="alerts" element={<TacticalAlerts />} />
          <Route path="simulations" element={<SimulationLab />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
