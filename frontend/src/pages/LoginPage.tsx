import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { ShieldAlert, Lock, Mail, Loader2, Eye, EyeOff } from 'lucide-react';
import { toast } from 'sonner';
import { apiClient } from '../api/client';
import { useAuthStore } from '../store/authStore';

const loginSchema = z.object({
  email: z.string().email('Invalid email address'),
  password: z.string().min(8, 'Password must be at least 8 characters'),
});

type LoginForm = z.infer<typeof loginSchema>;

const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const setAuth = useAuthStore((state) => state.setAuth);
  const [isLoading, setIsLoading] = React.useState(false);
  const [showPassword, setShowPassword] = React.useState(false);

  const { register, handleSubmit, formState: { errors } } = useForm<LoginForm>({
    resolver: zodResolver(loginSchema),
  });

  const onSubmit = async (data: LoginForm) => {
    setIsLoading(true);
    try {
      const params = new URLSearchParams();
      params.append('username', data.email);
      params.append('password', data.password);

      const resp = await apiClient.post('/auth/login', params, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
      });
      
      const { access_token } = resp.data;
      
      // Get user profile
      const userResp = await apiClient.get('/auth/me', {
        headers: { Authorization: `Bearer ${access_token}` }
      });
      
      setAuth(userResp.data, access_token);
      toast.success('Authentication successful. Welcome to EpiSense.');
      navigate('/');
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Authentication failed. Check credentials.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#0a0a0c] flex items-center justify-center p-6 relative overflow-hidden">
      {/* Background Decor */}
      <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-brand-primary/10 rounded-full blur-[120px] animate-pulse-soft" />
      <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-emerald-500/10 rounded-full blur-[120px] animate-pulse-soft" />
      
      <div className="w-full max-w-md z-10">
        <div className="text-center mb-10">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-brand-primary/10 border border-brand-primary/20 shadow-[0_0_30px_rgba(30,144,255,0.2)] mb-6">
            <ShieldAlert className="w-8 h-8 text-brand-primary" />
          </div>
          <h1 className="text-4xl font-black tracking-tighter text-white mb-2">EPISENSE</h1>
          <p className="text-slate-500 font-medium uppercase tracking-[0.3em] text-[10px]">Tactical Health Command</p>
        </div>

        <div className="glass-panel p-8 rounded-3xl">
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            <div className="space-y-2">
              <label className="tactical-header">Operational Identity</label>
              <div className="relative group">
                <Mail className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-500 group-focus-within:text-brand-primary transition-colors" />
                <input
                  {...register('email')}
                  type="email"
                  placeholder="name@agency.gov"
                  className="w-full bg-white/[0.03] border border-white/10 rounded-xl py-3 pl-12 pr-4 text-white placeholder:text-slate-600 focus:outline-none focus:ring-2 focus:ring-brand-primary/50 focus:border-brand-primary transition-all"
                />
              </div>
              {errors.email && <p className="text-xs text-rose-500 font-medium ml-1">{errors.email.message}</p>}
            </div>

            <div className="space-y-2">
              <label className="tactical-header">Access Protocol</label>
              <div className="relative group">
                <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-500 group-focus-within:text-brand-primary transition-colors" />
                <input
                  {...register('password')}
                  type={showPassword ? 'text' : 'password'}
                  placeholder="••••••••••••"
                  className="w-full bg-white/[0.03] border border-white/10 rounded-xl py-3 pl-12 pr-12 text-white placeholder:text-slate-600 focus:outline-none focus:ring-2 focus:ring-brand-primary/50 focus:border-brand-primary transition-all"
                />
                <button
                  type="button"
                  aria-label={showPassword ? 'Hide password' : 'Show password'}
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-4 top-1/2 -translate-y-1/2 text-slate-500 hover:text-white transition-colors"
                >
                  {showPassword ? <EyeOff aria-hidden="true" className="w-5 h-5" /> : <Eye aria-hidden="true" className="w-5 h-5" />}
                </button>
              </div>
              {errors.password && <p className="text-xs text-rose-500 font-medium ml-1">{errors.password.message}</p>}
            </div>

            <button
              disabled={isLoading}
              aria-busy={isLoading}
              type="submit"
              className="w-full btn-tactical btn-primary py-4 flex items-center justify-center gap-3 mt-4"
            >
              {isLoading ? (
                <Loader2 aria-hidden="true" className="w-5 h-5 animate-spin" />
              ) : (
                <>
                  <span className="uppercase tracking-widest text-xs font-bold">Initiate Authentication</span>
                </>
              )}
            </button>
          </form>
          
          <div className="mt-8 pt-8 border-t border-white/5 text-center">
            <p className="text-xs text-slate-600">
              Authorized access only. All sessions are monitored.
              <br />
              <span className="text-brand-primary/60 font-semibold cursor-pointer hover:text-brand-primary transition-colors">Emergency Recovery Path</span>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
