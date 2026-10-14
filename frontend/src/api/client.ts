import axios from 'axios';
import { useAuthStore } from '../store/authStore';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

export const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

const originalGet = apiClient.get;
const inFlightGets = new Map<string, Promise<any>>();

apiClient.get = function (url: string, config?: any) {
  const key = `${url}?${JSON.stringify(config?.params || {})}`;

  if (inFlightGets.has(key)) {
    console.debug(`[Phantom] Coalesced duplicate GET request to: ${key}`);
    return inFlightGets.get(key)!;
  }

  const promise = originalGet.call(this, url, config).finally(() => {
    inFlightGets.delete(key);
  });

  inFlightGets.set(key, promise);
  return promise;
} as any;

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
