import axios, { AxiosRequestConfig, AxiosResponse } from 'axios';
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

// 🌀 Phantom Infrastructure: Request Coalescing
// Deduplicates simultaneous identical GET requests into a single network call.
const inFlightRequests = new Map<string, Promise<AxiosResponse<any, any>>>();

const originalGet = apiClient.get;

apiClient.get = function <T = any, R = AxiosResponse<T>, D = any>(
  url: string,
  config?: AxiosRequestConfig<D>
): Promise<R> {
  // Generate a unique key for this request based on URL and query params
  const keyParams = config?.params ? JSON.stringify(config.params) : '';
  const requestKey = `${url}?${keyParams}`;

  if (inFlightRequests.has(requestKey)) {
    // Return the in-flight promise, saving a network round trip
    console.debug(`🌀 Phantom Coalescing: Reusing in-flight request for ${requestKey}`);
    return inFlightRequests.get(requestKey) as Promise<R>;
  }

  console.debug(`🌀 Phantom Network: Originating new request for ${requestKey}`);
  const promise = originalGet.call(this, url, config).finally(() => {
    inFlightRequests.delete(requestKey);
  });

  inFlightRequests.set(requestKey, promise);
  return promise as Promise<R>;
};
