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

// --- Request Coalescing (Invisible Infrastructure) ---
// Multiple simultaneous GET requests to the same URL+params will be
// deduplicated into a single network request.
const inFlightGets = new Map<string, Promise<any>>();
const originalGet = apiClient.get;

apiClient.get = function (url: string, config?: any) {
  // If the request has an abort signal, we bypass coalescing
  // because aborting one request would incorrectly abort the coalesced promise for others.
  if (config?.signal) {
    return originalGet.call(this, url, config);
  }

  const paramsString = config?.params ? JSON.stringify(config.params) : '';
  const key = `${url}|${paramsString}`;

  if (inFlightGets.has(key)) {
    console.debug(`🌀 Phantom: Coalesced duplicate GET request to ${url}`);
    return inFlightGets.get(key)!;
  }

  const promise = originalGet.call(this, url, config).finally(() => {
    inFlightGets.delete(key);
  });

  inFlightGets.set(key, promise);
  return promise;
};
