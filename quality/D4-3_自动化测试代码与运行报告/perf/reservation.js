import http from 'k6/http';
import { check } from 'k6';
import { sleep } from 'k6';

export const options = {
  vus: 20,
  duration: '1m',
  thresholds: {
    http_req_failed: ['rate<0.01'],
    http_req_duration: ['p(95)<350']
  }
};

export default function () {
  const payload = JSON.stringify({
    member_id: 'm001',
    store_id: 'store-bj-001',
    table_id: 't08',
    reserved_at: '2026-06-05T18:30:00+08:00',
    party_size: 2
  });
  const params = { headers: { 'Content-Type': 'application/json' } };
  const response = http.post('http://localhost:8081/reservations', payload, params);
  check(response, {
    'create reservation status is 201': (r) => r.status === 201
  });
  sleep(1);
}
