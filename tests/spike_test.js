import http from 'k6/http';
import { check } from 'k6';

export const options = {
  scenarios: {
    spike: {
      executor: 'ramping-arrival-rate',
      startRate: 50,
      timeUnit: '1s',
      preAllocatedVUs: 50,
      maxVUs: 2000,
      stages: [
        { target: 100, duration: '10s' },   // Normal
        { target: 2000, duration: '10s' },  // 💣 ATAQUE (20x carga em 10s)
        { target: 2000, duration: '10s' },  // Sustentar ataque
        { target: 100, duration: '10s' },   // Recuperação
      ],
    },
  },
};

const payload = JSON.stringify({ features: Array(30).fill(0.5) });
const params = { headers: { 'Content-Type': 'application/json' } };

export default function () {
  http.post('http://localhost:8080/predict', payload, params);
}