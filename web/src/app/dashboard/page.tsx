// web/src/app/dashboard/page.tsx
"use client";

import { useEffect, useState } from "react";
import { fetchTodaysPredictions, getToken } from "@/lib/api";
import { useRouter } from "next/navigation";
import RequirePro from "@/components/RequirePro";

function DashboardInner(){
  const [data,setData]=useState<any[]|null>(null);
  const [error,setError]=useState<string|null>(null);
  useEffect(()=>{
    fetchTodaysPredictions().then(setData).catch((err:any)=>setError(err?.response?.data?.detail||"Failed to load predictions"));
  },[]);
  return (
    <main className="p-8 max-w-5xl mx-auto">
      <h1 className="text-2xl font-bold mb-4">Today’s Predictions</h1>
      {error && <div className="text-red-600 text-sm mb-4">{error}</div>}
      {!data ? <div>Loading…</div> : <div className="grid gap-4">{data.map((p:any)=>(
        <div key={p.game_id} className="border rounded p-4">
          <div className="font-semibold">{p.away} @ {p.home} — {p.date}</div>
          <div className="text-sm mt-2">Home win prob: {(p.p_home_win*100).toFixed(1)}%</div>
          <div className="text-sm">Expected total: {p.expected_total ?? "—"}</div>
          <div className="text-sm">Confidence: {p.confidence ? (p.confidence*100).toFixed(1) + "%" : "—"}</div>
        </div>
      ))}</div>}
    </main>
  );
}

export default function DashboardPage(){
  const router = useRouter();
  const [ready, setReady] = useState(false);
  useEffect(()=>{
    // Only run client-side after mount to avoid SSR "location is not defined"
    if (!getToken()) {
      router.replace("/login");
      return;
    }
    setReady(true);
  },[router]);
  if (!ready) return null; // or a small spinner
  return (<RequirePro><DashboardInner/></RequirePro>);
}
