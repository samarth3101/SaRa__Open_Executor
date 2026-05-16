"use client";

import { useState } from "react";
import CommandInput from "../../components/intent/CommandInput";
import CommandResponse from "../../components/intent/CommandResponse";
import {
  CommandResponse as CommandResponseType,
  executeCommand,
} from "../../utils/api";

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
    <main className="min-h-screen bg-white px-6 py-12 text-black">
      <div className="mx-auto max-w-3xl">
        <h1 className="text-3xl font-bold">SaRa Command Center</h1>
        <p className="mt-2 text-sm text-gray-600">
          Type a command for SaRa. Start with daily execution queries first.
        </p>

        <div className="mt-8">
          <CommandInput onSubmit={handleCommandSubmit} loading={loading} />
        </div>

        {error ? (
          <div className="mt-6 rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
            {error}
          </div>
        ) : null}

        <CommandResponse data={response} />
      </div>
    </main>
  );
}
