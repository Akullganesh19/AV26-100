const axios = require('axios');

const apiClient = axios.create();

const inFlight = new Map();
const originalGet = apiClient.get;

apiClient.get = function(url, config) {
  const key = url + (config ? JSON.stringify(config) : '');
  if (inFlight.has(key)) {
    console.log('Coalescing request:', key);
    return inFlight.get(key);
  }

  const promise = originalGet.call(this, url, config).finally(() => {
    inFlight.delete(key);
  });

  inFlight.set(key, promise);
  return promise;
};

async function test() {
  const p1 = apiClient.get('https://jsonplaceholder.typicode.com/todos/1');
  const p2 = apiClient.get('https://jsonplaceholder.typicode.com/todos/1');

  await Promise.all([p1, p2]);
  console.log('Done');
}

test();
