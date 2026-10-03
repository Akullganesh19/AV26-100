const inFlight = new Map();
function dedupedGet(url) {
  if (inFlight.has(url)) {
    console.log("Coalescing request for", url);
    return inFlight.get(url);
  }
  console.log("Making new request for", url);
  const promise = new Promise((resolve) => setTimeout(() => resolve(`Data for ${url}`), 100))
    .finally(() => inFlight.delete(url));
  inFlight.set(url, promise);
  return promise;
}

async function run() {
  const p1 = dedupedGet('/api/data');
  const p2 = dedupedGet('/api/data');

  const [r1, r2] = await Promise.all([p1, p2]);
  console.log(r1, r2);
}
run();
