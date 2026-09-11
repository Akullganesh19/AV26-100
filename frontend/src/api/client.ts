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


// 🌀 Phantom: Request Coalescing
// Multiple simultaneous requests for the same resource → one request
const inFlight = new Map();

const originalGet = apiClient.get;
(apiClient as any).get = function (url: string, config?: any) {
  const cacheKey = config ? `${url}-${JSON.stringify(config)}` : url;

  if (inFlight.has(cacheKey)) {
    return inFlight.get(cacheKey);
  }

  const promise = originalGet.call(this, url, config).finally(() => {
    inFlight.delete(cacheKey);
  });

  inFlight.set(cacheKey, promise);
  return promise;
};
