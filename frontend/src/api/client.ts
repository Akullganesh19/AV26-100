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

// Phantom: Request Coalescing Infrastructure
const inFlight = new Map();
const originalGet = apiClient.get;

// Wrap the original get method for coalescing duplicate requests
apiClient.get = function(url: string, config?: any) {
  // Use config params if any exist to make the key unique to the request
  const key = `${url}-${JSON.stringify(config?.params || {})}`;

  // If already in flight, return the same promise
  if (inFlight.has(key)) {
    console.debug(`[Phantom] Coalesced duplicate request: ${url}`);
    return inFlight.get(key);
  }

  // Otherwise make request and store promise
  const promise = originalGet.call(this, url, config).finally(() => {
    // Ensure we delete it from the map when it completes (success or failure)
    inFlight.delete(key);
  });

  inFlight.set(key, promise);
  return promise;
};
