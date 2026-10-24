import axios from 'axios';
import { useAuthStore } from '../store/authStore';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

export const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 🌀 Phantom: Request Coalescing
// Identical concurrent GET requests are deduped into a single network call.
// The promise is shared with all callers, then removed from the map when settled.
const inFlightRequests = new Map<string, Promise<any>>();
const originalGet = apiClient.get;

apiClient.get = function <T = any, R = import('axios').AxiosResponse<T>, D = any>(
  url: string,
  config?: import('axios').AxiosRequestConfig<D>
): Promise<R> {
  const cacheKey = apiClient.getUri({ url, params: config?.params });

  if (inFlightRequests.has(cacheKey)) {
    console.debug(`🌀 Phantom: Coalescing duplicate GET request for ${cacheKey}`);
    return inFlightRequests.get(cacheKey) as Promise<R>;
  }

  const promise = originalGet.call(apiClient, url, config).finally(() => {
    inFlightRequests.delete(cacheKey);
  });

  inFlightRequests.set(cacheKey, promise);
  return promise as Promise<R>;
};

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
