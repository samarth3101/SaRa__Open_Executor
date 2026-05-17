import { CommandResponse as CommandResponseType } from "../../utils/api";

type Props = {
   data : CommandResponseType | null;
};

function getIntentLabel(intent?: CommandResponseType["intent"]) {
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

function getIntentEyebrow(intent?: CommandResponseType["intent"]) {
  switch (intent) {
    case "news_summary":
      return "Current coverage";
    case "latest_emails":
      return "Inbox snapshot";
    case "today_remaining":
      return "Execution status";
    case "goal_status":
      return "Goal review";
    case "add_task":
      return "Task capture";
    default:
      return "Assistant response";
  }
}

function getIntentEmptyState(intent?: CommandResponseType["intent"]) {
  switch (intent) {
    case "latest_emails":
      return "No inbox items to highlight right now.";
    case "news_summary":
      return "No major stories were returned.";
    case "goal_status":
      return "No goals available yet.";
    case "today_remaining":
      return "Nothing urgent is pending right now.";
    default:
      return "Nothing important right now.";
  }
}

export default function CommandResponse({ data }: Props) {
  if (!data) return null;

  const cards = Array.isArray(data.cards) ? data.cards : [];
  const priorityItems = Array.isArray(data.priority_items)
    ? data.priority_items
    : [];

  const hasCards = cards.length > 0;
  const intentLabel = getIntentLabel(data.intent);
  const eyebrow = getIntentEyebrow(data.intent);
  const emptyState = getIntentEmptyState(data.intent);

  return (
    <section className="sara-response-card">
      <div className="sara-response-header">
        <div className="sara-response-meta">
          <div className="sara-intent-badge">
            <span className="sara-intent-dot" aria-hidden="true" />
            {intentLabel}
          </div>

          <p className="sara-eyebrow" style={{ marginTop: "16px" }}>
            {eyebrow}
          </p>

          <h2 className="sara-response-title">
            {data.summary || "Here’s the latest update."}
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

      <div className="sara-response-body">
        {hasCards ? (
          <div className="sara-cards-grid">
            {cards.map((card, index) => {
              const isNews = data.intent === "news_summary";
              const isEmail = data.intent === "latest_emails";
              const isGoals = data.intent === "goal_status";
              const isToday = data.intent === "today_remaining";

              const cardClassName = [
                "sara-item-card",
                card.url ? "sara-item-card--link" : "",
                isNews ? "sara-item-card--news" : "",
                isEmail ? "sara-item-card--email" : "",
                isGoals ? "sara-item-card--goal" : "",
                isToday ? "sara-item-card--today" : "",
              ]
                .filter(Boolean)
                .join(" ");

              const inner = (
                <>
                  <div className="sara-card-item-top">
                    <div className="sara-card-item-labels">
                      {card.label && (
                        <span className="sara-card-label">{card.label}</span>
                      )}
                      {card.subtitle && (
                        <span className="sara-card-subtitle">
                          {card.subtitle}
                        </span>
                      )}
                    </div>

                    {card.url ? (
                      <span className="sara-open-pill">Open ↗</span>
                    ) : isEmail ? (
                      <span className="sara-open-pill">Inbox item</span>
                    ) : isGoals ? (
                      <span className="sara-open-pill">Goal</span>
                    ) : isToday ? (
                      <span className="sara-open-pill">Task</span>
                    ) : null}
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
                    className={cardClassName}
                  >
                    {inner}
                  </a>
                );
              }

              return (
                <div
                  key={`${card.title ?? "card"}-${index}`}
                  className={cardClassName}
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
              <p className="sara-empty-state">{emptyState}</p>
            ) : (
              <ul className="sara-priority-list">
                {priorityItems.map((item, index) => (
                  <li key={index} className="sara-priority-item">
                    <span className="sara-priority-dot" aria-hidden="true" />
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            )}
          </div>
        )}

        <div className="sara-suggestion">
          <div className="sara-suggestion-top">
            <p className="sara-suggestion-label">Suggested next action</p>
            <span className="sara-suggestion-badge">{intentLabel}</span>
          </div>

          <p className="sara-suggestion-text">
            {data.suggested_next_action || "Ask SaRa a follow-up question."}
          </p>
        </div>
      </div>
    </section>
  );
}
