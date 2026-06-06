export default function AgentTimeline({ steps, tasks, loading }) {
  return (
    <div className="timeline">
      <div className="timeline-header">
        <div className="timeline-label">Agent Activity</div>
        {loading && <span className="live-badge">LIVE</span>}
      </div>

      {tasks.length > 0 && (
        <div className="tasks-block">
          <div className="tasks-title">Sub-tasks identified</div>
          {tasks.map((task, i) => (
            <div key={i} className="task-row">
              <span className="task-num">{String(i + 1).padStart(2, "0")}</span>
              <span className="task-text">{task}</span>
            </div>
          ))}
        </div>
      )}

      <div className="steps-block">
        {steps.map((step, i) => (
          <div
            key={i}
            className="step-row"
            style={{ animationDelay: `${i * 60}ms` }}
          >
            <span className="step-indicator" />
            <span className="step-text">{step}</span>
          </div>
        ))}
      </div>
    </div>
  );
}