export default function handler(req, res) {
  const rows = Array.from({length: 8}).map((_, i) => ({
    src_ip: `10.0.1.${i+10}`,
    c: Math.floor(50 + Math.random() * 500)
  }));
  res.status(200).json({ rows });
}