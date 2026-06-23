import React from 'react';
import { Outlet, Link, useLocation, useNavigate } from 'react-router-dom';
import { 
  LayoutDashboard, 
  AlertTriangle, 
  Activity, 
  Settings, 
  LogOut,
  ShieldAlert,
  Menu,
  Stethoscope,
  Map as MapIcon
} from 'lucide-react';
import { useAuthStore } from '../store/authStore';
import { useQueryClient } from '@tanstack/react-query';
import { apiClient } from '../api/client';

const MainLayout: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { logout, user } = useAuthStore();
  const [isSidebarOpen, setSidebarOpen] = React.useState(true);
  const queryClient = useQueryClient();

  const handlePrefetch = (path: string) => {
    if (path === '/') {
      queryClient.prefetchQuery({
        queryKey: ['dashboard-stats'],
        queryFn: async () => {
          const response = await apiClient.get(`/districts/stats`);
          return response.data;
        }
      });
    } else if (path === '/map') {
      queryClient.prefetchQuery({
        queryKey: ['choropleth-data', false, null],
        queryFn: async () => {
          const response = await apiClient.get(`/districts`);
          return response.data;
        }
      });
    } else if (path === '/alerts') {
      queryClient.prefetchQuery({
        queryKey: ['tactical-alerts', false, null],
        queryFn: async () => {
          const response = await apiClient.get(`/alerts`);
          return response.data;
        }
      });
    }
  };

  const navItems = [
    { path: '/', label: 'Command Center', icon: LayoutDashboard },
    { path: '/map', label: 'Strategic Map', icon: MapIcon },
    { path: '/diagnostics', label: 'Clinical Center', icon: Stethoscope },
    { path: '/alerts', label: 'Tactical Alerts', icon: ShieldAlert },
    { path: '/analysis', label: 'Epi Analysis', icon: Activity },
    { path: '/simulations', label: 'Scenario Lab', icon: AlertTriangle },
    { path: '/settings', label: 'System Config', icon: Settings },
  ];

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="flex h-screen bg-[#0a0a0c] text-slate-100 overflow-hidden">
      {/* Sidebar */}
      <aside 
        className={`${
          isSidebarOpen ? 'w-64' : 'w-20'
        } glass-panel border-y-0 border-l-0 transition-all duration-300 flex flex-col z-50`}
      >
        <div className="p-6 flex items-center gap-3">
          <div className="w-8 h-8 bg-brand-primary rounded-lg flex items-center justify-center shadow-[0_0_15px_rgba(30,144,255,0.4)]">
            <ShieldAlert className="w-5 h-5 text-white" />
          </div>
          {isSidebarOpen && (
            <span className="font-bold text-xl tracking-tighter bg-gradient-to-r from-white to-slate-400 bg-clip-text text-transparent">
              EPISENSE
            </span>
          )}
        </div>

        <nav className="flex-1 px-4 py-6 space-y-2">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path;
            return (
              <Link
                key={item.path}
                to={item.path}
                onMouseEnter={() => handlePrefetch(item.path)}
                className={`flex items-center gap-4 px-4 py-3 rounded-xl transition-all duration-200 group ${
                  isActive 
                    ? 'bg-brand-primary/10 text-brand-primary border border-brand-primary/20 shadow-[0_0_15px_rgba(30,144,255,0.1)]' 
                    : 'text-slate-400 hover:text-slate-100 hover:bg-white/[0.03]'
                }`}
              >
                <Icon className={`w-5 h-5 ${isActive ? 'text-brand-primary' : 'group-hover:text-slate-100'}`} />
                {isSidebarOpen && <span className="font-medium text-sm tracking-wide">{item.label}</span>}
              </Link>
            );
          })}
        </nav>

        <div className="p-4 border-t border-white/5 space-y-4">
          {isSidebarOpen && (
            <div className="px-4 py-3 rounded-xl bg-white/[0.02] border border-white/5">
              <p className="text-[10px] uppercase tracking-widest text-slate-500 font-bold mb-1">Authenticated As</p>
              <p className="text-sm font-semibold truncate">{user?.name}</p>
              <p className="text-[11px] text-slate-500 truncate">{user?.role.toUpperCase()}</p>
            </div>
          )}
          <button
            onClick={handleLogout}
            className="w-full flex items-center gap-4 px-4 py-3 rounded-xl text-rose-400 hover:bg-rose-500/10 transition-all group"
          >
            <LogOut className="w-5 h-5" />
            {isSidebarOpen && <span className="font-medium text-sm">Terminate Session</span>}
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {/* Top Header */}
        <header className="h-16 border-b border-white/5 flex items-center justify-between px-8 bg-black/20 backdrop-blur-md">
          <div className="flex items-center gap-4">
            <button 
              onClick={() => setSidebarOpen(!isSidebarOpen)}
              className="p-2 rounded-lg hover:bg-white/5 transition-colors"
            >
              <Menu className="w-5 h-5 text-slate-400" />
            </button>
            <div className="h-4 w-[1px] bg-white/10" />
            <h1 className="text-sm font-medium text-slate-400">
              {navItems.find(i => i.path === location.pathname)?.label || 'System'}
            </h1>
          </div>
          
          <div className="flex items-center gap-6">
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/20">
              <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
              <span className="text-[10px] font-bold text-emerald-500 uppercase tracking-widest">Core Active</span>
            </div>
          </div>
        </header>

        {/* Viewport */}
        <section className="flex-1 overflow-y-auto p-8 relative">
          {/* Subtle Ambient Background Gradients */}
          <div className="absolute top-[-10%] right-[-10%] w-[40%] h-[40%] bg-brand-primary/5 rounded-full blur-[120px] pointer-events-none" />
          <div className="absolute bottom-[-10%] left-[-10%] w-[30%] h-[30%] bg-emerald-500/5 rounded-full blur-[100px] pointer-events-none" />
          
          <div className="max-w-7xl mx-auto">
            <Outlet />
          </div>
        </section>
      </main>
    </div>
  );
};

export default MainLayout;
