import React, { useEffect, useState } from 'react';
import { LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

export default function Home() {
  const [volume, setVolume] = useState([]);
  const [errorPct, setErrorPct] = useState(0);
  const [topSrc, setTopSrc] = useState([]);

  useEffect(() => {
    const fetchAll = async () => {
      const v = await fetch('/api/mock/metrics/volume').then(r=>r.json());
      const e = await fetch('/api/mock/metrics/error').then(r=>r.json());
      const t = await fetch('/api/mock/metrics/top-src').then(r=>r.json());
      /*setVolume(v.data);*/ setErrorPct(e.error_pct); setTopSrc(t.rows);
      const formattedVolume = (v.data || []).map(d => ({...d,
      bucket: new Date(d.bucket).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}));
      setVolume(formattedVolume);

    };
    fetchAll();
    const id = setInterval(fetchAll, 3000);
    return () => clearInterval(id);
  }, []);

  return (
    <div style={{fontFamily:'ui-sans-serif, system-ui', padding: 24}}>
      <h1 style={{fontSize: 28, fontWeight: 700}}>Commlogs Dashboard</h1>
      <p style={{opacity: 0.7}}>Live volume, error rate, and top source IPs</p>

      <div style={{display:'grid', gridTemplateColumns:'1fr 1fr', gap: 24, marginTop: 24}}>
        <div style={{padding:16, border:'1px solid #eee', borderRadius:12}}>
          <h2>Logs per Minute</h2>
          <ResponsiveContainer width="100%" height={250}>
            <LineChart data={volume}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="bucket" />
              <YAxis />
              <Tooltip />
              <Line type="monotone" dataKey="logs" />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div style={{padding:16, border:'1px solid #eee', borderRadius:12}}>
          <h2>Error Rate (last 24h)</h2>
          <div style={{fontSize: 48, fontWeight: 700}}>{errorPct.toFixed(2)}%</div>
        </div>
      </div>

      <div style={{marginTop: 24, padding:16, border:'1px solid #eee', borderRadius:12}}>
        <h2>Top Source IPs</h2>
        <table style={{width:'100%', borderCollapse:'collapse'}}>
          <thead>
            <tr><th style={{textAlign:'left', padding:8}}>Source IP</th><th style={{textAlign:'left', padding:8}}>Count</th></tr>
          </thead>
          <tbody>
            {topSrc.map((row, idx) => (
              <tr key={idx}>
                <td style={{padding:8, borderTop:'1px solid #eee'}}>{row.src_ip}</td>
                <td style={{padding:8, borderTop:'1px solid #eee'}}>{row.c}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
