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

// 🌀 Phantom: Invisible Request Coalescing
// Prevent duplicate simultaneous GET requests for the same resource
const inFlightGets = new Map<string, Promise<any>>();
const originalGet = apiClient.get;

apiClient.get = function <T = any, R = import('axios').AxiosResponse<T>, D = any>(
  url: string,
  config?: import('axios').AxiosRequestConfig<D>
): Promise<R> {
  let cacheKey = url;
  if (config && config.params) {
    // Safely serialize query params to avoid "[object Object]" collisions on nested objects
    cacheKey = apiClient.getUri({ url, params: config.params });
  }

  if (inFlightGets.has(cacheKey)) {
    console.debug(`[Phantom] Coalescing duplicate GET request to: ${url}`);
    return inFlightGets.get(cacheKey) as Promise<R>;
  }

  const promise = originalGet.call(this, url, config).finally(() => {
    inFlightGets.delete(cacheKey);
  });

  inFlightGets.set(cacheKey, promise);
  return promise as Promise<R>;
};
