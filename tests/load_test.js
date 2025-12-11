import http from 'k6/http';
import { check } from 'k6';

export const options = {
  scenarios: {
    constant_load: {
      executor: 'constant-arrival-rate',
      rate: 200,          // MUDANÇA: De 5000 para 1000 TPS (Realista para Desktop comum, se não dexe 5000)
      timeUnit: '1s',
      duration: '30s',
      preAllocatedVUs: 20,
      maxVUs: 500,         // MUDANÇA: Damos mais folga para o K6 criar conexões
    },
  },
  thresholds: {
    'http_req_duration': ['p(99)<500'], // Relaxamos o SLA para 500ms (Docker Windows é mais lento)
    'http_req_failed': ['rate<0.05'],   // Aceitamos até 5% de erro em teste de stress máximo
  },
};

const payload = JSON.stringify({
  features: Array(30).fill(0.5) // Dados falsos (30 features)
});

const params = {
  headers: {
    'Content-Type': 'application/json',
  },
};

export default function () {
  // Batendo na porta 8080 (Nginx)
  const res = http.post('http://localhost:8080/predict', payload, params);
  
  check(res, {
    'status is 200': (r) => r.status === 200,
  });
}