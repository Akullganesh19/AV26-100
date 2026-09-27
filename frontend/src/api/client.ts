import axios from 'axios';
import { useAuthStore } from '../store/authStore';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

export const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

const pendingRequests = new Map<string, Promise<any>>();

const originalGet = apiClient.get;
// @ts-ignore - Override Axios get signature for coalescing
apiClient.get = function (url: string, config?: any) {
  // Create a unique key based on URL and query params
  let queryStr = '';
  if (config?.params) {
    if (config.params instanceof URLSearchParams) {
      queryStr = config.params.toString();
    } else {
      queryStr = JSON.stringify(config.params);
    }
  }
  const key = url + queryStr;

  if (pendingRequests.has(key)) {
    return pendingRequests.get(key) as Promise<any>;
  }

  const requestPromise = originalGet.call(this, url, config).finally(() => {
    pendingRequests.delete(key);
  });

  pendingRequests.set(key, requestPromise);
  return requestPromise;
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
