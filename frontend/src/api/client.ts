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

// 🌀 Phantom: Invisible Infrastructure - Request Coalescing
// This deduplicates concurrent identical GET requests across the app.
// If 5 components render simultaneously and request the same data,
// only 1 network request is made. The other 4 wait on the same Promise.
// Uses `unknown` to satisfy ESLint while achieving identical behavior.
const pendingGetRequests = new Map<string, Promise<AxiosResponse<unknown>>>();
const originalGet = apiClient.get;

apiClient.get = function <T = unknown, R = AxiosResponse<T>, D = unknown>(
  url: string,
  config?: AxiosRequestConfig<D>
): Promise<R> {
  const queryParams = config?.params ? JSON.stringify(config.params) : '';
  const cacheKey = `${url}?${queryParams}`;

  if (pendingGetRequests.has(cacheKey)) {
    // Return the in-flight promise to coalesce requests
    return pendingGetRequests.get(cacheKey) as Promise<R>;
  }

  const promise = originalGet.call(this, url, config) as Promise<R>;

  const wrappedPromise = promise.finally(() => {
    // Clean up once the request completes (success or error)
    pendingGetRequests.delete(cacheKey);
  });

  pendingGetRequests.set(cacheKey, wrappedPromise as unknown as Promise<AxiosResponse<unknown>>);

  return wrappedPromise as Promise<R>;
};
