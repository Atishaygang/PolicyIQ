import { ArrowUpRight } from "./Icons";

export default function QuestionComposer({ value, onChange, onSubmit, loading, serviceReady }) {
  const remaining = 1000 - value.length;
  const canSubmit = value.trim().length >= 3 && value.length <= 1000 && !loading && serviceReady;

  function handleKeyDown(event) {
    if ((event.ctrlKey || event.metaKey) && event.key === "Enter") {
      event.preventDefault();
      if (canSubmit) onSubmit();
    }
  }

  return (
    <div className="composer-card">
      <div className="composer-heading-row">
        <div>
          <p className="field-label">Ask PolicyIQ</p>
          <p className="field-helper">Ask naturally — the answer will stay grounded in retrieved documents.</p>
        </div>
        <span className={`char-count ${remaining < 80 ? "near-limit" : ""}`}>{remaining}</span>
      </div>

      <textarea
        className="question-input"
        value={value}
        onChange={(event) => onChange(event.target.value)}
        onKeyDown={handleKeyDown}
        maxLength={1000}
        rows={5}
        placeholder="For example: What is the maximum No Claim Bonus?"
        aria-label="Ask an insurance question"
      />

      <div className="composer-footer">
        <span className="keyboard-hint">Ctrl / ⌘ + Enter to ask</span>
        <button className="primary-button" type="button" onClick={onSubmit} disabled={!canSubmit}>
          <span>{loading ? "Working…" : "Ask PolicyIQ"}</span>
          <ArrowUpRight />
        </button>
      </div>

      {!serviceReady && <p className="composer-warning">Start the PolicyIQ backend before sending a question.</p>}
    </div>
  );
}
