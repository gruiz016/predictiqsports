// web/src/app/account/page.tsx
"use client";
import { useEffect, useState } from "react";
import { billingStatus, portalSession, syncCheckout } from "@/lib/api";
import { useSearchParams } from "next/navigation";
import Link from "next/link";

export default function AccountPage(){
  const [status,setStatus] = useState<any|null>(null);
  const [err,setErr] = useState<string|null>(null);
  const [working,setWorking] = useState(false);
  const search = useSearchParams();

  async function load(){
    setErr(null);
    try{ const data = await billingStatus(); setStatus(data); }
    catch(e:any){ setErr(e?.response?.data?.detail || e?.message || "Failed to fetch status"); }
  }

  async function manageBilling(){
    setWorking(true); setErr(null);
    try{ const { url } = await portalSession(); window.location.href = url; }
    catch(e:any){ setErr(e?.response?.data?.detail || e?.message || "Failed to open portal"); }
    finally{ setWorking(false); }
  }

  useEffect(()=>{
    const sid = search.get("session_id");
    if(sid){
      // One-time sync after returning from Stripe
      syncCheckout(sid).finally(load);
    }else{
      load();
    }
  },[search]);

  return (
    <main className="p-8 max-w-2xl mx-auto">
      <h1 className="text-2xl font-bold mb-2">Account</h1>
      <p className="opacity-70 text-sm mb-4">This page shows your subscription status after Stripe checkout.</p>

      {err && <div className="mb-3 text-sm text-red-700 border border-red-500 rounded p-2">{err}</div>}

      {!status ? <div>Loading…</div> : (
        <div className="border rounded p-4 space-y-2">
          <div><span className="font-semibold">Active:</span> {String(status.active)}</div>
          <div><span className="font-semibold">Status:</span> {status.status ?? "—"}</div>
          <div><span className="font-semibold">Plan:</span> {status.plan ?? "—"}</div>
          <div><span className="font-semibold">Current period end:</span> {status.current_period_end ?? "—"}</div>
          {!status.active ? (
            <div className="pt-2">
              <Link href="/pricing" className="underline">Subscribe now</Link>
            </div>
          ) : (
            <div className="pt-2">
              <button onClick={manageBilling} className="border rounded p-2" disabled={working}>
                {working ? "Opening portal…" : "Manage billing"}
              </button>
            </div>
          )}
          <div className="pt-2">
            <button onClick={load} className="border rounded p-2">Refresh status</button>
          </div>
        </div>
      )}
    </main>
  );
}
