import { useState, useRef } from "react";

const WORD_OPTIONS = [
  { label: "Brief", value: 300 },
  { label: "Standard", value: 800 },
  { label: "Detailed", value: 3000 },
  { label: "In-depth", value: 6000 },
];

export default function QueryPanel({ onSubmit, loading }) {
  const [query, setQuery] = useState("");
  const [wordLimit, setWordLimit] = useState(500);
  const [listening, setListening] = useState(false);
  const recognitionRef = useRef(null);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (query.trim() && !loading) {
      onSubmit(query.trim(), wordLimit);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const toggleVoice = () => {
    if (listening) {
      recognitionRef.current?.stop();
      setListening(false);
      return;
    }

    const SpeechRecognition =
      window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
      alert("Voice input not supported in this browser. Use Chrome or Edge.");
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.lang = "en-US";
    recognition.interimResults = true;
    recognition.continuous = false;
    recognitionRef.current = recognition;

    recognition.onresult = (event) => {
      const transcript = Array.from(event.results)
        .map((r) => r[0].transcript)
        .join("");
      setQuery(transcript);
    };

    recognition.onend = () => setListening(false);
    recognition.onerror = () => setListening(false);

    recognition.start();
    setListening(true);
  };

  return (
    <form onSubmit={handleSubmit} className="query-panel">
      <div className="input-wrapper">
        <textarea
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="What would you like to research?"
          rows={2}
          disabled={loading}
          spellCheck={false}
        />
        <button
          type="button"
          className={`voice-btn ${listening ? "voice-active" : ""}`}
          onClick={toggleVoice}
          disabled={loading}
          title="Voice input"
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z" />
            <path d="M19 10v2a7 7 0 0 1-14 0v-2" />
            <line x1="12" y1="19" x2="12" y2="22" />
          </svg>
        </button>
        <button type="submit" className="submit-btn" disabled={loading || !query.trim()}>
          {loading ? (
            <span className="btn-loading">
              <span className="spinner" />
              Researching
            </span>
          ) : (
            "Research"
          )}
        </button>
      </div>

      <div className="controls-row">
        <p className="hint">
          {listening
            ? "Listening... speak your query"
            : loading
            ? "Agents are working — this takes 30–60 seconds"
            : "Press Enter to submit · Shift+Enter for new line"}
        </p>
        <div className="word-limit-control">
          <label>Length:</label>
          <div className="word-options">
            {WORD_OPTIONS.map((opt) => (
              <button
                key={opt.value}
                type="button"
                className={`word-chip ${wordLimit === opt.value ? "active" : ""}`}
                onClick={() => setWordLimit(opt.value)}
                disabled={loading}
              >
                {opt.label}
              </button>
            ))}
          </div>
        </div>
      </div>
    </form>
  );
}