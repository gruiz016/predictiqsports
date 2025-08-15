// web/src/hooks/useBillingStatus.ts
"use client";

import { useEffect, useState } from "react";
import { getBillingStatus } from "@/lib/api";

export type BillingState = {
  loading: boolean;
  status: string;
  plan: string | null;
  current_period_end: string | null;
  isActive: boolean;
  error?: string | null;
};

export default function useBillingStatus(): BillingState {
  const [state, setState] = useState<BillingState>({
    loading: true,
    status: "none",
    plan: null,
    current_period_end: null,
    isActive: false,
    error: null,
  });

  useEffect(() => {
    (async () => {
      try {
        const res = await getBillingStatus();
        const isActive = res?.status === "active";
        setState({
          loading: false,
          status: res?.status ?? "none",
          plan: res?.plan ?? null,
          current_period_end: res?.current_period_end ?? null,
          isActive,
          error: null,
        });
      } catch (e: any) {
        setState((s) => ({
          ...s,
          loading: false,
          status: "none",
          isActive: false,
          error: e?.response?.data?.detail || null,
        }));
      }
    })();
  }, []);

  return state;
}
