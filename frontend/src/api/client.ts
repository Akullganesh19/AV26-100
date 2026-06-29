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

// --- Phantom: Request Coalescing ---
// Deduplicate identical concurrent GET requests
const inFlightRequests = new Map<string, Promise<unknown>>();

const getCacheKey = (url: string, config?: Record<string, unknown>) => {
  if (!config?.params || typeof config.params !== 'object') return url;

  let paramsObj: Record<string, unknown> = {};
  if (config.params instanceof URLSearchParams) {
    for (const [key, value] of config.params.entries()) {
      paramsObj[key] = value;
    }
  } else {
    paramsObj = config.params as Record<string, unknown>;
  }

  // Sort params for consistent cache key
  const sortedParams = Object.keys(paramsObj)
    .sort()
    .reduce((acc: Record<string, unknown>, key) => {
      acc[key] = paramsObj[key];
      return acc;
    }, {});
  return `${url}?${JSON.stringify(sortedParams)}`;
};

const originalGet = apiClient.get;
apiClient.get = (async function (url: string, config?: Record<string, unknown>) {
  const cacheKey = getCacheKey(url, config);

  if (inFlightRequests.has(cacheKey)) {
    // Wait for the in-flight request to finish
    const response = await inFlightRequests.get(cacheKey);
    // Clone ONLY the data, not the whole AxiosResponse, to avoid DataCloneError
    return {
      ...(response as Record<string, unknown>),
      data: structuredClone((response as { data: unknown }).data)
    };
  }

  const promise = originalGet.call(this, url, config)
    .finally(() => {
      inFlightRequests.delete(cacheKey);
    });

  inFlightRequests.set(cacheKey, promise);
  return promise;
}) as typeof originalGet;
