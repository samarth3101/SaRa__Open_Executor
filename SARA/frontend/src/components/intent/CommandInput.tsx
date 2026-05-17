"use client";

import { FormEvent, KeyboardEvent, useState } from "react";

type Props = {
  onSubmit: (value: string) => Promise<void> | void;
  loading?: boolean;
};

export default function CommandInput({ onSubmit, loading = false }: Props) {
  const [value, setValue] = useState("");

  function submitCurrentValue() {
    const trimmed = value.trim();
    if (!trimmed || loading) return;
    onSubmit(trimmed);
    setValue("");
  }

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    submitCurrentValue();
  }

  function handleKeyDown(e: KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      submitCurrentValue();
    }
  }

  return (
    <form onSubmit={handleSubmit} className="sara-form">
      <label htmlFor="command-input" className="sr-only">
        Command input
      </label>

      <div className="sara-input-card">
        {/* Textarea */}
        <div className="sara-textarea-wrap">
          <textarea
            id="command-input"
            value={value}
            onChange={(e) => setValue(e.target.value)}
            onKeyDown={handleKeyDown}
            rows={4}
            placeholder='Try: "Hey SaRa, what is remaining today?"'
            className="sara-textarea"
          />

          {/* Send button — icon in box, bottom-right of textarea */}
          <button
            type="submit"
            disabled={loading || !value.trim()}
            aria-label="Send command"
            className="sara-send-btn"
          >
            {loading ? (
              <span className="sara-send-spinner" aria-hidden="true" />
            ) : (
              /* Arrow-up-right icon drawn with two SVG lines */
              <svg
                width="18"
                height="18"
                viewBox="0 0 18 18"
                fill="none"
                aria-hidden="true"
              >
                <path
                  d="M4.5 13.5L13.5 4.5M13.5 4.5H6.75M13.5 4.5V11.25"
                  stroke="currentColor"
                  strokeWidth="1.8"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              </svg>
            )}
          </button>
        </div>

        {/* Footer hints */}
        <div className="sara-input-footer">
          <span className="sara-input-hint">
            Press <kbd className="sara-kbd">Enter</kbd> to send,{" "}
            <kbd className="sara-kbd">Shift + Enter</kbd> for a new line.
          </span>
          <span className="sara-input-hint sara-input-hint--muted">
            Natural language works best.
          </span>
        </div>
      </div>
    </form>
  );
}