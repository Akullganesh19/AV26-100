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

// Implement Request Coalescing
const originalGet = apiClient.get;
const inFlightRequests = new Map<string, Promise<unknown>>();

function generateCacheKey(url: string, config?: { params?: unknown }): string {
  let key = url;
  if (config && config.params) {
    const sortedParams: Record<string, string> = {};
    if (config.params instanceof URLSearchParams) {
      const entries = Array.from(config.params.entries());
      entries.sort(([keyA], [keyB]) => keyA.localeCompare(keyB));
      entries.forEach(([k, v]) => { sortedParams[k] = v; });
    } else if (typeof config.params === 'object') {
      const entries = Object.entries(config.params as Record<string, unknown>);
      entries.sort(([keyA], [keyB]) => keyA.localeCompare(keyB));
      entries.forEach(([k, v]) => { sortedParams[k] = typeof v === 'object' ? JSON.stringify(v) : String(v); });
    }
    key += '?' + JSON.stringify(sortedParams);
  }
  return key;
}

apiClient.get = (async (url: string, config?: unknown) => {
  const cacheKey = generateCacheKey(url, config as { params?: unknown });

  if (inFlightRequests.has(cacheKey)) {
    return inFlightRequests.get(cacheKey);
  }

  const promise = originalGet(url, config as Record<string, unknown>).finally(() => {
    inFlightRequests.delete(cacheKey);
  });

  inFlightRequests.set(cacheKey, promise);
  return promise;
}) as typeof originalGet;
