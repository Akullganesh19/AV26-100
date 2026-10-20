import { AxiosInstance, AxiosResponse, AxiosRequestConfig } from 'axios';
import axios from 'axios';

const inFlightGets = new Map<string, Promise<any>>();

export function applyRequestCoalescing(instance: AxiosInstance | typeof axios) {
  const originalGet = instance.get;

  instance.get = function <T = any, R = AxiosResponse<T>, D = any>(
    url: string,
    config?: AxiosRequestConfig<D>
  ): Promise<R> {
    const cacheKey = instance.getUri({ url, params: config?.params });

    if (inFlightGets.has(cacheKey)) {
      console.debug(`[Phantom] Coalescing request for: ${cacheKey}`);
      return inFlightGets.get(cacheKey) as Promise<R>;
    }

    const promise = originalGet.call(instance, url, config).finally(() => {
      inFlightGets.delete(cacheKey);
    });

    inFlightGets.set(cacheKey, promise);
    return promise;
  };
}
