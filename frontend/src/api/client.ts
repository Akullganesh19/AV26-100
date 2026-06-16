import axios, { AxiosRequestConfig } from 'axios';
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

// Invisible Infrastructure: Request Coalescing
// Prevents identical simultaneous GET requests by returning the same promise.
// eslint-disable-next-line @typescript-eslint/no-explicit-any
const inFlight = new Map<string, Promise<any>>();
const originalGet = apiClient.get;

// eslint-disable-next-line @typescript-eslint/no-explicit-any
apiClient.get = async function <T = any, R = import('axios').AxiosResponse<T>, D = any>(url: string, config?: AxiosRequestConfig<D>): Promise<R> {
  // Generate a unique key for this request based on URL and query params
  const key = `${url}:${JSON.stringify(config?.params || {})}`;

  if (inFlight.has(key)) {
    // Return the existing promise instead of making a new request
    return inFlight.get(key)!;
  }

  // Make the actual request and store the promise
  const promise = originalGet.call(this, url, config).finally(() => {
    // Remove from in-flight map when request completes (success or failure)
    inFlight.delete(key);
  });

  inFlight.set(key, promise);
  return promise;
};
