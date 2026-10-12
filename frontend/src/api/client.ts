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

// 🌀 Phantom: Request Coalescing (Invisible Infrastructure)
// Prevents multiple identical in-flight GET requests
const inFlight = new Map<string, Promise<any>>();
const originalGet = apiClient.get;
const originalRequest = apiClient.request;

// Helper to safely stringify config objects, avoiding circular reference errors
function safeStringify(obj: any): string {
  try {
    return JSON.stringify(obj, (key, value) => {
      // Ignore common non-serializable properties in axios configs
      if (['cancelToken', 'signal', 'adapter', 'transformRequest', 'transformResponse'].includes(key)) {
        return undefined;
      }
      return value;
    });
  } catch (e) {
    return 'un-stringifiable-config';
  }
}

apiClient.get = function (url: string, config?: any) {
  const cacheKey = config ? `${url}-${safeStringify(config)}` : url;

  if (inFlight.has(cacheKey)) {
    console.debug(`[Phantom] Coalesced identical request to: ${url}`);
    return inFlight.get(cacheKey)!;
  }

  const promise = originalGet.call(this, url, config).finally(() => {
    inFlight.delete(cacheKey);
  });

  inFlight.set(cacheKey, promise);
  return promise;
};

// Also wrap the generic request method if it's used for GETs
apiClient.request = function (config: any) {
  if (config.method?.toLowerCase() === 'get' || !config.method) {
    const url = config.url || '';
    const cacheKey = `${url}-${safeStringify(config)}`;

    if (inFlight.has(cacheKey)) {
      console.debug(`[Phantom] Coalesced identical request to: ${url}`);
      return inFlight.get(cacheKey)!;
    }

    const promise = originalRequest.call(this, config).finally(() => {
      inFlight.delete(cacheKey);
    });

    inFlight.set(cacheKey, promise);
    return promise;
  }
  return originalRequest.call(this, config);
};
