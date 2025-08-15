// web/src/app/parlay/page.tsx
"use client";
import RequireActive from "@/src/components/RequireActive";
import { useState } from "react";
import { buildParlay } from "@/src/lib/api";

type Pick = { market: string; selection: string; odds_type: "american"|"decimal"; odds: number };

export default function ParlayPage() {
  const [picks, setPicks] = useState<Pick[]>([
    { market: "ML", selection: "NYY ML", odds_type: "american", odds: -135 },
  ]);
  const [stake, setStake] = useState(10);
  const [result, setResult] = useState<any | null>(null);
  const [error, setError] = useState<string | null>(null);

  const addPick = () => setPicks([...picks, { market: "ML", selection: "", odds_type: "american", odds: 100 }]);
  const updatePick = (i: number, v: Partial<Pick>) => setPicks(picks.map((p, idx) => (idx === i ? { ...p, ...v } : p)));

  const calculate = async () => {
    setError(null); setResult(null);
    try {
      const res = await buildParlay({ stake, picks });
      setResult(res);
    } catch (e: any) {
      setError(e?.message || "Failed to build parlay");
    }
  };

  return (
    <RequireActive>
      <div className="p-6 space-y-4">
        <h1 className="text-2xl font-semibold">Parlay Builder</h1>
        {picks.map((p, i) => (
          <div key={i} className="grid grid-cols-1 md:grid-cols-4 gap-2 items-center">
            <input className="border rounded-xl px-3 py-2" value={p.market} onChange={e=>updatePick(i,{market:e.target.value})} placeholder="Market" />
            <input className="border rounded-xl px-3 py-2" value={p.selection} onChange={e=>updatePick(i,{selection:e.target.value})} placeholder="Selection" />
            <select className="border rounded-xl px-3 py-2" value={p.odds_type} onChange={e=>updatePick(i,{odds_type:e.target.value as any})}>
              <option value="american">American</option>
              <option value="decimal">Decimal</option>
            </select>
            <input className="border rounded-xl px-3 py-2" type="number" value={p.odds} onChange={e=>updatePick(i,{odds: Number(e.target.value)})} placeholder="Odds" />
          </div>
        ))}
        <div className="flex gap-2">
          <button onClick={addPick} className="px-3 py-2 rounded-xl border">+ Add leg</button>
          <input className="border rounded-xl px-3 py-2" type="number" value={stake} onChange={e=>setStake(Number(e.target.value))} placeholder="Stake" />
          <button onClick={calculate} className="px-4 py-2 rounded-xl bg-black text-white">Calculate</button>
        </div>
        {error && <div className="text-red-600 text-sm">{error}</div>}
        {result && (
          <div className="p-4 rounded-2xl border inline-block">
            <div>Legs: <b>{result.legs}</b></div>
            <div>Combined decimal: <b>{result.combined_decimal}</b></div>
            <div>Combined American: <b>{result.combined_american}</b></div>
            <div>Potential payout: <b>${result.potential_payout}</b></div>
            <div>Potential profit: <b>${result.potential_profit}</b></div>
          </div>
        )}
      </div>
    </RequireActive>
  );
}
