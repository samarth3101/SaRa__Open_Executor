"use client";

import { useState } from "react";

type Props = {
  onSubmit: (value: string) => Promise<void>;
  loading: boolean;
};

export default function CommandInput({ onSubmit, loading }: Props) {
  const [value, setValue] = useState("");

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!value.trim()) return;
    await onSubmit(value);
  }

  return (
    <form onSubmit={handleSubmit} className="w-full space-y-3">
      <textarea
        value={value}
        onChange={(e) => setValue(e.target.value)}
        placeholder='Try: "Hey SaRa, what is remaining today?"'
        className="w-full rounded-xl border border-gray-300 p-4 text-sm outline-none focus:border-black min-h-[120px]"
      />
      <button
        type="submit"
        disabled={loading}
        className="rounded-xl bg-black px-4 py-2 text-sm text-white disabled:opacity-50"
      >
        {loading ? "Thinking..." : "Ask SaRa"}
      </button>
    </form>
  );
}
