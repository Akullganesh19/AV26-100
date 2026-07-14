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


// --- Request Coalescing Infrastructure ---
const inFlightRequests = new Map<string, Promise<any>>();

function generateCacheKey(url: string, config?: import('axios').AxiosRequestConfig): string {
  if (!config?.params) return url;

  let paramsString = '';
  if (config.params instanceof URLSearchParams) {
    paramsString = config.params.toString();
  } else {
    const sortedKeys = Object.keys(config.params).sort();
    const serializedParams = sortedKeys.map(key => {
      const val = config.params[key];
      const serializedVal = typeof val === 'object' && val !== null ? JSON.stringify(val) : String(val);
      return `${key}=${serializedVal}`;
    }).join('&');
    paramsString = serializedParams;
  }
  return paramsString ? `${url}?${paramsString}` : url;
}

const originalGet = apiClient.get.bind(apiClient);
apiClient.get = <T = any, R = import('axios').AxiosResponse<T, any>, D = any>(url: string, config?: import('axios').AxiosRequestConfig<D>): Promise<R> => {
  const cacheKey = generateCacheKey(url, config);
  if (inFlightRequests.has(cacheKey)) return inFlightRequests.get(cacheKey) as Promise<R>;
  const promise = originalGet<T, R, D>(url, config).finally(() => inFlightRequests.delete(cacheKey));
  inFlightRequests.set(cacheKey, promise);
  return promise;
};
