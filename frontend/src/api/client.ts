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

// ⚡ Bolt: Request Coalescing Optimization
// Prevents identical concurrent GET requests by returning the same promise.
const activeRequests = new Map<string, Promise<any>>();
const originalGet = apiClient.get;

apiClient.get = (async (url: string, config?: any) => {
  let cacheKey = url;
  if (config?.params) {
    let paramsStr = '';
    if (config.params instanceof URLSearchParams) {
      const entries = Array.from(config.params.entries()).sort(([a], [b]) => a.localeCompare(b));
      paramsStr = new URLSearchParams(entries).toString();
    } else {
      const sortedKeys = Object.keys(config.params).sort();
      const parts = sortedKeys.map(k => {
        const v = config.params[k];
        const stringified = typeof v === 'object' && v !== null ? JSON.stringify(v) : String(v);
        return `${encodeURIComponent(k)}=${encodeURIComponent(stringified)}`;
      });
      paramsStr = parts.join('&');
    }
    cacheKey += `?${paramsStr}`;
  }

  if (activeRequests.has(cacheKey)) {
    return activeRequests.get(cacheKey);
  }

  const promise = originalGet(url, config).finally(() => {
    activeRequests.delete(cacheKey);
  });

  activeRequests.set(cacheKey, promise);
  return promise;
}) as typeof originalGet;
