import { useState, useEffect } from "react";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export default function HistoryPanel({ onSelect, visible, onClose }) {
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (visible) fetchHistory();
  }, [visible]);

  const fetchHistory = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem("token");
      const res = await fetch(`${API_URL}/history`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      const data = await res.json();
      setSessions(data.sessions || []);
    } catch (err) {
      console.error("Failed to fetch history:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id, e) => {
    e.stopPropagation();
    if (!confirm("Delete this research session?")) return;
    try {
      const token = localStorage.getItem("token");
      await fetch(`${API_URL}/history/${id}`, {
        method: "DELETE",
        headers: { Authorization: `Bearer ${token}` },
      });
      setSessions((prev) => prev.filter((s) => s.id !== id));
    } catch (err) {
      console.error("Delete failed:", err);
    }
  };

  const formatDate = (dateStr) => {
    const d = new Date(dateStr);
    const now = new Date();
    const diffMs = now - d;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return "Just now";
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    return d.toLocaleDateString();
  };

  if (!visible) return null;

  return (
    <div className="history-overlay" onClick={onClose}>
      <div className="history-panel" onClick={(e) => e.stopPropagation()}>
        <div className="history-header">
          <h3>Research History</h3>
          <button className="history-close" onClick={onClose}>✕</button>
        </div>

        {loading && <div className="history-loading">Loading...</div>}

        {!loading && sessions.length === 0 && (
          <div className="history-empty">
            No research sessions yet. Start your first one!
          </div>
        )}

        <div className="history-list">
          {sessions.map((s) => (
            <div
              key={s.id}
              className="history-item"
              onClick={() => { onSelect(s); onClose(); }}
            >
              <div className="history-query">{s.query}</div>
              <div className="history-meta">
                <span className="history-date">{formatDate(s.created_at)}</span>
                {s.eval_scores?.overall > 0 && (
                  <span className="history-score">
                    {(s.eval_scores.overall * 100).toFixed(0)}%
                  </span>
                )}
                <button
                  className="history-delete"
                  onClick={(e) => handleDelete(s.id, e)}
                >
                  Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}