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

// Phantom: Request Coalescing
const inFlight = new Map<string, Promise<any>>();

const originalGet = apiClient.get;
apiClient.get = function<T = any, R = AxiosResponse<T>, D = any>(
  url: string,
  config?: AxiosRequestConfig<D>
): Promise<R> {
  const key = url + (config?.params ? JSON.stringify(config.params) : '');

  if (inFlight.has(key)) {
    console.debug(`[Phantom] Coalescing duplicate GET request to ${url}`);
    return inFlight.get(key)!;
  }

  const promise = originalGet.apply(this, [url, config]).finally(() => {
    inFlight.delete(key);
  });

  inFlight.set(key, promise);
  return promise;
};
