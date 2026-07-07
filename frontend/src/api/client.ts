import axios, { InternalAxiosRequestConfig, AxiosResponse, AxiosError } from 'axios';
import { useAuthStore } from '../store/authStore';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

export const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request coalescing for GET requests to prevent identical concurrent network requests
const inFlightRequests = new Map<string, Promise<unknown>>();

apiClient.defaults.adapter = async function(config: InternalAxiosRequestConfig): Promise<unknown> {
  const method = config.method?.toLowerCase();

  if (method !== 'get') {
     const originalAdapter = axios.defaults.adapter;
     const adapterList = Array.isArray(originalAdapter) ? originalAdapter : [originalAdapter];
     const filteredList = adapterList.filter(Boolean) as unknown[];
     const adapterFn = axios.getAdapter(filteredList);
     return (adapterFn as (config: InternalAxiosRequestConfig) => Promise<unknown>)(config);
  }

  let key = `${method}:${config.url}`;
  if (config.params) {
       const sorted = Object.keys(config.params).sort().map(k => {
           const v = config.params[k];
           const valStr = typeof v === 'object' && v !== null ? JSON.stringify(v) : String(v);
           return `${k}=${valStr}`;
       }).join('&');
       key += `?${sorted}`;
  }

  if (inFlightRequests.has(key)) {
     return inFlightRequests.get(key);
  }

  const originalAdapter = axios.defaults.adapter;
  const adapterList = Array.isArray(originalAdapter) ? originalAdapter : [originalAdapter];
  const filteredList = adapterList.filter(Boolean) as unknown[];
  const adapterFn = axios.getAdapter(filteredList);

  const promise = (adapterFn as (config: InternalAxiosRequestConfig) => Promise<unknown>)(config).finally(() => {
     inFlightRequests.delete(key);
  });

  inFlightRequests.set(key, promise);
  return promise;
};

apiClient.interceptors.request.use((config) => {
  const token = useAuthStore.getState().token;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

apiClient.interceptors.response.use(
  (response: AxiosResponse) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      useAuthStore.getState().logout();
    }
    return Promise.reject(error);
  }
);
