export type CommandIntent =
  | "today_remaining"
  | "latest_emails"
  | "news_summary"
  | "goal_status"
  | "add_task"
  | "unknown";

export type CommandCard = {
  title: string;
  subtitle?: string | null;
  description?: string | null;
  url?: string | null;
  label?: string | null;
};

export type CommandResponse = {
  intent: CommandIntent;
  summary: string;
  priority_items: string[];
  suggested_next_action: string;
  source: string;
  estimated_minutes?: number | null;
  command_text?: string | null;
  cards?: CommandCard[];
};

export type CommandHistoryItem = {
  id: number;
  user_id: number;
  command_text: string;
  intent: CommandIntent;
  summary?: string | null;
  source?: string | null;
  created_at: string;
};

const API_BASE = "http://localhost:4000";

export async function executeCommand(text: string) {
  const res = await fetch(`${API_BASE}/commands/execute`, {
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

export async function getCommandHistory(userId = 1, limit = 100) {
  const res = await fetch(
    `${API_BASE}/commands/history/${userId}?limit=${limit}`,
    {
      method: "GET",
      cache: "no-store",
    }
  );

  if (!res.ok) {
    throw new Error("Failed to fetch command history");
  }

  return (await res.json()) as CommandHistoryItem[];
}
