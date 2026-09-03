"use client";

import { useState } from "react";
import { Shell } from "../../components/layout";
import { Button, ErrorState, Input, StatusBadge } from "../../components/ui";
import { runCopilotAgent, type CopilotAgentEvent } from "../../lib/api";
import {
  eventActivity,
  sourceReferences,
  suggestedQuestions,
  type CopilotMessage,
} from "../../state/copilot";

const sessionId = "default";
const sourceSnapshot = "current-decision-session";

function AgentEvents({ events }: { events: CopilotAgentEvent[] }) {
  return (
    <ul className="copilot-events" aria-label="Tool activity">
      {events.map((event, index) => (
        <li key={`${event.type}-${index}`}>
          <span className="status-badge status-badge--estimated">
            {eventActivity(event) ?? event.type.replaceAll("_", " ")}
          </span>
          <span>{event.message}</span>
        </li>
      ))}
    </ul>
  );
}

export default function CopilotPage() {
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState<CopilotMessage[]>([]);
  const [status, setStatus] = useState<"idle" | "running" | "failed">("idle");
  const [error, setError] = useState<string | null>(null);

  async function submitQuestion(value = question) {
    const trimmed = value.trim();
    if (!trimmed || status === "running") return;
    setQuestion("");
    setError(null);
    setStatus("running");
    setMessages((current) => [
      ...current,
      { id: `user-${Date.now()}`, role: "user", content: trimmed },
    ]);
    try {
      const result = await runCopilotAgent({
        session_id: sessionId,
        question: trimmed,
        source_state_snapshot: sourceSnapshot,
        context: { decision_session: sessionId },
      });
      setMessages((current) => [
        ...current,
        {
          id: `assistant-${Date.now()}`,
          role: "assistant",
          content: result.answer,
          events: result.events,
          sources: sourceReferences(result),
          missingCapabilities: result.missing_capabilities,
        },
      ]);
      setStatus("idle");
    } catch (reason: unknown) {
      setStatus("failed");
      setError(reason instanceof Error ? reason.message : "Copilot request failed.");
    }
  }

  return (
    <Shell sessionId={sessionId}>
      <main className="dashboard">
        <header className="dashboard__header">
          <div>
            <p className="eyebrow">NAVISAIL intelligence</p>
            <h1>Copilot</h1>
            <p>Ask questions against approved tools in the current decision session.</p>
          </div>
          <StatusBadge status="LIVE" />
        </header>

        <section className="copilot-layout">
          <section className="glass-panel copilot-panel" aria-label="Copilot conversation">
            <div className="copilot-context">
              <strong>Decision session</strong>
              <span>{sessionId}</span>
              <span className="chart-note">Source snapshot: {sourceSnapshot}</span>
            </div>
            <div className="copilot-messages" aria-live="polite">
              {messages.length === 0 && (
                <p className="lede">
                  Ask for a recommendation, comparison, explanation, or feasibility check.
                </p>
              )}
              {messages.map((message) => (
                <article
                  key={message.id}
                  className={`copilot-message copilot-message--${message.role}`}
                >
                  <strong>{message.role === "user" ? "You" : "NAVISAIL AI"}</strong>
                  <p>{message.content}</p>
                  {message.events && <AgentEvents events={message.events} />}
                  {message.missingCapabilities && message.missingCapabilities.length > 0 && (
                    <p className="chart-note">
                      Unavailable capabilities: {message.missingCapabilities.join(", ")}
                    </p>
                  )}
                  {message.sources && (
                    <details>
                      <summary>Sources and evidence</summary>
                      <ul className="data-list">
                        {message.sources.map((source) => (
                          <li key={source}>
                            <span>{source}</span>
                          </li>
                        ))}
                      </ul>
                    </details>
                  )}
                </article>
              ))}
              {status === "running" && (
                <p role="status">Copilot is retrieving, calculating, simulating, or comparing…</p>
              )}
            </div>
            {error && <ErrorState message={error} />}
            <form
              className="copilot-composer"
              onSubmit={(event) => {
                event.preventDefault();
                void submitQuestion();
              }}
            >
              <Input
                aria-label="Ask NAVISAIL Copilot"
                value={question}
                onChange={(event) => setQuestion(event.target.value)}
                placeholder="Ask NAVISAIL AI…"
              />
              <Button type="submit" disabled={status === "running" || !question.trim()}>
                {status === "running" ? "Working…" : "Ask"}
              </Button>
            </form>
          </section>

          <aside className="glass-panel" aria-label="Suggested questions">
            <h2>Suggested questions</h2>
            <div className="suggested-questions">
              {suggestedQuestions.map((suggestion) => (
                <Button
                  key={suggestion}
                  variant="quiet"
                  onClick={() => void submitQuestion(suggestion)}
                >
                  {suggestion}
                </Button>
              ))}
            </div>
          </aside>
        </section>
      </main>
    </Shell>
  );
}
