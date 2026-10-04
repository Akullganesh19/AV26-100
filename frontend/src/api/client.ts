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

// 🌀 Phantom: Invisible Infrastructure - Request Coalescing
// Prevents identical GET requests from hitting the network simultaneously.
// If component A and component B both request /api/data at the same time,
// only one network request is made. Both get the same promise resolved.
const inFlightRequests = new Map();

const originalGet = apiClient.get;

apiClient.get = function (url: string, config?: any) {
  // Safe serialization of config for cache key, skipping non-serializable like FormData
  let configStr = '';
  try {
    configStr = JSON.stringify(config || {});
  } catch (e) {
    configStr = 'unserializable';
  }
  const key = `${url}-${configStr}`;

  if (inFlightRequests.has(key)) {
    return inFlightRequests.get(key);
  }

  const promise = originalGet.call(apiClient, url, config).finally(() => {
    inFlightRequests.delete(key);
  });

  inFlightRequests.set(key, promise);
  return promise;
};
