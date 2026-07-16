const metrics = [
  ["Clients", "0"],
  ["Published websites", "0"],
  ["New leads", "0"],
  ["Domains expiring", "0"],
  ["Skipped WhatsApp messages", "0"],
  ["Pending SEO audits", "0"],
];

export default function AdminDashboard() {
  return (
    <main>
      <p className="muted">Super Admin</p>
      <h1>Zylora Control Centre</h1>
      <div className="grid grid-3">
        {metrics.map(([label, value]) => (
          <section className="card" key={label}>
            <div className="muted">{label}</div>
            <strong style={{ fontSize: 32 }}>{value}</strong>
          </section>
        ))}
      </div>
    </main>
  );
}
