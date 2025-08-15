// web/src/app/logout/page.tsx
"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { logout } from "@/lib/api";

export default function LogoutPage(){
  const router = useRouter();
  useEffect(()=>{
    logout();
    router.replace("/login");
  },[router]);
  return (
    <main className="p-8 max-w-2xl mx-auto">
      <h1 className="text-2xl font-bold mb-2">Signing out…</h1>
      <p className="opacity-70">You’ll be redirected to the login page.</p>
    </main>
  );
}
