import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '1m', target: 20 }, // Ramp up to 20 users
    { duration: '3m', target: 20 }, // Stay at 20 users
    { duration: '1m', target: 0 },  // Ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<800'], // 95% of requests must be below 800ms
    http_req_failed: ['rate<0.01'],   // Error rate must be less than 1%
  },
};

export default function () {
  const url = 'http://localhost:8000/api/v1/predict/';
  const payload = JSON.stringify({
    district_id: 'd8a7c2e3-4f5g-6h7i-8j9k-0l1m2n3o4p5q', // Placeholder UUID
    disease: 'cholera',
    prediction_date: '2024-05-14',
    overrides: {}
  });

  const params = {
    headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer YOUR_TEST_JWT_TOKEN',
    },
  };

  const res = http.post(url, payload, params);
  
  check(res, {
    'status is 201': (r) => r.status === 201,
    'has prediction_id': (r) => r.json().hasOwnProperty('prediction_id'),
  });

  sleep(1);
}
