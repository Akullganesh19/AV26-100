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

// Request coalescing for GET requests
const inFlightGets = new Map();
const originalGet = apiClient.get;

apiClient.get = function (...args) {
  const [url, config] = args;
  // Simple serialization of config parameters for cache key
  const cacheKey = url + (config?.params ? JSON.stringify(config.params) : '');

  if (inFlightGets.has(cacheKey)) {
    console.debug(`[Phantom] Coalescing duplicate request to: ${cacheKey}`);
    return inFlightGets.get(cacheKey);
  }

  const promise = originalGet.apply(this, args).finally(() => {
    inFlightGets.delete(cacheKey);
  });

  inFlightGets.set(cacheKey, promise);
  return promise;
};
