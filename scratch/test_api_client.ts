import axios from 'axios';
import http from 'http';

// Create a simple test server
const server = http.createServer((req, res) => {
  setTimeout(() => {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ data: 'ok', url: req.url }));
  }, 100); // 100ms delay to ensure coalescing window
});

server.listen(3000, async () => {
  console.log('Server running on port 3000');

  const apiClient = axios.create({ baseURL: 'http://localhost:3000' });
  const inFlightGets = new Map<string, Promise<any>>();
  const originalGet = apiClient.get;

  apiClient.get = function (url: string, config?: any) {
    let cacheKey = url;
    if (config?.params) {
      let paramsObj: Record<string, unknown> = {};

      if (config.params instanceof URLSearchParams) {
        for (const [key, value] of config.params.entries()) {
          paramsObj[key] = value;
        }
      } else {
        paramsObj = { ...config.params };
      }

      const sortedKeys = Object.keys(paramsObj).sort();
      const sortedParams: Record<string, string> = {};
      for (const key of sortedKeys) {
        const v = paramsObj[key];
        sortedParams[key] = typeof v === 'object' && v !== null ? JSON.stringify(v) : String(v);
      }
      cacheKey = `${url}?${JSON.stringify(sortedParams)}`;
    }

    if (inFlightGets.has(cacheKey)) {
      console.log("Coalescing request for:", cacheKey);
      return inFlightGets.get(cacheKey)!;
    }

    console.log("Making new request for:", cacheKey);
    const promise = originalGet.call(this, url, config).finally(() => {
      inFlightGets.delete(cacheKey);
    });

    inFlightGets.set(cacheKey, promise);
    return promise;
  } as typeof originalGet;

  // Test coalescing
  console.log("Test 1: Identical requests without params");
  const [res1, res2] = await Promise.all([
    apiClient.get('/test'),
    apiClient.get('/test')
  ]);
  console.log("res1 == res2?", res1 === res2);

  console.log("\nTest 2: Identical requests with params");
  const [res3, res4] = await Promise.all([
    apiClient.get('/test', { params: { a: 1, b: 2 } }),
    apiClient.get('/test', { params: { b: 2, a: 1 } })
  ]);
  console.log("res3 == res4?", res3 === res4);

  console.log("\nTest 3: Different requests");
  const [res5, res6] = await Promise.all([
    apiClient.get('/test1'),
    apiClient.get('/test2')
  ]);
  console.log("res5 == res6?", res5 === res6);

  server.close();
});
