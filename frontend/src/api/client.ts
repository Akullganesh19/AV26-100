import axios from 'axios';
import { useAuthStore } from '../store/authStore';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

export const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

apiClient.interceptors.request.use((config) => {
  const token = useAuthStore.getState().token;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      useAuthStore.getState().logout();
    }
    return Promise.reject(error);
  }
);

// 🌪️ Phantom: Request Coalescing Infrastructure
// Prevents duplicate concurrent GET requests to the same endpoint
const pendingRequests = new Map<string, Promise<any>>();
const originalGet = apiClient.get;

apiClient.get = function (url: string, config?: any) {
  const paramsKey = config?.params ? JSON.stringify(config.params) : '';
  const key = `${url}?${paramsKey}`;

  if (pendingRequests.has(key)) {
    console.debug(`[Phantom] Coalescing duplicate request: ${key}`);
    return pendingRequests.get(key)!;
  }

  const promise = originalGet.call(this, url, config).finally(() => {
    pendingRequests.delete(key);
  });

  pendingRequests.set(key, promise);
  return promise;
};
