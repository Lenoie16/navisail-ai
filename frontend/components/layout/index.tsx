"use client";

import Link from "next/link";
import type { ReactNode } from "react";
import { usePathname } from "next/navigation";

const links = [
  ["Command Center", "/command-center"],
  ["Shipments", "/shipments"],
  ["Freight Intelligence", "/freight-intelligence"],
  ["Port Intelligence", "/ports"],
  ["Contract Strategy", "/contracts"],
  ["Scenario Lab", "/risk"],
  ["Recommendations", "/recommendations"],
  ["AI Copilot", "/copilot"],
  ["Execution", "/execution"],
  ["Audit", "/audit"],
];

export function Shell({ children, sessionId }: { children: ReactNode; sessionId?: string }) {
  const pathname = usePathname();

  return (
    <div className="shell">
      <a className="skip-link" href="#main-content">
        Skip to main content
      </a>
      <aside className="shell__sidebar">
        <Link className="brand" href="/">
          <span className="brand__mark" aria-hidden="true">⌁</span>
          <span><strong>NAVISAIL AI</strong><small>SAIL Maritime Intelligence</small></span>
        </Link>
        <Link className="sidebar-cta" href="/shipments">＋ Plan new shipment</Link>
        <nav className="nav" aria-label="Primary navigation">
          {links.map(([label, href]) => (
            <Link
              key={href}
              className={pathname === href ? "nav__link nav__link--active" : "nav__link"}
              aria-current={pathname === href ? "page" : undefined}
              href={sessionId ? `${href}?session=${encodeURIComponent(sessionId)}` : href}
            >
              <span className="nav__icon" aria-hidden="true">{["⌂", "▣", "◈", "⚓", "◇", "◌", "✦", "✧", "▶", "≡"][links.findIndex((item) => item[1] === href)]}</span>
              {label}
              {label === "AI Copilot" && <span className="nav__new">NEW</span>}
            </Link>
          ))}
        </nav>
        <div className="sidebar-footer"><span className="avatar">SA</span><span><strong>SAIL User</strong><small>Operations</small></span></div>
      </aside>
      <div className="shell__content" id="main-content">{children}</div>
    </div>
  );
}

export function ScreenPlaceholder({ title, description }: { title: string; description: string }) {
  return (
    <Shell>
      <main className="dashboard">
        <header className="dashboard__header">
          <div>
            <p className="eyebrow">NAVISAIL workspace</p>
            <h1>{title}</h1>
            <p>{description}</p>
          </div>
          <span className="status-badge status-badge--demo">DEMO</span>
        </header>
        <section className="glass-panel">
          <h2>Awaiting authoritative data</h2>
          <p className="lede">
            This surface is ready for connected maritime state. Demo and synthetic signals remain
            clearly labeled until a source is available.
          </p>
        </section>
      </main>
    </Shell>
  );
}
