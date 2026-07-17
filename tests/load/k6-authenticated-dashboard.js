import http from "k6/http";
import { check, sleep } from "k6";
export const options = { vus: 10, duration: "1m", thresholds: { http_req_failed: ["rate<0.01"], http_req_duration: ["p(95)<500"] } };
const API = __ENV.API_URL || "http://localhost:8000/api/v1";
export default function () { const response=http.get(`${API}/portal/${__ENV.TENANT_ID}/summary`, { headers:{Authorization:`Bearer ${__ENV.ACCESS_TOKEN}`} }); check(response,{"authorized summary":r=>r.status===200}); sleep(1); }
