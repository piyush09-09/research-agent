export default function EvalBadge({ scores }) {
  if (!scores || scores.overall < 0) return null;

  const getColor = (score) => {
    if (score >= 0.8) return "var(--green)";
    if (score >= 0.6) return "var(--amber)";
    return "var(--red)";
  };

  const getLabel = (score) => {
    if (score >= 0.8) return "High";
    if (score >= 0.6) return "Medium";
    return "Low";
  };

  const metrics = [
    { key: "faithfulness", label: "Faithfulness" },
    { key: "answer_relevancy", label: "Relevancy" },
    { key: "context_precision", label: "Precision" },
  ];

  return (
    <div className="eval-badge">
      <div className="eval-header">
        <span className="eval-title">RAGAS Evaluation</span>
        <span
          className="eval-overall"
          style={{ color: getColor(scores.overall) }}
        >
          {(scores.overall * 100).toFixed(0)}%
          <span className="eval-quality">{getLabel(scores.overall)}</span>
        </span>
      </div>
      <div className="eval-metrics">
        {metrics.map((m) => {
          const val = scores[m.key];
          if (val == null || val < 0) return null;
          return (
            <div key={m.key} className="eval-metric">
              <div className="eval-metric-header">
                <span className="eval-metric-label">{m.label}</span>
                <span
                  className="eval-metric-score"
                  style={{ color: getColor(val) }}
                >
                  {(val * 100).toFixed(0)}%
                </span>
              </div>
              <div className="eval-bar-bg">
                <div
                  className="eval-bar-fill"
                  style={{
                    width: `${val * 100}%`,
                    background: getColor(val),
                  }}
                />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}