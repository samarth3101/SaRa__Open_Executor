"use client";

import { useEffect, useMemo, useState } from "react";
import CommandInput from "../../components/intent/CommandInput";
import CommandResponse from "../../components/intent/CommandResponse";
import {
  CommandHistoryItem,
  CommandResponse as CommandResponseType,
  executeCommand,
  getCommandHistory,
} from "../../utils/api";

const quickCommands = [
  "Latest AI news",
  "Check latest emails",
  "What's remaining today",
  "How am I doing on goals",
];

function getIntentLabel(intent: CommandHistoryItem["intent"]) {
  switch (intent) {
    case "news_summary":
      return "News";
    case "latest_emails":
      return "Inbox";
    case "today_remaining":
      return "Today";
    case "goal_status":
      return "Goals";
    case "add_task":
      return "Task";
    default:
      return "SaRa";
  }
}

function parseSafeDate(value: string) {
  const time = new Date(value).getTime();
  return Number.isNaN(time) ? 0 : time;
}

function formatHistoryTime(value: string) {
  const date = new Date(value);

  if (Number.isNaN(date.getTime())) return "Just now";

  return new Intl.DateTimeFormat("en-IN", {
    day: "2-digit",
    month: "short",
    hour: "numeric",
    minute: "2-digit",
    hour12: true,
    timeZone: "Asia/Kolkata",
  }).format(date);
}

function estimateTokens(item: CommandHistoryItem) {
  const textSize =
    (item.command_text?.length || 0) + (item.summary?.length || 0);
  return Math.max(24, Math.round(textSize / 4));
}

export default function CommandCenterPage() {
  const [loading, setLoading] = useState(false);
  const [historyLoading, setHistoryLoading] = useState(true);
  const [response, setResponse] = useState<CommandResponseType | null>(null);
  const [history, setHistory] = useState<CommandHistoryItem[]>([]);
  const [error, setError] = useState("");
  const [historyError, setHistoryError] = useState("");
  const [showExportNote, setShowExportNote] = useState(false);

  async function loadHistory() {
    try {
      setHistoryLoading(true);
      setHistoryError("");
      const result = await getCommandHistory(1, 100);
      setHistory(result);
    } catch {
      setHistory([]);
      setHistoryError("Could not load command memory.");
    } finally {
      setHistoryLoading(false);
    }
  }

  useEffect(() => {
    loadHistory();
  }, []);

  async function handleCommandSubmit(value: string) {
    try {
      setLoading(true);
      setError("");
      const result = await executeCommand(value);
      setResponse(result);
      await loadHistory();
    } catch {
      setError("Could not reach SaRa backend.");
      setResponse(null);
    } finally {
      setLoading(false);
    }
  }

  const sortedHistory = useMemo(() => {
    return [...history].sort(
      (a, b) => parseSafeDate(b.created_at) - parseSafeDate(a.created_at)
    );
  }, [history]);

  const visibleHistory = useMemo(() => {
    return sortedHistory.slice(0, 15);
  }, [sortedHistory]);

  const hiddenHistoryCount = Math.max(sortedHistory.length - visibleHistory.length, 0);

  const analytics = useMemo(() => {
    const counts = {
      news_summary: 0,
      latest_emails: 0,
      today_remaining: 0,
      goal_status: 0,
      add_task: 0,
      unknown: 0,
    };

    let totalTokens = 0;

    for (const item of sortedHistory) {
      counts[item.intent] += 1;
      totalTokens += estimateTokens(item);
    }

    return {
      counts,
      total: sortedHistory.length,
      totalTokens,
      averageTokens:
        sortedHistory.length > 0
          ? Math.round(totalTokens / sortedHistory.length)
          : 0,
      latestTokens:
        sortedHistory.length > 0 ? estimateTokens(sortedHistory[0]) : 0,
    };
  }, [sortedHistory]);

  return (
    <main className="sara-page">
      <div className="sara-glow" aria-hidden="true" />

      <div className="sara-outer">
        <div className="sara-inner">
          <section className="sara-card">
            <div className="sara-card-header">
              <div className="sara-brand">
                <div className="sara-brand-icon" aria-hidden="true">
                  ✦
                </div>
                <div>
                  <p className="sara-brand-eyebrow">SARA</p>
                  <h1 className="sara-brand-title">Command Center</h1>
                </div>
              </div>

              <div className="sara-pills">
                <span className="sara-pill">Status · Ready</span>
                <span className="sara-pill">Focus · Command flow</span>
                <span className="sara-pill sara-pill--accent">
                  Quiet productivity
                </span>
              </div>
            </div>

            <div className="sara-card-body">
              <p className="sara-eyebrow">Personal operating surface</p>

              <h2 className="sara-hero-title">
                Ask SaRa what matters right now.
              </h2>

              <p className="sara-hero-sub">
                Review inbox activity, daily priorities, goal progress, and
                important updates from one clean command surface.
              </p>

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

              <div className="sara-input-area">
                <CommandInput onSubmit={handleCommandSubmit} loading={loading} />
              </div>
            </div>
          </section>

          {error ? (
            <div className="sara-error" role="alert">
              {error}
            </div>
          ) : null}

          <CommandResponse data={response} />

          <section className="sara-response-card">
            <div className="sara-response-header">
              <div className="sara-response-meta">
                <div className="sara-intent-badge">
                  <span className="sara-intent-dot" aria-hidden="true" />
                  Recent activity
                </div>

                <p className="sara-eyebrow" style={{ marginTop: "16px" }}>
                  Command memory
                </p>

                <h2 className="sara-response-title">
                  Your latest SaRa interactions
                </h2>
              </div>

              <div className="sara-response-stats">
                <div className="sara-stat-card">
                  <p className="sara-stat-label">Fetched</p>
                  <p className="sara-stat-value">{analytics.total}</p>
                </div>
                <div className="sara-stat-card">
                  <p className="sara-stat-label">Visible</p>
                  <p className="sara-stat-value">{visibleHistory.length}</p>
                </div>
              </div>
            </div>

            <div className="sara-response-body">
              <div className="sara-analytics-grid">
                <div className="sara-item-card">
                  <div className="sara-card-item-top">
                    <div className="sara-card-item-labels">
                      <span className="sara-card-label">Analytics</span>
                      <span className="sara-card-subtitle">Intent mix</span>
                    </div>
                  </div>

                  <div className="sara-metric-list">
                    <div className="sara-metric-row">
                      <span>News</span>
                      <strong>{analytics.counts.news_summary}</strong>
                    </div>
                    <div className="sara-metric-row">
                      <span>Inbox</span>
                      <strong>{analytics.counts.latest_emails}</strong>
                    </div>
                    <div className="sara-metric-row">
                      <span>Today</span>
                      <strong>{analytics.counts.today_remaining}</strong>
                    </div>
                    <div className="sara-metric-row">
                      <span>Goals</span>
                      <strong>{analytics.counts.goal_status}</strong>
                    </div>
                    <div className="sara-metric-row">
                      <span>Task</span>
                      <strong>{analytics.counts.add_task}</strong>
                    </div>
                    <div className="sara-metric-row">
                      <span>Unknown</span>
                      <strong>{analytics.counts.unknown}</strong>
                    </div>
                  </div>
                </div>

                <div className="sara-item-card">
                  <div className="sara-card-item-top">
                    <div className="sara-card-item-labels">
                      <span className="sara-card-label">Usage</span>
                      <span className="sara-card-subtitle">Dummy tokens</span>
                    </div>
                  </div>

                  <div className="sara-metric-list">
                    <div className="sara-metric-row">
                      <span>Total tokens</span>
                      <strong>{analytics.totalTokens}</strong>
                    </div>
                    <div className="sara-metric-row">
                      <span>Average / command</span>
                      <strong>{analytics.averageTokens}</strong>
                    </div>
                    <div className="sara-metric-row">
                      <span>Latest command</span>
                      <strong>{analytics.latestTokens}</strong>
                    </div>
                  </div>
                </div>
              </div>

              {historyLoading ? (
                <div className="sara-item-card">
                  <p className="sara-empty-state">Loading recent commands…</p>
                </div>
              ) : historyError ? (
                <div className="sara-item-card">
                  <p className="sara-empty-state">{historyError}</p>
                </div>
              ) : visibleHistory.length === 0 ? (
                <div className="sara-item-card">
                  <p className="sara-empty-state">
                    No commands yet. Ask SaRa something to start building history.
                  </p>
                </div>
              ) : (
                <>
                  <div className="sara-history-list">
                    {visibleHistory.map((item) => (
                      <div key={item.id} className="sara-history-item">
                        <div className="sara-history-top">
                          <div className="sara-history-badges">
                            <span className="sara-card-label">
                              {getIntentLabel(item.intent)}
                            </span>
                            <span className="sara-card-subtitle">
                              {item.source || "system"}
                            </span>
                          </div>
                          <span className="sara-open-pill">
                            {formatHistoryTime(item.created_at)}
                          </span>
                        </div>

                        <h3 className="sara-card-item-title">
                          {item.command_text}
                        </h3>

                        <p className="sara-card-item-desc">
                          {item.summary || "No summary available."}
                        </p>
                      </div>
                    ))}
                  </div>

                  {hiddenHistoryCount > 0 ? (
                    <div className="sara-history-footer">
                      <div className="sara-history-footer-copy">
                        <p className="sara-history-footer-title">
                          More command memory is available
                        </p>
                        <p className="sara-history-footer-text">
                          Showing the latest 15 interactions. {hiddenHistoryCount} older
                          entries are available in the full activity record.
                        </p>
                      </div>

                      <button
                        type="button"
                        className="sara-history-footer-btn"
                        onClick={() => setShowExportNote((prev) => !prev)}
                      >
                        Prepare full history export
                      </button>
                    </div>
                  ) : null}

                  {showExportNote ? (
                    <div className="sara-export-note" role="status">
                      <p className="sara-export-note-title">
                        Full activity export is the next step
                      </p>
                      <p className="sara-export-note-text">
                        SaRa can already retain command history in memory. The next
                        upgrade is a structured export flow for complete activity review,
                        such as PDF or shareable reporting.
                      </p>
                    </div>
                  ) : null}
                </>
              )}
            </div>
          </section>
        </div>
      </div>
    </main>
  );
}
