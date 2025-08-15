// web/src/app/page.tsx
export default function Home() {
  return (
    <main className="p-8 max-w-4xl mx-auto">
      <h1 className="text-3xl font-bold mb-4">Sports Prediction & Parlay Platform</h1>
      <p className="mb-6">
        Transparent MLB predictions with a paid-only access model. Public accuracy. No free picks.
      </p>
      <ul className="list-disc pl-6 space-y-2">
        <li><a className="underline" href="/track-record">Track Record (public)</a></li>
        <li><a className="underline" href="/accuracy">Accuracy (public)</a></li>
        <li><a className="underline" href="/dashboard">Today’s Predictions (paid)</a></li>
        <li><a className="underline" href="/parlay">Parlay Builder (paid)</a></li>
      </ul>
    </main>
  );
}
