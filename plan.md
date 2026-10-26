1. **Explore the current API client code**
   - Check `frontend/src/api/client.ts` to confirm its structure.
2. **Implement Request Coalescing in `frontend/src/api/client.ts`**
   - Override the `apiClient.get` method to store in-flight GET requests in a Map.
   - Use `apiClient.getUri` for generating the cache key from `url` and `config?.params`.
   - Call `originalGet.call(apiClient, url, config)` for the actual fetching.
   - Keep the types accurate as specified in the memory: `function <T = any, R = import('axios').AxiosResponse<T>, D = any>(url: string, config?: import('axios').AxiosRequestConfig<D>): Promise<R>`.
   - Add `console.debug` to prove measurability.
3. **Write to Phantom's Journal**
   - Create and populate `.jules/phantom.md` with details of the request coalescing enhancement.
4. **Test Execution**
   - Run tests and linting in the frontend. `cd frontend && npm run lint; npm run build`
5. **Execute pre-commit instructions**
   - Ensure proper testing, verification, review, and reflection are done by following the pre-commit instructions.
6. **Submit PR**
   - Submit the branch with PR description based on Phantom persona.
