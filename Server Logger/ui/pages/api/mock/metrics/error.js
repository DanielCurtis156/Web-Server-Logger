const base = process.env.COLLECTOR_API_BASE || "http://localhost:8080";

export default async function handler(req, res) {
  try {
    const url = new URL("/metrics/error", base);
    for (const [k, v] of Object.entries(req.query)) url.searchParams.set(k, v);
    const resp = await fetch(url);
    if (!resp.ok) throw new Error(`collector ${resp.status}`);
    const json = await resp.json();
    res.status(200).json(json);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: "failed to load error metrics" });
  }
}
