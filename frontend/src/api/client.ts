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

// Request Coalescing Middleware
// Identical in-flight GET requests are deduplicated into a single network call.
const inFlightGets = new Map<string, Promise<unknown>>();

const originalGet = apiClient.get;
apiClient.get = (async (url: string, config?: Record<string, unknown>) => {
  // Generate deterministic cache key based on URL and sorted query params
  let cacheKey = url;
  if (config && config.params) {
    const paramsObj: Record<string, unknown> = config.params instanceof URLSearchParams
      ? Object.fromEntries(config.params.entries())
      : config.params as Record<string, unknown>;

    // Sort keys to ensure consistent JSON stringification
    const sortedKeys = Object.keys(paramsObj).sort();
    const sortedParams: Record<string, unknown> = {};
    for (const key of sortedKeys) {
      const v = paramsObj[key];
      // Properly serialize nested objects to avoid "[object Object]"
      sortedParams[key] = typeof v === 'object' && v !== null ? JSON.stringify(v) : String(v);
    }
    cacheKey = `${url}?${JSON.stringify(sortedParams)}`;
  }

  if (inFlightGets.has(cacheKey)) {
    return inFlightGets.get(cacheKey);
  }

  const promise = originalGet(url, config).finally(() => {
    inFlightGets.delete(cacheKey);
  });

  inFlightGets.set(cacheKey, promise);
  return promise;
}) as typeof originalGet;
