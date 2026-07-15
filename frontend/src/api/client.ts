import axios, { AxiosRequestConfig } from 'axios';
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

// Request coalescing map
const inFlight = new Map<string, Promise<any>>();
const originalGet = apiClient.get.bind(apiClient);

function getCacheKey(url: string, config?: AxiosRequestConfig): string {
  let key = url;
  if (config?.params) {
    if (config.params instanceof URLSearchParams) {
      key += `?${config.params.toString()}`;
    } else if (typeof config.params === 'object') {
      const sortedKeys = Object.keys(config.params).sort();
      const queryParts = sortedKeys.map(k => {
        const v = config.params[k];
        return `${k}=${typeof v === 'object' ? JSON.stringify(v) : String(v)}`;
      });
      if (queryParts.length > 0) {
        key += `?${queryParts.join('&')}`;
      }
    } else {
      key += `?${String(config.params)}`;
    }
  }
  return key;
}

apiClient.get = <T = any, R = import('axios').AxiosResponse<T, any>, D = any>(
  url: string,
  config?: AxiosRequestConfig<D>
): Promise<R> => {
  const cacheKey = getCacheKey(url, config);

  if (inFlight.has(cacheKey)) {
    return inFlight.get(cacheKey) as Promise<R>;
  }

  const promise = originalGet(url, config).finally(() => {
    inFlight.delete(cacheKey);
  });

  inFlight.set(cacheKey, promise);
  return promise as Promise<R>;
};
