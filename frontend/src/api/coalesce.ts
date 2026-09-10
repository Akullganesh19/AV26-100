import { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';

// Map to store in-flight requests by URL + method
const inFlightRequests = new Map<string, Promise<any>>();

/**
 * Wraps an axios instance to coalesce identical concurrent GET requests.
 * Instead of firing multiple duplicate requests, subsequent identical
 * requests will await the response of the first one.
 */
export const withRequestCoalescing = (axiosInstance: AxiosInstance): AxiosInstance => {
  const originalGet = axiosInstance.get;

  (axiosInstance as any).get = async function<T = any, R = AxiosResponse<T>, D = any>(
    url: string,
    config?: AxiosRequestConfig<D>
  ): Promise<R> {
    // We only coalesce GET requests
    // Generate a cache key based on URL and query params
    const cacheKey = JSON.stringify({
      url,
      params: config?.params,
      auth: config?.headers?.Authorization
    });

    if (inFlightRequests.has(cacheKey)) {
      return inFlightRequests.get(cacheKey) as Promise<R>;
    }

    const promise = originalGet.call(this, url, config).finally(() => {
      inFlightRequests.delete(cacheKey);
    });

    inFlightRequests.set(cacheKey, promise);
    return promise;
  };

  return axiosInstance;
};
