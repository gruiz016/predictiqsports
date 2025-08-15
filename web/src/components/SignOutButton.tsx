// web/src/components/SignOutButton.tsx
"use client";

import { logout } from "@/lib/api";
import { useRouter } from "next/navigation";

export default function SignOutButton({ className = "" }: { className?: string }){
  const router = useRouter();
  return (
    <button
      className={className || "border rounded px-3 py-2"}
      onClick={() => { logout(); router.replace("/login"); }}
    >
      Sign out
    </button>
  );
}
