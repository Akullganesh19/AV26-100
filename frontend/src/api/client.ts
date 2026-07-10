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

// --- Request Coalescing (Phantom) ---
// Deduplicate identical simultaneous GET requests

const inFlightRequests = new Map<string, Promise<unknown>>();

function generateCacheKey(url: string, config?: AxiosRequestConfig): string {
  let key = url;
  if (config?.params) {
    if (config.params instanceof URLSearchParams) {
      key += `?${config.params.toString()}`;
    } else {
      const paramsObj = config.params as Record<string, unknown>;
      const sortedKeys = Object.keys(paramsObj).sort();
      const paramsString = sortedKeys.map(k => {
        const v = paramsObj[k];
        return `${k}=${typeof v === 'object' && v !== null ? JSON.stringify(v) : String(v)}`;
      }).join('&');
      if (paramsString) {
        key += `?${paramsString}`;
      }
    }
  }
  return key;
}

const originalGet = apiClient.get;
apiClient.get = function <T = unknown, R = AxiosResponse<T>, D = unknown>(url: string, config?: AxiosRequestConfig<D>): Promise<R> {
  const key = generateCacheKey(url, config);

  if (inFlightRequests.has(key)) {
    return inFlightRequests.get(key) as Promise<R>;
  }

  const promise = originalGet.call(this, url, config).finally(() => {
    inFlightRequests.delete(key);
  });

  inFlightRequests.set(key, promise);
  return promise as Promise<R>;
};
