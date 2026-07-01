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
// Prevent duplicate concurrent GET requests for the same URL + params
const inFlightGets = new Map<string, Promise<unknown>>();
const originalGet = apiClient.get;

apiClient.get = (async (url: string, config?: Record<string, unknown>) => {
  let cacheKey = url;

  if (config && config.params) {
    let paramsObj: Record<string, unknown> = {};
    if (config.params instanceof URLSearchParams) {
      for (const [key, value] of config.params.entries()) {
        paramsObj[key] = value;
      }
    } else {
      paramsObj = { ...(config.params as Record<string, unknown>) };
    }

    const sortedKeys = Object.keys(paramsObj).sort();
    if (sortedKeys.length > 0) {
      const queryString = sortedKeys.map(k => {
        const v = paramsObj[k];
        const serialized = typeof v === 'object' && v !== null ? JSON.stringify(v) : String(v);
        return `${k}=${serialized}`;
      }).join('&');
      cacheKey += `?${queryString}`;
    }
  }

  if (inFlightGets.has(cacheKey)) {
    return inFlightGets.get(cacheKey);
  }

  const promise = originalGet(url, config).finally(() => {
    inFlightGets.delete(cacheKey);
  });

  inFlightGets.set(cacheKey, promise);
  return promise;
}) as typeof originalGet;
