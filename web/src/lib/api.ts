// web/src/lib/api.ts
import axios from "axios";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8080";

export const api = axios.create({
  baseURL: API_URL,
  timeout: 10000,
});

export async function fetchHistory() {
  const res = await api.get("/v1/predictions/history");
  return res.data;
}

export async function fetchAccuracy(window: string = "30d") {
  const res = await api.get("/v1/accuracy", { params: { window } });
  return res.data;
}

export async function fetchTodaysPredictions(token?: string) {
  const res = await api.get("/v1/predictions/today", {
    headers: token ? { Authorization: `Bearer ${token}` } : {},
  });
  return res.data;
}
