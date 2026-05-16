export type CommandResponse = {
  intent: "today_remaining" | "latest_emails" | "news_summary" | "unknown";
  summary: string;
  priority_items: string[];
  suggested_next_action: string;
  source: string;
};

export async function executeCommand(text: string) {
  const res = await fetch("http://localhost:4000/commands/execute", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      text,
      user_id: 1,
    }),
  });

  if (!res.ok) {
    throw new Error("Failed to execute command");
  }

  return (await res.json()) as CommandResponse;
}
