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

// Implement Request Coalescing for GET requests
const originalGet = apiClient.get;
const inFlightGets = new Map<string, Promise<AxiosResponse>>();

apiClient.get = async <T = unknown, R = AxiosResponse<T>, D = unknown>(
  url: string,
  config?: AxiosRequestConfig<D>
): Promise<R> => {
  // Construct a stable cache key combining URL and query parameters
  const paramsString = config?.params ? JSON.stringify(config.params) : '';
  const cacheKey = `${url}?${paramsString}`;

  if (inFlightGets.has(cacheKey)) {
    // If request is already in flight, wait for it and clone the response
    // We soft clone to avoid DataCloneError from structuredClone on XMLHttpRequest
    const res = await inFlightGets.get(cacheKey)!;
    const clonedResponse: AxiosResponse = { ...res };
    return clonedResponse as unknown as R;
  }

  // Otherwise, initiate a new request
  const promise = originalGet(url, config);

  inFlightGets.set(cacheKey, promise);

  promise.finally(() => {
    inFlightGets.delete(cacheKey);
  });

  return promise as unknown as Promise<R>;
};
