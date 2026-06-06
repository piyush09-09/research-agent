import { useNavigate } from "react-router-dom";
import QueryPanel from "../components/QueryPanel";
import AgentTimeline from "../components/AgentTimeline";
import StreamingReport from "../components/StreamingReport";
import EvalBadge from "../components/EvalBadge";
import Logo from "../components/Logo";
import { useSSE } from "../hooks/useSSE";

export default function Dashboard() {
  const { tokens, steps, tasks, done, loading, error, evalScores, startResearch } = useSSE();
  const navigate = useNavigate();

  const user = JSON.parse(localStorage.getItem("user") || '{"name":"User"}');

  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    navigate("/");
  };

  const handleSubmit = (query, wordLimit) => {
    startResearch(query, wordLimit);
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
          <span className="user-name">{user.name}</span>
          <button className="logout-btn" onClick={handleLogout}>
            Log out
          </button>
        </div>
      </header>

      <main>
        <QueryPanel onSubmit={handleSubmit} loading={loading} />

        {steps.length > 0 && (
          <AgentTimeline steps={steps} tasks={tasks} loading={loading} />
        )}

        <StreamingReport content={tokens} done={done} error={error} />

        {evalScores && <EvalBadge scores={evalScores} />}
      </main>

      <footer className="app-footer">
        <span>LangGraph · Groq · Qdrant · FastAPI · React</span>
      </footer>
    </div>
  );
}