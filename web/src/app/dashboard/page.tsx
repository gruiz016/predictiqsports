// web/src/app/dashboard/page.tsx
"use client";
import RequireActive from "@/src/components/RequireActive";
import { useEffect, useState } from "react";
import { getTodayPredictions } from "@/src/lib/api";

export default function DashboardPage() {
  const [data, setData] = useState<any[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    (async () => {
      try {
        const res = await getTodayPredictions();
        setData(res);
      } catch (e: any) {
        setError(e?.message || "Failed to load predictions");
      }
    })();
  }, []);

  return (
    <RequireActive>
      <div className="p-6 space-y-4">
        <h1 className="text-2xl font-semibold">Today’s Predictions</h1>
        {error && <div className="text-red-600 text-sm">{error}</div>}
        {!data && !error && <div>Loading…</div>}
        {data && (
          <div className="overflow-x-auto">
            <table className="min-w-full text-sm">
              <thead>
                <tr className="text-left border-b">
                  <th className="py-2 pr-4">Game</th>
                  <th className="py-2 pr-4">Pick</th>
                  <th className="py-2 pr-4">Predicted</th>
                  <th className="py-2 pr-4">Confidence</th>
                  <th className="py-2 pr-4">Odds</th>
                </tr>
              </thead>
              <tbody>
                {data.map((r, i) => (
                  <tr key={i} className="border-b last:border-0">
                    <td className="py-2 pr-4">{r.away_team} @ {r.home_team}</td>
                    <td className="py-2 pr-4">{r.pick}</td>
                    <td className="py-2 pr-4">{r.predicted_score_away ?? "–"}–{r.predicted_score_home ?? "–"}</td>
                    <td className="py-2 pr-4">{(r.model_confidence ?? 0)*100}%</td>
                    <td className="py-2 pr-4">{r.odds_american ?? ""}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </RequireActive>
  );
}
