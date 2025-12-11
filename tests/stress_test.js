import http from 'k6/http';
import { check } from 'k6';

export const options = {
  scenarios: {
    stress_ramp: {
      executor: 'ramping-arrival-rate',
      startRate: 50,
      timeUnit: '1s',
      preAllocatedVUs: 50,
      maxVUs: 1000,
      stages: [
        { target: 500, duration: '30s' },  // Aquecimento já começa alto
        { target: 1000, duration: '1m' },  // Meta agressiva
        { target: 2000, duration: '1m' },  // GOD MODE
        { target: 0, duration: '30s' },
      ],
    },
  },
  thresholds: {
    'http_req_failed': ['rate<0.10'], // Aceitamos até 10% de falha pois queremos quebrar
  },
};

const payload = JSON.stringify({ features: Array(30).fill(0.5) });
const params = { headers: { 'Content-Type': 'application/json' } };

export default function () {
  const res = http.post('http://localhost:8080/predict', payload, params);
  check(res, { 'status is 200': (r) => r.status === 200 });
}