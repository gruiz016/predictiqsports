// web/src/components/RequirePro.tsx
"use client";

import useBillingStatus from "@/hooks/useBillingStatus";
import Link from "next/link";
import React from "react";

export default function RequirePro({ children }: { children: React.ReactNode }) {
  const { loading, isActive, status } = useBillingStatus();

  if (loading) {
    return <main className="p-8 max-w-4xl mx-auto">Loading…</main>;
  }

  if (!isActive) {
    return (
      <main className="p-8 max-w-3xl mx-auto">
        <h1 className="text-2xl font-bold mb-4">Upgrade to access</h1>
        <p className="mb-4">
          This feature is available for active subscribers. Your current status is{" "}
          <span className="font-semibold">{status || "none"}</span>.
        </p>
        <div className="flex gap-3">
          <Link href="/pricing" className="border rounded px-4 py-2">View Plans</Link>
          <Link href="/account" className="border rounded px-4 py-2">Account</Link>
        </div>
      </main>
    );
  }

  return <>{children}</>;
}
