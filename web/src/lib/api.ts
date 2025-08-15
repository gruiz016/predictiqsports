// web/src/lib/api.ts
import axios from "axios";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8080";
const STORAGE_KEY = "predictiq_token";

export function setToken(token: string | null) {
  if (token) localStorage.setItem(STORAGE_KEY, token);
  else localStorage.removeItem(STORAGE_KEY);
}
export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(STORAGE_KEY);
}

export const api = axios.create({ baseURL: API_URL, timeout: 15000 });
api.interceptors.request.use((config) => {
  const t = getToken();
  if (t) config.headers.Authorization = `Bearer ${t}`;
  return config;
});

// ---------- Public ----------
export async function fetchHistory(): Promise<any[]> {
  const res = await api.get("/v1/predictions/history");
  const d = res.data;
  if (Array.isArray(d)) return d;
  if (d && Array.isArray(d.items)) return d.items;
  if (d && Array.isArray(d.results)) return d.results;
  if (d && Array.isArray(d.data)) return d.data;
  return [];
}

export async function fetchAccuracy(window: string = "30d") {
  const res = await api.get("/v1/accuracy", { params: { window } });
  return res.data;
}

// ---------- Auth ----------
export async function login(email: string, password: string) {
  const res = await api.post("/v1/auth/login", { email, password });
  return res.data;
}
export async function register(email: string, password: string) {
  const res = await api.post("/v1/auth/register", { email, password });
  return res.data;
}

// ---------- Paid ----------
export async function fetchTodaysPredictions() {
  const res = await api.get("/v1/predictions/today");
  return res.data;
}

// ---------- Billing ----------
export async function checkout(plan: "monthly" | "quarterly" | "yearly") {
  const res = await api.post(`/v1/billing/checkout-session?plan=${plan}`);
  return res.data;
}
export async function getBillingStatus() {
  const res = await api.get("/v1/billing/status");
  return res.data;
}
export async function openPortal() {
  const res = await api.post("/v1/billing/portal-session");
  return res.data;
}
export async function syncCheckout(session_id: string) {
  const res = await api.post(`/v1/billing/sync-checkout?session_id=${encodeURIComponent(session_id)}`);
  return res.data;
}
