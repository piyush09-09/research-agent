import { useState } from "react";
import { useNavigate } from "react-router-dom";
import QueryPanel from "../components/QueryPanel";
import AgentTimeline from "../components/AgentTimeline";
import StreamingReport from "../components/StreamingReport";
import EvalBadge from "../components/EvalBadge";
import HistoryPanel from "../components/HistoryPanel";
import Logo from "../components/Logo";
import { useSSE } from "../hooks/useSSE";

export default function Dashboard() {
  const { tokens, steps, tasks, done, loading, error, evalScores, startResearch } = useSSE();
  const [historyOpen, setHistoryOpen] = useState(false);
  const [viewingReport, setViewingReport] = useState(null);
  const navigate = useNavigate();

  const user = JSON.parse(localStorage.getItem("user") || '{"name":"User"}');

  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    navigate("/");
  };

  const handleSubmit = (query, wordLimit) => {
    setViewingReport(null);
    startResearch(query, wordLimit);
  };

  const handleHistorySelect = (session) => {
    setViewingReport(session);
  };

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-left">
          <Logo size={34} />
          <div>
            <h1>Research Agent</h1>
            <p className="subtitle">
              Multi-agent system — plan, search, synthesize, write
            </p>
          </div>
        </div>
        <div className="header-right">
          <button className="history-btn" onClick={() => setHistoryOpen(true)}>
            History
          </button>
          <span className="user-name">{user.name}</span>
          <button className="logout-btn" onClick={handleLogout}>
            Log out
          </button>
        </div>
      </header>

      <main>
        <QueryPanel onSubmit={handleSubmit} loading={loading} />

        {viewingReport ? (
          <>
            <div className="viewing-banner">
              <span>Viewing saved report: "{viewingReport.query}"</span>
              <button onClick={() => setViewingReport(null)}>Close</button>
            </div>
            <StreamingReport content={viewingReport.report} done={true} error={false} />
            {viewingReport.eval_scores?.overall > 0 && (
              <EvalBadge scores={viewingReport.eval_scores} />
            )}
          </>
        ) : (
          <>
            {steps.length > 0 && (
              <AgentTimeline steps={steps} tasks={tasks} loading={loading} />
            )}
            <StreamingReport content={tokens} done={done} error={error} />
            {evalScores && <EvalBadge scores={evalScores} />}
          </>
        )}
      </main>

      <footer className="app-footer">
        <span>LangGraph · Groq · Qdrant · FastAPI · React</span>
      </footer>

      <HistoryPanel
        visible={historyOpen}
        onClose={() => setHistoryOpen(false)}
        onSelect={handleHistorySelect}
      />
    </div>
  );
}