// web/src/components/RequireActive.tsx
"use client";
import { useEffect, useState } from "react";
import { getBillingStatus, startCheckout } from "@/src/lib/api";

export default function RequireActive({ children }: { children: React.ReactNode }) {
  const [loading, setLoading] = useState(true);
  const [active, setActive] = useState<boolean | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;
    (async () => {
      try {
        const s = await getBillingStatus();
        if (!mounted) return;
        setActive(!!s.active);
      } catch (e: any) {
        setError(e?.message || "Failed to load subscription status");
        setActive(false);
      } finally {
        setLoading(false);
      }
    })();
    return () => { mounted = false; };
  }, []);

  if (loading) {
    return <div className="p-6">Checking subscription…</div>;
  }
  if (error) {
    return (
      <div className="p-6 space-y-2">
        <div className="font-semibold">We couldn’t verify your subscription.</div>
        <div className="text-sm opacity-80">{error}</div>
      </div>
    );
  }
  if (!active) {
    const goCheckout = async () => {
      const url = await startCheckout("monthly");
      window.location.href = url;
    };
    return (
      <div className="p-8 rounded-2xl border shadow-sm max-w-xl mx-auto mt-10 text-center space-y-4">
        <h2 className="text-xl font-semibold">Premium feature</h2>
        <p className="text-sm opacity-80">
          A paid subscription is required to access this page. See our past performance on the Track Record page, or subscribe now.
        </p>
        <div className="flex items-center justify-center gap-3">
          <a className="px-4 py-2 rounded-xl border" href="/track-record">View Track Record</a>
          <button onClick={goCheckout} className="px-4 py-2 rounded-xl bg-black text-white">Subscribe</button>
        </div>
      </div>
    );
  }
  return <>{children}</>;
}
