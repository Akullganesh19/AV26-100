import type { AxiosRequestConfig } from 'axios';
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

const inFlightRequests = new Map<string, Promise<any>>();

function generateCacheKey(url: string, config?: AxiosRequestConfig): string {
  let key = url;
  if (config?.params) {
    const params = config.params as Record<string, unknown> | URLSearchParams;
    let paramsStr = '';

    if (params instanceof URLSearchParams) {
      paramsStr = params.toString();
    } else if (typeof params === 'object' && params !== null) {
      const sortedKeys = Object.keys(params).sort();
      const serializedParams = sortedKeys.map(k => {
        const v = (params as Record<string, unknown>)[k];
        const valStr = typeof v === 'object' && v !== null ? JSON.stringify(v) : String(v);
        return `${k}=${valStr}`;
      }).join('&');
      paramsStr = serializedParams;
    } else {
      paramsStr = String(params);
    }

    if (paramsStr) {
      key += `?${paramsStr}`;
    }
  }
  return key;
}

const originalGet = apiClient.get;
apiClient.get = function<T = any, R = import("axios").AxiosResponse<T, any>, D = any>(url: string, config?: AxiosRequestConfig<D>): Promise<R> {
  const key = generateCacheKey(url, config);

  if (inFlightRequests.has(key)) {
    console.debug(`[Phantom] Coalesced duplicate request to: ${url}`);
    return inFlightRequests.get(key) as Promise<any>;
  }

  const promise = originalGet.apply(this, [url, config]).finally(() => {
    inFlightRequests.delete(key);
  });

  inFlightRequests.set(key, promise);
  return promise;
};
