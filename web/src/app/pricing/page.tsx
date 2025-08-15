// web/src/app/pricing/page.tsx
"use client";
import { checkout } from "@/lib/api";
export default function PricingPage(){
  async function go(plan:"monthly"|"quarterly"|"yearly"){ const {url}=await checkout(plan); window.location.href=url; }
  return (<main className="p-8 max-w-3xl mx-auto"><h1 className="text-2xl font-bold mb-6">Choose your plan</h1>
    <div className="grid gap-4 sm:grid-cols-3">
      <div className="border rounded p-4"><h2 className="font-semibold mb-2">Monthly</h2><button className="border rounded p-2 w-full" onClick={()=>go("monthly")}>Subscribe</button></div>
      <div className="border rounded p-4"><h2 className="font-semibold mb-2">Quarterly</h2><button className="border rounded p-2 w-full" onClick={()=>go("quarterly")}>Subscribe</button></div>
      <div className="border rounded p-4"><h2 className="font-semibold mb-2">Yearly</h2><button className="border rounded p-2 w-full" onClick={()=>go("yearly")}>Subscribe</button></div>
    </div>
    <p className="mt-6 text-sm opacity-70">You’ll be redirected to Stripe Checkout. Test cards accepted in dev.</p></main>); }
