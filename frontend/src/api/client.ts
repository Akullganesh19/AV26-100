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

// 🌪️ Phantom: Request Coalescing Infrastructure
// Prevents duplicate concurrent GET requests to the same endpoint
// eslint-disable-next-line @typescript-eslint/no-explicit-any
const pendingRequests = new Map<string, Promise<any>>();
const originalGet = apiClient.get;

// eslint-disable-next-line @typescript-eslint/no-explicit-any
apiClient.get = function <T = any, R = axios.AxiosResponse<T>, D = any>(
  this: any, // Explicitly type 'this' to avoid TS2683 in strict mode
  url: string,
  config?: axios.AxiosRequestConfig<D>
): Promise<R> {
  // If abort signal is provided, or responseType/headers are uniquely modified, bypass coalescing
  if (config?.signal || config?.responseType || config?.headers) {
    return originalGet.call(this, url, config) as Promise<R>;
  }

  // Use URLSearchParams directly if provided, otherwise stringify the generic params object
  let paramsKey = '';
  if (config?.params) {
      if (config.params instanceof URLSearchParams) {
          paramsKey = config.params.toString();
      } else {
          paramsKey = JSON.stringify(config.params);
      }
  }

  const key = `${url}?${paramsKey}`;

  if (pendingRequests.has(key)) {
    console.debug(`[Phantom] Coalescing duplicate request: ${key}`);
    return pendingRequests.get(key)! as Promise<R>;
  }

  const promise = (originalGet.call(this, url, config) as Promise<R>).finally(() => {
    pendingRequests.delete(key);
  });

  pendingRequests.set(key, promise);
  return promise;
};
