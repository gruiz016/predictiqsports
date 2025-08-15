// web/src/app/login/page.tsx
"use client";
import { useState } from "react";
import { login, setToken } from "@/lib/api";
import { useRouter } from "next/navigation";
export default function LoginPage(){
  const [email,setEmail]=useState(""); const [password,setPassword]=useState(""); const [error,setError]=useState<string|null>(null); const router=useRouter();
  async function onSubmit(e:React.FormEvent){ e.preventDefault(); setError(null);
    try{ const res=await login(email,password); setToken(res.token); router.push("/dashboard"); }catch(err:any){ setError(err?.response?.data?.detail||"Login failed"); } }
  return (<main className="p-8 max-w-md mx-auto"><h1 className="text-2xl font-bold mb-4">Log in</h1>
    <form onSubmit={onSubmit} className="space-y-3">
      <input className="border rounded p-2 w-full" placeholder="Email" value={email} onChange={e=>setEmail(e.target.value)}/>
      <input className="border rounded p-2 w-full" placeholder="Password" type="password" value={password} onChange={e=>setPassword(e.target.value)}/>
      <button className="border rounded p-2 w-full" type="submit">Log in</button>
      {error && <div className="text-red-600 text-sm">{error}</div>}
    </form>
    <p className="mt-4 text-sm">No account? <a className="underline" href="/register">Register</a></p></main>); }
