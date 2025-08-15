// web/src/app/register/page.tsx
"use client";
import { useState } from "react";
import { register, setToken } from "@/lib/api";
import { useRouter } from "next/navigation";
export default function RegisterPage(){
  const [email,setEmail]=useState(""); const [password,setPassword]=useState(""); const [error,setError]=useState<string|null>(null); const router=useRouter();
  async function onSubmit(e:React.FormEvent){ e.preventDefault(); setError(null);
    try{ const res=await register(email,password); setToken(res.token); router.push("/dashboard"); }catch(err:any){ setError(err?.response?.data?.detail||"Registration failed"); } }
  return (<main className="p-8 max-w-md mx-auto"><h1 className="text-2xl font-bold mb-4">Create your account</h1>
    <form onSubmit={onSubmit} className="space-y-3">
      <input className="border rounded p-2 w-full" placeholder="Email" value={email} onChange={e=>setEmail(e.target.value)}/>
      <input className="border rounded p-2 w-full" placeholder="Password (6+ chars)" type="password" value={password} onChange={e=>setPassword(e.target.value)}/>
      <button className="border rounded p-2 w-full" type="submit">Create account</button>
      {error && <div className="text-red-600 text-sm">{error}</div>}
    </form>
    <p className="mt-4 text-sm">Already have an account? <a className="underline" href="/login">Log in</a></p></main>); }
