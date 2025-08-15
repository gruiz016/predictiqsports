// web/src/app/parlay/page.tsx
"use client";

import { useState } from "react";
import { api } from "@/lib/api";

export default function ParlayPage() {
  const [stake, setStake] = useState(1000);
  const [result, setResult] = useState<any>(null);
  const [legs, setLegs] = useState<any[]>([
    { game_id: "uuid-today-1", market: "ML", selection: "HOME", price_decimal: 1.7, leg_probability: 0.6 },
    { game_id: "uuid-today-2", market: "TOTAL", selection: "OVER", line: 8.5, price_decimal: 1.95, leg_probability: 0.55 }
  ]);

  async function evaluate() {
    const res = await api.post("/v1/parlays/evaluate", { stake_cents: stake, legs });
    setResult(res.data);
  }

  return (
    <main className="p-8 max-w-3xl mx-auto">
      <h1 className="text-2xl font-bold mb-4">Parlay Builder</h1>

      <div className="border rounded p-4">
        <label className="block text-sm mb-1">Stake (cents)</label>
        <input className="border rounded p-2 w-full"
          type="number" value={stake} onChange={e => setStake(parseInt(e.target.value || "0", 10))}/>
      </div>

      <div className="mt-4 space-y-2">
        <div className="text-sm opacity-70">Sample legs (MVP)</div>
        {legs.map((l, i) => (
          <div key={i} className="border rounded p-3 text-sm">
            <div>Market: {l.market}, Selection: {l.selection}</div>
            <div>Decimal Odds: {l.price_decimal}, P(leg): {Math.round(l.leg_probability*100)}%</div>
            {l.line ? <div>Line: {l.line}</div> : null}
          </div>
        ))}
      </div>

      <button className="mt-4 border rounded p-2" onClick={evaluate}>Evaluate EV</button>

      {result && (
        <div className="mt-4 border rounded p-4">
          <div>Combined odds: {result.combined_decimal_odds}</div>
          <div>P(parlay win): {(result.p_parlay_win*100).toFixed(2)}%</div>
          <div>Expected value: {result.expected_value_cents}¢ ({result.ev_positive ? "✅ positive" : "❌ negative"})</div>
        </div>
      )}
      <p className="mt-6 text-sm opacity-70">Gating + correlation adjustments coming in Phase 3.</p>
    </main>
  );
}
