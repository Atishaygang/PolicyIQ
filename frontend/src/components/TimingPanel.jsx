import { ChevronDown, ClockIcon } from "./Icons";

const LABELS = {
  hybrid_retrieval_ms: "Hybrid retrieval",
  reranking_ms: "Reranking",
  context_prompt_ms: "Context + prompt",
  llm_client_ms: "LLM client",
  llm_generation_ms: "LLM generation",
  response_build_ms: "Response build",
  total_ms: "Total",
};

function formatDuration(ms) {
  if (ms >= 1000) return `${(ms / 1000).toFixed(2)} s`;
  if (ms >= 10) return `${ms.toFixed(0)} ms`;
  return `${ms.toFixed(2)} ms`;
}

export default function TimingPanel({ timings }) {
  if (!timings) return null;
  return (
    <details className="timing-panel">
      <summary>
        <span className="timing-summary-left"><ClockIcon/><span>How long did this take?</span></span>
        <span className="timing-summary-right">{formatDuration(timings.total_ms || 0)}<ChevronDown/></span>
      </summary>
      <div className="timing-grid">
        {Object.entries(LABELS).map(([key, label]) => typeof timings[key] === "number" ? (
          <div className={`timing-item ${key === "total_ms" ? "timing-total" : ""}`} key={key}>
            <span>{label}</span><strong>{formatDuration(timings[key])}</strong>
          </div>
        ) : null)}
      </div>
      <p className="timing-note">Timings are diagnostic measurements from this request, not benchmark results.</p>
    </details>
  );
}
