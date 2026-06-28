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

// Invisible Infrastructure: Request Coalescing
// Identical simultaneous GET requests are deduplicated into a single network call.
// eslint-disable-next-line @typescript-eslint/no-explicit-any
const inFlightGets = new Map<string, Promise<any>>();

// eslint-disable-next-line @typescript-eslint/no-explicit-any
const generateCacheKey = (url: string, config?: any) => {
  if (!config || !config.params) return url;

  const sortedParams = Object.keys(config.params)
    .sort()
    .reduce((acc, key) => {
      acc[key] = config.params[key];
      return acc;
    }, {} as Record<string, unknown>);

  return `${url}?${JSON.stringify(sortedParams)}`;
};

const originalGet = apiClient.get;

// eslint-disable-next-line @typescript-eslint/no-explicit-any
apiClient.get = async function (url: string, config?: any) {
  const cacheKey = generateCacheKey(url, config);

  if (inFlightGets.has(cacheKey)) {
    const response = await inFlightGets.get(cacheKey);
    // Return a shallow copy so modifications by one caller don't affect others.
    // We cannot use structuredClone on AxiosResponse.
    return { ...response };
  }

  const promise = originalGet.call(this, url, config).finally(() => {
    inFlightGets.delete(cacheKey);
  });

  inFlightGets.set(cacheKey, promise);

  return promise;
};
