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

// 🌀 Phantom: Request Coalescing Infrastructure
const inFlight = new Map<string, Promise<AxiosResponse>>();

const originalGet = apiClient.get;

// eslint-disable-next-line @typescript-eslint/no-explicit-any
apiClient.get = async function<T = any, R = AxiosResponse<T>, D = any>(
  url: string,
  config?: AxiosRequestConfig<D>
): Promise<R> {
  const queryParams = config?.params ? JSON.stringify(config.params) : '';
  const cacheKey = `${url}?${queryParams}`;

  if (inFlight.has(cacheKey)) {
    return inFlight.get(cacheKey) as Promise<R>;
  }

  const promise = originalGet.call(this, url, config).finally(() => {
    inFlight.delete(cacheKey);
  });

  inFlight.set(cacheKey, promise);

  return promise as Promise<R>;
};
