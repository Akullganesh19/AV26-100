import axios from 'axios';
import { useAuthStore } from '../store/authStore';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

export const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

const inFlight = new Map();
const originalGet = apiClient.get;

apiClient.get = function(url, config) {
  const key = url + (config ? JSON.stringify(config) : '');
  if (inFlight.has(key)) {
    return inFlight.get(key);
  }

  const promise = originalGet.call(this, url, config).finally(() => {
    inFlight.delete(key);
  });

  inFlight.set(key, promise);
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
