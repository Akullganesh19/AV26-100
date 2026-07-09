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

// 🌀 Phantom: Invisible Infrastructure - Request Coalescing
// Prevents duplicate concurrent identical GET requests by returning the same Promise.
// We wrap the `apiClient.get` method rather than overriding `apiClient.request` or
// `apiClient.defaults.adapter` (which causes Axios version/type conflicts).
const inFlight = new Map<string, Promise<any>>();
const originalGet = apiClient.get;

apiClient.get = async function <T = any, R = import('axios').AxiosResponse<T>, D = any>(
  this: import('axios').AxiosInstance,
  url: string,
  config?: import('axios').AxiosRequestConfig<D>
): Promise<R> {
  // Generate a robust key including headers and base URL to avoid cross-contamination
  const baseURL = config?.baseURL || this.defaults.baseURL || '';
  const headers = config?.headers ? JSON.stringify(config.headers) : '';

  // Handle both standard objects and URLSearchParams for config.params
  let paramsStr = '';
  if (config?.params) {
    if (config.params instanceof URLSearchParams) {
      const entries = Array.from(config.params.entries());
      entries.sort(([keyA], [keyB]) => keyA.localeCompare(keyB));
      paramsStr = new URLSearchParams(entries).toString();
    } else {
      paramsStr = JSON.stringify(
        Object.entries(config.params).sort(([keyA], [keyB]) => keyA.localeCompare(keyB))
      );
    }
  }

  const key = `get:${baseURL}${url}?headers=${headers}&params=${paramsStr}`;

  if (inFlight.has(key)) {
    // Return the cached promise. We do not clone or spread the response here because
    // the response could be an array (from interceptors) or a complex object, and spreading
    // could corrupt it. The config sharing risk is minimal for idempotent GET requests
    // that have the same headers and params.
    return inFlight.get(key) as Promise<R>;
  }

  const promise = originalGet.call(this, url, config).finally(() => {
    inFlight.delete(key);
  });

  inFlight.set(key, promise);
  return promise;
};
