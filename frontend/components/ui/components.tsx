import React, { type ReactNode } from "react";

export type DataStatus = "LIVE" | "DELAYED" | "ESTIMATED" | "SYNTHETIC" | "DEMO";

export function Button({
  children,
  variant = "primary",
  ...props
}: React.ButtonHTMLAttributes<HTMLButtonElement> & { variant?: "primary" | "quiet" }) {
  return (
    <button className={`button button--${variant}`} {...props}>
      {children}
    </button>
  );
}
export function Input(props: React.InputHTMLAttributes<HTMLInputElement>) {
  return <input className={`control ${props.className ?? ""}`} {...props} />;
}
export function Select({ children, ...props }: React.SelectHTMLAttributes<HTMLSelectElement>) {
  return <select className={`control ${props.className ?? ""}`} {...props}>{children}</select>;
}
export function DateSelector(props: React.InputHTMLAttributes<HTMLInputElement>) {
  return <Input type="date" {...props} />;
}
export function MetricCard({
  label,
  value,
  hint,
}: {
  label: string;
  value: ReactNode;
  hint?: ReactNode;
}) {
  return (
    <article className="metric-card card-surface">
      <span className="metric-card__label">{label}</span>
      <strong className="metric-card__value">{value}</strong>
      {hint && <small className="metric-card__hint">{hint}</small>}
    </article>
  );
}
export function StatusBadge({ status }: { status: DataStatus }) {
  return (
    <span
      className={`status-badge status-badge--${status.toLowerCase()}`}
      aria-label={`Data status: ${status}`}
    >
      {status}
    </span>
  );
}
export function ConfidenceIndicator({ value }: { value: number }) {
  return (
    <span aria-label={`Confidence ${Math.round(value * 100)} percent`}>
      Confidence {Math.round(value * 100)}%
    </span>
  );
}
export function RiskIndicator({ level }: { level: "low" | "medium" | "high" }) {
  return (
    <span
      className={`status-badge status-badge--${level === "high" ? "delayed" : level === "medium" ? "estimated" : "live"}`}
    >
      Risk {level}
    </span>
  );
}
export function DataTable({ headers, rows }: { headers: string[]; rows: ReactNode[][] }) {
  return (
    <div role="region" aria-label="Data table" tabIndex={0}>
      <table>
        <thead>
          <tr>
            {headers.map((header) => (
              <th key={header}>{header}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, index) => (
            <tr key={index}>
              {row.map((cell, cellIndex) => (
                <td key={cellIndex}>{cell}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
export function ChartContainer({ title, children }: { title: string; children: ReactNode }) {
  return (
    <section className="glass-panel card-surface" aria-label={title}>
      <h2>{title}</h2>
      {children}
    </section>
  );
}
export function RecommendationCard({ title, children }: { title: string; children: ReactNode }) {
  return (
    <section className="glass-panel">
      <h2>{title}</h2>
      {children}
    </section>
  );
}
export function Timeline({ items }: { items: string[] }) {
  return (
    <ol className="data-list">
      {items.map((item) => (
        <li key={item}>
          <strong>{item}</strong>
          <span>Tracked</span>
        </li>
      ))}
    </ol>
  );
}
export function EmptyState({ title }: { title: string }) {
  return (
    <section className="glass-panel">
      <h2>{title}</h2>
      <p className="lede">No authoritative data is available for this view.</p>
    </section>
  );
}
export function LoadingState() {
  return (
    <p className="state-message" role="status" aria-live="polite">
      Loading maritime intelligence…
    </p>
  );
}
export function ErrorState({ message }: { message: string }) {
  return (
    <p className="state-message state-message--error" role="alert">
      {message}
    </p>
  );
}
export function Drawer({ children }: { children: ReactNode }) {
  return (
    <aside className="glass-panel" aria-label="Drawer">
      {children}
    </aside>
  );
}
export function Modal({ children }: { children: ReactNode }) {
  return (
    <div role="dialog" aria-modal="true" className="glass-panel">
      {children}
    </div>
  );
}
export function CommandPalette({ children }: { children: ReactNode }) {
  return (
    <div role="search" className="glass-panel">
      {children}
    </div>
  );
}
export function Toast({ children }: { children: ReactNode }) {
  return (
    <div role="status" className="glass-panel">
      {children}
    </div>
  );
}
