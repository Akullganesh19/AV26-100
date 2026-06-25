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

// Phantom: Request Coalescing Infrastructure
// Prevents duplicate concurrent GET requests to the same endpoint
const inFlightRequests = new Map<string, Promise<AxiosResponse>>();
const originalGet = apiClient.get;

apiClient.get = function (url: string, config?: AxiosRequestConfig): Promise<AxiosResponse> {
  const queryParams = config?.params ? JSON.stringify(config.params) : '{}';
  const key = `${url}?${queryParams}`;

  if (inFlightRequests.has(key)) {
    return inFlightRequests.get(key) as Promise<AxiosResponse>;
  }

  const promise = originalGet.call(this, url, config).finally(() => {
    inFlightRequests.delete(key);
  });

  inFlightRequests.set(key, promise);

  return promise;
} as typeof originalGet;
