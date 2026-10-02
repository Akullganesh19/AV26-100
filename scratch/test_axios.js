const axios = require('axios');

const inFlight = new Map();

const instance = axios.create();

instance.interceptors.request.use((config) => {
  if (config.method !== 'get') {
    return config;
  }

  // A naive request coalescing implementation inside an interceptor is tricky
  // because interceptors must return config, not a Promise of response.
  // We can wrap the `axios.get` instead, or override the `instance.request` method.
  return config;
});
