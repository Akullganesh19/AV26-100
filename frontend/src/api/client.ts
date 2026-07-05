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

const originalGet = apiClient.get;
const inFlightGets = new Map<string, Promise<unknown>>();

apiClient.get = function (url: string, config?: Parameters<typeof originalGet>[1]) {
  let cacheKey = url;
  if (config && config.params) {
    let paramsObj: Record<string, unknown> = {};
    if (config.params instanceof URLSearchParams) {
      for (const [key, value] of config.params.entries()) {
        paramsObj[key] = value;
      }
    } else if (typeof config.params === 'object' && config.params !== null) {
      paramsObj = { ...(config.params as Record<string, unknown>) };
    }

    const sortedKeys = Object.keys(paramsObj).sort();
    const sortedParams = sortedKeys.map(key => {
      const v = paramsObj[key];
      const serializedValue = typeof v === 'object' && v !== null ? JSON.stringify(v) : String(v);
      return `${key}=${serializedValue}`;
    }).join('&');

    if (sortedParams) {
      cacheKey += `?${sortedParams}`;
    }
  }

  if (inFlightGets.has(cacheKey)) {
    return inFlightGets.get(cacheKey) as ReturnType<typeof originalGet>;
  }

  const promise = originalGet(url, config).finally(() => {
    inFlightGets.delete(cacheKey);
  });

  inFlightGets.set(cacheKey, promise);
  return promise as ReturnType<typeof originalGet>;
} as typeof originalGet;
