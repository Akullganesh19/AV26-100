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

// --- Request Coalescing (Deduplication) ---
const inFlightRequests = new Map<string, Promise<any>>();

function generateCacheKey(url: string, config?: AxiosRequestConfig): string {
  let key = url;
  if (config?.params) {
    if (config.params instanceof URLSearchParams) {
      key += `?${config.params.toString()}`;
    } else {
      const sortedParams = Object.keys(config.params)
        .sort()
        .reduce((acc, k) => {
          const v = config.params[k];
          acc[k] = typeof v === 'object' ? JSON.stringify(v) : String(v);
          return acc;
        }, {} as Record<string, string>);
      key += `?${new URLSearchParams(sortedParams).toString()}`;
    }
  }
  return key;
}

const originalGet = apiClient.get.bind(apiClient);

apiClient.get = <T = any, R = AxiosResponse<T, any>, D = any>(
  url: string,
  config?: AxiosRequestConfig<D>
): Promise<R> => {
  const cacheKey = generateCacheKey(url, config);

  if (inFlightRequests.has(cacheKey)) {
    // Instrumentation: Log when a request is coalesced
    console.debug(`[Phantom] Coalesced request: ${cacheKey}`);
    return inFlightRequests.get(cacheKey) as Promise<R>;
  }

  const promise = originalGet<T, R, D>(url, config).finally(() => {
    inFlightRequests.delete(cacheKey);
  });

  inFlightRequests.set(cacheKey, promise);
  return promise;
};
