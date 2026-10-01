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

const inFlightRequests = new Map<string, Promise<any>>();

const originalGet = apiClient.get;

;(apiClient as any).get = async function (url: string, config?: any) {
  const key = `${url}?${JSON.stringify(config?.params || {})}`;

  if (inFlightRequests.has(key)) {
    return inFlightRequests.get(key);
  }

  const promise = originalGet.call(this, url, config).finally(() => {
    inFlightRequests.delete(key);
  });

  inFlightRequests.set(key, promise);
  return promise;
};
