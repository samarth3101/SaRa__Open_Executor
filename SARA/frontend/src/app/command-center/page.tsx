"use client";

import { useState } from "react";
import CommandInput from "../../components/intent/CommandInput";
import CommandResponse from "../../components/intent/CommandResponse";
import {
  CommandResponse as CommandResponseType,
  executeCommand,
} from "../../utils/api";

const quickCommands = [
  "Latest AI news",
  "Check latest emails",
  "What's remaining today",
  "How am I doing on goals",
];

export default function CommandCenterPage() {
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState<CommandResponseType | null>(null);
  const [error, setError] = useState("");

  async function handleCommandSubmit(value: string) {
    try {
      setLoading(true);
      setError("");
      const result = await executeCommand(value);
      setResponse(result);
    } catch {
      setError("Could not reach SaRa backend.");
      setResponse(null);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="sara-page">
      {/* Subtle radial glow behind the card */}
      <div className="sara-glow" aria-hidden="true" />

      <div className="sara-outer">
        <div className="sara-inner">

          {/* ── Main command card ── */}
          <section className="sara-card">

            {/* Card header */}
            <div className="sara-card-header">
              <div className="sara-brand">
                <div className="sara-brand-icon" aria-hidden="true">✦</div>
                <div>
                  <p className="sara-brand-eyebrow">SARA</p>
                  <h1 className="sara-brand-title">Command Center</h1>
                </div>
              </div>

              <div className="sara-pills">
                <span className="sara-pill">Status · Ready</span>
                <span className="sara-pill">Focus · Command flow</span>
                <span className="sara-pill sara-pill--accent">Quiet productivity</span>
              </div>
            </div>

            {/* Card body */}
            <div className="sara-card-body">
              <p className="sara-eyebrow">Personal operating surface</p>

              <h2 className="sara-hero-title">
                Ask SaRa what matters right now.
              </h2>

              <p className="sara-hero-sub">
                Review inbox activity, daily priorities, goal progress, and
                important updates from one clean command surface.
              </p>

              {/* Quick command chips */}
              <div className="sara-chips">
                {quickCommands.map((item) => (
                  <button
                    key={item}
                    type="button"
                    onClick={() => handleCommandSubmit(item)}
                    disabled={loading}
                    className="sara-chip"
                  >
                    {item}
                  </button>
                ))}
              </div>

              {/* Text input */}
              <div className="sara-input-area">
                <CommandInput onSubmit={handleCommandSubmit} loading={loading} />
              </div>
            </div>
          </section>

          {/* Error banner */}
          {error ? (
            <div className="sara-error" role="alert">
              {error}
            </div>
          ) : null}

          {/* Response panel */}
          <CommandResponse data={response} />

        </div>
      </div>
    </main>
  );
}