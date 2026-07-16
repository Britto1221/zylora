import Link from "next/link";

export function PageHeader({
  eyebrow,
  title,
  description,
  actions,
}: {
  eyebrow: string;
  title: string;
  description?: string;
  actions?: React.ReactNode;
}) {
  return (
    <header className="page-head">
      <div>
        <p className="eyebrow">{eyebrow}</p>
        <h1>{title}</h1>
        {description ? <p className="lede">{description}</p> : null}
      </div>
      {actions ? <div className="actions">{actions}</div> : null}
    </header>
  );
}

export function Metric({
  label,
  value,
  foot,
}: {
  label: string;
  value: React.ReactNode;
  foot?: string;
}) {
  return (
    <article className="metric">
      <div className="metric-label">{label}</div>
      <div className="metric-value">{value}</div>
      {foot ? <div className="metric-foot">{foot}</div> : null}
    </article>
  );
}

export function Panel({
  title,
  description,
  action,
  children,
  flush = false,
}: {
  title: string;
  description?: string;
  action?: React.ReactNode;
  children: React.ReactNode;
  flush?: boolean;
}) {
  return (
    <section className="panel">
      <header className="panel-head">
        <div>
          <h2>{title}</h2>
          {description ? <p>{description}</p> : null}
        </div>
        {action}
      </header>
      <div className={`panel-body${flush ? " flush" : ""}`}>{children}</div>
    </section>
  );
}

export function Badge({
  children,
  dark = false,
  soft = false,
}: {
  children: React.ReactNode;
  dark?: boolean;
  soft?: boolean;
}) {
  return <span className={`badge${dark ? " dark" : ""}${soft ? " soft" : ""}`}>{children}</span>;
}

export function Empty({
  title,
  description,
  actionHref,
  actionLabel,
}: {
  title: string;
  description: string;
  actionHref?: string;
  actionLabel?: string;
}) {
  return (
    <div className="empty">
      <div>
        <strong>{title}</strong>
        <p>{description}</p>
        {actionHref && actionLabel ? (
          <Link href={actionHref} className="button secondary small" style={{ marginTop: 15 }}>
            {actionLabel}
          </Link>
        ) : null}
      </div>
    </div>
  );
}

export function DateText({ value }: { value?: string | null }) {
  if (!value) return <span className="cell-sub">Not set</span>;
  const date = new Date(value);
  return <span>{Number.isNaN(date.getTime()) ? value : date.toLocaleString()}</span>;
}
