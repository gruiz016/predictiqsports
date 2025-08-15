// web/src/app/parlay/page.tsx
"use client";

import RequirePro from "@/components/RequirePro";
import { getToken } from "@/lib/api";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

function ParlayInner(){
  return (
    <main className="p-8 max-w-5xl mx-auto">
      <h1 className="text-2xl font-bold mb-4">Parlay Builder</h1>
      <p className="opacity-80">(Coming in Phase 3) Build multi-leg parlays from today’s predictions and see combined odds & EV.</p>
    </main>
  );
}

export default function ParlayPage(){
  const router = useRouter();
  const [ready, setReady] = useState(false);
  useEffect(()=>{
    if (!getToken()) {
      router.replace("/login");
      return;
    }
    setReady(true);
  },[router]);
  if (!ready) return null;
  return (<RequirePro><ParlayInner/></RequirePro>);
}
