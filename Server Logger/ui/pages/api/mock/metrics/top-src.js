const base = process.env.COLLECTOR_API_BASE || "http://localhost:8080";

export default async function handler(req, res) {
  try {
    const url = new URL("/metrics/top-src", base);
    for (const [k, v] of Object.entries(req.query)) url.searchParams.set(k, v);
    const resp = await fetch(url);
    if (!resp.ok) throw new Error(`collector ${resp.status}`);
    res.status(200).json(await resp.json());
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: "failed to load top sources" });
  }
}


/*Dummy function

export default function handler(req, res) {
  const rows = Array.from({length: 8}).map((_, i) => ({
    src_ip: `10.0.1.${i+10}`,
    c: Math.floor(50 + Math.random() * 500)
  }));
  res.status(200).json({ rows });
}
  */