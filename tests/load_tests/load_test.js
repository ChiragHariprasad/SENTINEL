// LEVEL 8: PERFORMANCE TESTING
// Requires: k6 (https://k6.io)
// Run: k6 run tests/load_tests/load_test.js

import http from 'k6/http';
import { check, sleep } from 'k6';

const BASE = 'http://localhost:8082';
const V1 = `${BASE}/api/v1`;
const V2 = `${BASE}/api/v2`;

const SLEEP_DURATION = 1;

export let options = {
  stages: [
    { duration: '30s', target: 50 },   // ramp up to 50
    { duration: '30s', target: 100 },  // ramp up to 100
    { duration: '30s', target: 100 },  // stay at 100
    { duration: '30s', target: 500 },  // ramp up to 500
    { duration: '30s', target: 500 },  // stay at 500
    { duration: '30s', target: 0 },    // ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<2000'], // 95% of requests must complete within 2s
    http_req_failed: ['rate<0.05'],    // less than 5% failures
  },
};

export default function () {
  // Login once, use token for subsequent requests
  const loginRes = http.post(`${V1}/auth/login`, JSON.stringify({
    email: 'admin@sentinel.ai',
    password: 'admin123',
  }), { headers: { 'Content-Type': 'application/json' } });

  check(loginRes, { 'login success': (r) => r.status === 200 });
  const token = loginRes.json('data.access_token');
  if (!token) return;

  const params = { headers: { Authorization: `Bearer ${token}` } };

  // 1. List entities
  let res = http.get(`${V2}/entities`, params);
  check(res, { 'GET /entities': (r) => r.status === 200 });
  sleep(SLEEP_DURATION);

  // 2. Get first entity detail
  const entities = res.json('data.entities');
  if (entities && entities.length > 0) {
    const eid = entities[0].entity_id;
    res = http.get(`${V2}/entities/${eid}`, params);
    check(res, { 'GET /entities/:id': (r) => r.status === 200 });
    sleep(SLEEP_DURATION);

    // 3. Get graph
    res = http.get(`${V2}/graph/entity/${eid}`, params);
    check(res, { 'GET /graph/entity/:id': (r) => r.status === 200 });
    sleep(SLEEP_DURATION);

    // 4. Get risk
    res = http.get(`${V2}/risk/${eid}`, params);
    check(res, { 'GET /risk/:id': (r) => r.status === 200 });
    sleep(SLEEP_DURATION);

    // 5. Run scenario
    res = http.post(`${V2}/scenario/run`, JSON.stringify({
      entity_id: eid, scenario: 'BREACH',
    }), { headers: { 'Content-Type': 'application/json', ...params.headers } });
    check(res, { 'POST /scenario/run': (r) => r.status === 200 });
    sleep(SLEEP_DURATION);
  }

  // 6. Get intelligence
  res = http.get(`${V2}/intelligence/daily`, params);
  check(res, { 'GET /intelligence/daily': (r) => r.status === 200 });
  sleep(SLEEP_DURATION);

  // 7. Get executive brief
  res = http.get(`${V2}/intelligence/executive`, params);
  check(res, { 'GET /intelligence/executive': (r) => r.status === 200 });
  sleep(SLEEP_DURATION);

  // 8. Get priorities
  res = http.get(`${V2}/intelligence/priorities`, params);
  check(res, { 'GET /intelligence/priorities': (r) => r.status === 200 });
  sleep(SLEEP_DURATION);

  // 9. Copilot query
  res = http.post(`${V2}/copilot/query`, JSON.stringify({
    question: 'What should I focus on today?',
  }), { headers: { 'Content-Type': 'application/json', ...params.headers } });
  check(res, { 'POST /copilot/query': (r) => r.status === 200 });
  sleep(SLEEP_DURATION);

  // 10. Pipeline
  res = http.post(`${V2}/pipeline/run`, null, params);
  check(res, { 'POST /pipeline/run': (r) => r.status === 200 });
}
