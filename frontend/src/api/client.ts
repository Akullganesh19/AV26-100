import axios from 'axios';
import { useAuthStore } from '../store/authStore';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

export const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request Coalescing (In-flight request deduplication)
const inFlightGets = new Map();

// Helper to generate a deterministic cache key from URL and params
function generateCacheKey(url: string, params?: Record<string, unknown>): string {
  if (!params) return url;

  const sortedParams = Object.keys(params)
    .sort()
    .reduce((acc, key) => {
      const v = params[key];
      acc[key] = typeof v === 'object' && v !== null ? JSON.stringify(v) : String(v);
      return acc;
    }, {} as Record<string, string>);

  return `${url}?${new URLSearchParams(sortedParams).toString()}`;
}

const originalGet = apiClient.get;
apiClient.get = async function(url: string, config?: any) {
  const cacheKey = generateCacheKey(url, config?.params);

  if (inFlightGets.has(cacheKey)) {
    return inFlightGets.get(cacheKey);
  }

  const promise = originalGet.call(this, url, config)
    .finally(() => {
      inFlightGets.delete(cacheKey);
    });

  inFlightGets.set(cacheKey, promise);
  return promise;
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
