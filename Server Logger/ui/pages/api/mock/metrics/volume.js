const base = process.env.COLLECTOR_API_BASE || "http://localhost:8080";

export default async function handler(req, res) {
  try{
    const url = new URL("/metrics/volume", base);
    //FWD Query params
    for (const [k, v] of Object.entries(req.query)) url.searchParams.set(k,v);
    const resp = await fetch(url, { method: "GET" });
    if (!resp.ok) throw new Error(`collector ${resp.status}`);
    const json = await resp.json();
    res.status(200).json(json);
  } catch(err){
    console.error(err);
    res.status(500).json({ error: "failed to load volume metrics"});
  }

}



/*        Dummy handler:

//SELECT date_trunc($1, ts) AS bucket, count(*) FROM logs WHERE ts BETWEEN $2 AND $3 GROUP BY 1 ORDER BY 1;
export default function handler(req, res) {
  const now = Date.now();
  // Generate 60 minutes of sample buckets
  const data = Array.from({length: 60}).map((_, i) => ({
    bucket: new Date(now - (59 - i) * 60000).toLocaleTimeString([], {hour:'2-digit', minute:'2-digit'}),
    logs: Math.floor(50 + Math.random() * 200)
  }));
  res.status(200).json({ data });
}

*/