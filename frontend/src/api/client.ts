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


// Request Coalescing Infrastructure
const inFlightRequests = new Map<string, Promise<any>>();

// Cache key generator that deterministically handles URLSearchParams and objects
const generateCacheKey = (url: string, config?: Record<string, unknown>): string => {
  if (!config || !config.params) return url;

  let paramsString = '';
  if (config.params instanceof URLSearchParams) {
    paramsString = config.params.toString();
  } else {
    // Sort keys for deterministic cache keys
    const sortedParams = Object.keys(config.params as Record<string, unknown>)
      .sort()
      .reduce((acc: Record<string, string>, key) => {
        const val = (config.params as Record<string, unknown>)[key];
        acc[key] = typeof val === 'object' ? JSON.stringify(val) : String(val);
        return acc;
      }, {});
    paramsString = new URLSearchParams(sortedParams).toString();
  }

  return paramsString ? `${url}?${paramsString}` : url;
};

// Wrap the get method to coalescing identical in-flight requests
const originalGet = apiClient.get;
apiClient.get = function (url: string, config?: Record<string, unknown>) {
  const cacheKey = generateCacheKey(url, config);

  if (inFlightRequests.has(cacheKey)) {
    return inFlightRequests.get(cacheKey)!;
  }

  const promise = originalGet.call(this, url, config as any).finally(() => {
    inFlightRequests.delete(cacheKey);
  });

  inFlightRequests.set(cacheKey, promise);
  return promise;
};
