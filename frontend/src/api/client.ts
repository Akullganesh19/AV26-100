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
const originalGet = apiClient.get;
const inFlightGetRequests = new Map<string, Promise<unknown>>();

apiClient.get = function <T = unknown, R = AxiosResponse<T>, D = unknown>(
  url: string,
  config?: AxiosRequestConfig<D>
): Promise<R> {
  // Sort keys to ensure consistent cache keys regardless of parameter order
  const sortedParams = config?.params
    ? Object.keys(config.params).sort().reduce((acc: Record<string, unknown>, key) => {
        acc[key] = config.params[key];
        return acc;
      }, {})
    : undefined;

  const cacheKey = JSON.stringify({ url, params: sortedParams });

  if (inFlightGetRequests.has(cacheKey)) {
    return inFlightGetRequests.get(cacheKey) as Promise<R>;
  }

  const promise = originalGet.call(this, url, config).finally(() => {
    inFlightGetRequests.delete(cacheKey);
  });

  inFlightGetRequests.set(cacheKey, promise);
  return promise as Promise<R>;
};
