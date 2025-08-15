// web/src/app/track-record/page.tsx
"use client";

import { useEffect, useState } from "react";
import { fetchHistory } from "@/lib/api";

export default function TrackRecordPage(){
  const [data,setData] = useState<any[] | null>(null);
  const [error,setError] = useState<string | null>(null);

  useEffect(()=>{
    (async () => {
      try{
        const rows = await fetchHistory();
        setData(Array.isArray(rows) ? rows : []);
      }catch(e:any){
        setError(e?.response?.data?.detail || "Failed to load");
        setData([]);
      }
    })();
  },[]);

  return (
    <main className="p-8 max-w-5xl mx-auto">
      <h1 className="text-2xl font-bold mb-4">Track Record</h1>
      {error && <div className="text-red-600 text-sm mb-4">{error}</div>}
      {data === null ? <div>Loading…</div> : (
        data.length === 0 ? <div className="opacity-70">No history yet.</div> : (
          <table className="w-full border-collapse">
            <thead>
              <tr>
                <th className="border p-2 text-left">Date</th>
                <th className="border p-2 text-left">Matchup</th>
                <th className="border p-2 text-left">Predicted Winner</th>
                <th className="border p-2 text-left">Actual</th>
                <th className="border p-2 text-left">W/L</th>
              </tr>
            </thead>
            <tbody>
            {data.map((row:any)=>{
              const predictedWinner = (row?.p_home_win ?? 0) >= 0.5 ? row?.home ?? "HOME" : row?.away ?? "AWAY";
              const actual = row?.result ? `${row.result.home_runs}-${row.result.away_runs}` : "TBD";
              const wl = row?.result ? (row.result.win ? "✅" : "❌") : "—";
              return (
                <tr key={row?.game_id ?? Math.random()}>
                  <td className="border p-2">{row?.date ?? "—"}</td>
                  <td className="border p-2">{row?.away ?? "—"} @ {row?.home ?? "—"}</td>
                  <td className="border p-2">{predictedWinner}</td>
                  <td className="border p-2">{actual}</td>
                  <td className="border p-2">{wl}</td>
                </tr>
              );
            })}
            </tbody>
          </table>
        )
      )}
    </main>
  );
}
