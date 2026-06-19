import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'sonner';

import MainLayout from './layouts/MainLayout';
import LoginPage from './pages/LoginPage';
import Dashboard from './pages/Dashboard';
import StrategicMap from './pages/StrategicMap';
import DiagnosticsCenter from './pages/DiagnosticsCenter';
import TacticalAlerts from './pages/TacticalAlerts';
import SimulationLab from './pages/SimulationLab';
import { useAuthStore } from './store/authStore';

const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const { isAuthenticated, token } = useAuthStore();

  if (!isAuthenticated || !token) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
};

export default function App() {
  return (
    <BrowserRouter>
      <Toaster position="top-right" richColors />
      <Routes>
        <Route path="/login" element={<LoginPage />} />

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
          {/* Add a fallback to Dashboard for other paths */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
