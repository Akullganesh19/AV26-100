import axios from 'axios';
import { useAuthStore } from '../store/authStore';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

export const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 🌀 Phantom: Invisible Infrastructure - Request Coalescing
// Identical GET requests made concurrently will resolve to the exact same promise.
// Prevents thundering herds of requests on component mount/render.
const inFlightRequests = new Map();

const originalGet = apiClient.get;
(apiClient as any).get = async (url: string, config?: any) => {
  const cacheKey = url + JSON.stringify(config || {});

  if (inFlightRequests.has(cacheKey)) {
    console.debug(`🌀 Phantom: Coalesced duplicate request to ${url}`);
    return inFlightRequests.get(cacheKey);
  }

  const promise = originalGet.call(apiClient, url, config).finally(() => {
    inFlightRequests.delete(cacheKey);
  });

  inFlightRequests.set(cacheKey, promise);
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
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      useAuthStore.getState().logout();
    }
    return Promise.reject(error);
  }
);
