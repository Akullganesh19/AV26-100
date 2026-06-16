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

// --- Phantom Infrastructure: Request Coalescing & Caching ---
const CACHE_TTL_MS = 5000; // 5 seconds cache
const inFlightRequests = new Map<string, Promise<any>>();
const requestCache = new Map<string, { timestamp: number; data: any }>();

const originalGet = apiClient.get;

apiClient.get = async function (url: string, config?: any) {
  // Only cache and coalesce GET requests that don't explicitly bypass cache
  if (config?.headers?.['Cache-Control'] === 'no-cache') {
    return originalGet.call(this, url, config);
  }

  // Create a unique key for the request (URL + params)
  const cacheKey = url + (config?.params ? JSON.stringify(config.params) : '');

  // 1. Check Cache
  const cached = requestCache.get(cacheKey);
  if (cached && Date.now() - cached.timestamp < CACHE_TTL_MS) {
    console.log(`[Phantom Cache] HIT: ${url}`);
    return { data: cached.data, status: 200, statusText: 'OK', headers: {}, config: config || {} };
  }

  // 2. Check In-Flight (Coalescing)
  if (inFlightRequests.has(cacheKey)) {
    console.log(`[Phantom Coalesce] JOIN: ${url}`);
    return inFlightRequests.get(cacheKey)!;
  }

  console.log(`[Phantom Network] FETCH: ${url}`);

  // 3. Make Network Request
  const promise = originalGet.call(this, url, config).then((response) => {
    // Cache the response
    requestCache.set(cacheKey, { timestamp: Date.now(), data: response.data });
    return response;
  }).finally(() => {
    // Remove from in-flight
    inFlightRequests.delete(cacheKey);
  });

  inFlightRequests.set(cacheKey, promise);
  return promise;
};
