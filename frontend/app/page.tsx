import { Shell } from "../components/layout";

export default function HomePage() {
  return (
    <Shell>
      <main>
        <section className="hero">
          <p className="eyebrow">Maritime logistics intelligence</p>
          <h1>See the voyage before it moves.</h1>
          <p className="lede">
            Navisail AI brings shipments, port conditions, forecasts, and operational decisions into
            one focused command surface.
          </p>
          <a className="action" href="/command-center">
            Open command center
          </a>
        </section>
        <section className="signal-grid" aria-label="Platform capabilities">
          <article>
            <span>01</span>
            <h2>Live context</h2>
            <p>Unify vessel, port, route, and shipment signals.</p>
          </article>
          <article>
            <span>02</span>
            <h2>Forecast ahead</h2>
            <p>Turn changing conditions into clear operational options.</p>
          </article>
          <article>
            <span>03</span>
            <h2>Act with traceability</h2>
            <p>Move from recommendation to approved execution with an audit trail.</p>
          </article>
        </section>
      </main>
    </Shell>
  );
}
