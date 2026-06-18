import axios, { AxiosRequestConfig, AxiosResponse } from 'axios';
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
// Multiple simultaneous GET requests for the same resource -> one network request
const inFlightRequests = new Map<string, Promise<AxiosResponse>>();

const originalGet = apiClient.get;

apiClient.get = function (url: string, config?: AxiosRequestConfig) {
  // Fallback to original behavior if signal is provided to allow aborting safely
  if (config?.signal) {
    return originalGet.call(this, url, config);
  }

  const key = `${url}::${config?.params ? JSON.stringify(config.params) : ''}`;

  if (inFlightRequests.has(key)) {
    return inFlightRequests.get(key) as Promise<AxiosResponse<unknown, unknown>>;
  }

  const promise = originalGet.call(this, url, config).finally(() => {
    inFlightRequests.delete(key);
  });

  inFlightRequests.set(key, promise);
  return promise;
} as typeof apiClient.get;
