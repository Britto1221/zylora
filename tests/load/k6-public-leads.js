import http from "k6/http";
import { check, sleep } from "k6";
export const options = { stages: [{ duration: "30s", target: 10 }, { duration: "60s", target: 50 }, { duration: "30s", target: 0 }], thresholds: { http_req_failed: ["rate<0.01"], http_req_duration: ["p(95)<750"] } };
const API = __ENV.API_URL || "http://localhost:8000/api/v1";
export default function () {
  const body = JSON.stringify({ site_id: __ENV.SITE_ID, name: `Load ${__VU}-${__ITER}`, email: `load-${__VU}-${__ITER}@example.test`, whatsapp_consent: false, metadata: {} });
  const response = http.post(`${API}/leads/public`, body, { headers: { "Content-Type": "application/json" } });
  check(response, { "lead accepted": (r) => r.status === 201 || r.status === 429 }); sleep(0.2);
}
