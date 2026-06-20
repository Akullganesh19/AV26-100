import axios, { AxiosRequestConfig, AxiosResponse } from 'axios';
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

// Request Coalescing
// Prevent multiple simultaneous GET requests to the same URL
const inFlightRequests = new Map<string, Promise<AxiosResponse<unknown>>>();
const originalGet = apiClient.get;

function getCacheKey(url: string, config?: AxiosRequestConfig): string {
  const params = config?.params ? new URLSearchParams(config.params).toString() : '';
  const responseType = config?.responseType || '';

  // Create a stable string representation of headers if they exist
  let headersStr = '';
  if (config?.headers) {
    // Convert headers to a predictable string to avoid object key ordering issues
    const headerKeys = Object.keys(config.headers).sort();
    headersStr = headerKeys.map(k => `${k}:${config.headers![k]}`).join(',');
  }

  return `${url}?${params}|${headersStr}|${responseType}`;
}

apiClient.get = function <T = unknown, R = AxiosResponse<T>, D = unknown>(
  url: string,
  config?: AxiosRequestConfig<D>
): Promise<R> {
  const cacheKey = getCacheKey(url, config as AxiosRequestConfig);

  if (inFlightRequests.has(cacheKey)) {
    // Only clone the data payload to avoid DataCloneError on the full AxiosResponse
    // The AxiosResponse object contains non-cloneable items like the XMLHttpRequest
    return inFlightRequests.get(cacheKey)!.then((res) => {
      return {
        ...res,
        data: typeof res.data === 'object' && res.data !== null
          ? structuredClone(res.data)
          : res.data
      } as unknown as R;
    });
  }

  const promise = originalGet.call(apiClient, url, config).finally(() => {
    inFlightRequests.delete(cacheKey);
  });

  inFlightRequests.set(cacheKey, promise as Promise<AxiosResponse<unknown>>);
  return promise as Promise<R>;
};
