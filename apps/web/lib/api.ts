const API=process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
export async function getJson<T>(path:string):Promise<T>{
  try{const r=await fetch(`${API}${path}`,{headers:{'X-Tenant-ID':'demo-manufacturing'},cache:'no-store'}); if(!r.ok) throw new Error(`${r.status}`); return await r.json() as T}
  catch{return [] as T}
}
