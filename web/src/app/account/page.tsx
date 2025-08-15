// web/src/app/account/page.tsx
"use client";

import { useEffect, useState } from "react";
import { getBillingStatus, openPortal, syncCheckout } from "@/lib/api";
import { useSearchParams } from "next/navigation";

type Billing = { status: string; plan?: string | null; current_period_end?: string | null; stripe_customer_id?: string | null };

export default function AccountPage(){
  const [billing, setBilling] = useState<Billing | null>(null);
  const [error, setError] = useState<string | null>(null);
  const search = useSearchParams();

  useEffect(() => {
    const run = async () => {
      try {
        const status = search.get("status");
        const session_id = search.get("session_id");
        if (status === "success" && session_id) {
          await syncCheckout(session_id);
        }
        const b = await getBillingStatus();
        setBilling(b);
      } catch (e: any) {
        setError(e?.response?.data?.detail || "Failed to load billing status");
      }
    };
    run();
  }, [search]);

  async function handlePortal(){
    try {
      const { url } = await openPortal();
      window.location.href = url;
    } catch (e: any) {
      setError(e?.response?.data?.detail || "Could not open billing portal");
    }
  }

  return (
    <main className="p-8 max-w-2xl mx-auto">
      <h1 className="text-2xl font-bold mb-4">Account</h1>
      {error && <div className="text-red-600 text-sm mb-4">{error}</div>}
      {!billing ? <div>Loading…</div> : (
        <div className="space-y-2">
          <div><span className="font-semibold">Status:</span> {billing.status}</div>
          <div><span className="font-semibold">Plan:</span> {billing.plan ?? "—"}</div>
          <div><span className="font-semibold">Renews:</span> {billing.current_period_end ?? "—"}</div>
          <div className="mt-4">
            <button className="border rounded p-2" onClick={handlePortal} disabled={!billing.stripe_customer_id}>
              Open Billing Portal
            </button>
          </div>
          <p className="text-sm opacity-70 mt-2">Use the billing portal to update payment method or cancel.</p>
        </div>
      )}
    </main>
  );
}
