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
const inFlightRequests = new Map<string, Promise<unknown>>();

function generateCacheKey(url: string, config?: Record<string, unknown>): string {
  if (!config || !config.params) return url;

  let paramsObj: Record<string, unknown> = {};
  const params = config.params;

  if (params instanceof URLSearchParams) {
    for (const [key, value] of params.entries()) {
      paramsObj[key] = value;
    }
  } else if (typeof params === 'object' && params !== null) {
    paramsObj = { ...(params as Record<string, unknown>) };
  }

  const sortedKeys = Object.keys(paramsObj).sort();
  const sortedParams = sortedKeys.map(key => {
    const v = paramsObj[key];
    const stringified = typeof v === 'object' && v !== null ? JSON.stringify(v) : String(v);
    return `${key}=${stringified}`;
  }).join('&');

  return sortedParams ? `${url}?${sortedParams}` : url;
}

apiClient.get = function(url: string, config?: Record<string, unknown>) {
  const key = generateCacheKey(url, config);

  if (inFlightRequests.has(key)) {
    return inFlightRequests.get(key)!;
  }

  const promise = originalGet.call(this, url, config as Record<string, unknown>).finally(() => {
    inFlightRequests.delete(key);
  });

  inFlightRequests.set(key, promise);
  return promise;
} as typeof originalGet;
