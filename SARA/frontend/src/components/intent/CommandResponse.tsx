import { CommandResponse as CommandResponseType } from "../../utils/api";

type Props = {
  data: CommandResponseType | null;
};

function getIntentLabel(intent?: CommandResponseType["intent"]) {
  switch (intent) {
    case "news_summary":   return "News";
    case "latest_emails":  return "Inbox";
    case "today_remaining": return "Today";
    case "goal_status":    return "Goals";
    case "add_task":       return "Task";
    default:               return "SaRa";
  }
}

export default function CommandResponse({ data }: Props) {
  if (!data) return null;

  const cards = Array.isArray(data.cards) ? data.cards : [];
  const priorityItems = Array.isArray(data.priority_items)
    ? data.priority_items
    : [];
  const hasCards = cards.length > 0;

  return (
    <section className="sara-response-card">

      {/* Response header */}
      <div className="sara-response-header">
        <div className="sara-response-meta">
          <div className="sara-intent-badge">
            <span className="sara-intent-dot" aria-hidden="true" />
            {getIntentLabel(data.intent)}
          </div>

          <p className="sara-eyebrow" style={{ marginTop: "16px" }}>
            SaRa response
          </p>

          <h2 className="sara-response-title">
            {data.summary || "Here's the latest update."}
          </h2>
        </div>

        <div className="sara-response-stats">
          <div className="sara-stat-card">
            <p className="sara-stat-label">Source</p>
            <p className="sara-stat-value">{data.source || "SaRa"}</p>
          </div>
          <div className="sara-stat-card">
            <p className="sara-stat-label">Read time</p>
            <p className="sara-stat-value">
              {typeof data.estimated_minutes === "number"
                ? `${data.estimated_minutes} min`
                : "—"}
            </p>
          </div>
        </div>
      </div>

      {/* Response body */}
      <div className="sara-response-body">
        {hasCards ? (
          <div className="sara-cards-grid">
            {cards.map((card, index) => {
              const inner = (
                <>
                  <div className="sara-card-item-top">
                    <div className="sara-card-item-labels">
                      {card.label && (
                        <span className="sara-card-label">{card.label}</span>
                      )}
                      {card.subtitle && (
                        <span className="sara-card-subtitle">{card.subtitle}</span>
                      )}
                    </div>
                    {card.url && (
                      <span className="sara-open-pill">Open ↗</span>
                    )}
                  </div>
                  <h3 className="sara-card-item-title">
                    {card.title || "Untitled item"}
                  </h3>
                  {card.description && (
                    <p className="sara-card-item-desc">{card.description}</p>
                  )}
                </>
              );

              if (card.url) {
                return (
                  <a
                    key={`${card.title ?? "card"}-${index}`}
                    href={card.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="sara-item-card sara-item-card--link"
                  >
                    {inner}
                  </a>
                );
              }

              return (
                <div
                  key={`${card.title ?? "card"}-${index}`}
                  className="sara-item-card"
                >
                  {inner}
                </div>
              );
            })}
          </div>
        ) : (
          <div className="sara-item-card">
            <p className="sara-eyebrow">Priority items</p>
            {priorityItems.length === 0 ? (
              <p className="sara-empty-state">Nothing important right now.</p>
            ) : (
              <ul className="sara-priority-list">
                {priorityItems.map((item, index) => (
                  <li key={index} className="sara-priority-item">
                    {item}
                  </li>
                ))}
              </ul>
            )}
          </div>
        )}

        {/* Suggested next action */}
        <div className="sara-suggestion">
          <p className="sara-suggestion-label">Suggested next action</p>
          <p className="sara-suggestion-text">
            {data.suggested_next_action || "Ask SaRa a follow-up question."}
          </p>
        </div>
      </div>
    </section>
  );
}