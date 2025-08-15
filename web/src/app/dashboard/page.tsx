// web/src/app/dashboard/page.tsx
import { fetchTodaysPredictions } from "@/lib/api";

export default async function DashboardPage() {
  // For MVP dev, no token provided; backend may run with DEV_SKIP_AUTH=true
  const data = await fetchTodaysPredictions();
  return (
    <main className="p-8 max-w-5xl mx-auto">
      <h1 className="text-2xl font-bold mb-4">Today’s Predictions</h1>
      <div className="grid gap-4">
        {data.map((p: any) => (
          <div key={p.game_id} className="border rounded p-4">
            <div className="font-semibold">{p.away} @ {p.home} — {p.date}</div>
            <div className="text-sm mt-2">Home win prob: {(p.p_home_win*100).toFixed(1)}%</div>
            <div className="text-sm">Expected total: {p.expected_total ?? "—"}</div>
            <div className="text-sm">Confidence: {p.confidence ? (p.confidence*100).toFixed(1) + "%" : "—"}</div>
          </div>
        ))}
      </div>
      <p className="mt-6 text-sm opacity-70">Access will be gated by subscription in production.</p>
    </main>
  );
}
