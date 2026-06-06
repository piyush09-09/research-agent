import ReactMarkdown from "react-markdown";

export default function StreamingReport({ content, done, error }) {
  if (error) {
    return (
      <div className="report">
        <div className="report-header">
          <div className="report-label">Error</div>
        </div>
        <div className="report-body">
          <p style={{ color: "var(--red)" }}>
            Something went wrong. The backend might be down or the AI service is
            rate-limited. Please try again in a few minutes.
          </p>
        </div>
      </div>
    );
  }

  if (!content) return null;

  return (
    <div className="report">
      <div className="report-header">
        <div className="report-label">Research Report</div>
        {!done && <span className="writing-badge">Writing…</span>}
        {done && <span className="done-badge">Complete</span>}
      </div>
      <div className="report-body">
        <ReactMarkdown>{content}</ReactMarkdown>
        {!done && <span className="caret" />}
      </div>
    </div>
  );
}