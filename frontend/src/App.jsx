import { useCallback, useEffect, useState } from "react";
import { askPolicyIQ, checkPolicyIQStatus } from "./lib/api";
import Brand from "./components/Brand";
import StatusPill from "./components/StatusPill";
import QuestionComposer from "./components/QuestionComposer";
import QuickPrompts from "./components/QuickPrompts";
import LoadingState from "./components/LoadingState";
import AnswerPanel from "./components/AnswerPanel";
import SourcesPanel from "./components/SourcesPanel";
import TimingPanel from "./components/TimingPanel";
import EmptyState from "./components/EmptyState";
import ErrorCard from "./components/ErrorCard";

export default function App() {
  const [question, setQuestion] = useState("");
  const [status, setStatus] = useState({ state: "checking", version: "—" });
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const refreshStatus = useCallback(async () => {
    setStatus((current) => ({ ...current, state: "checking" }));
    try {
      const service = await checkPolicyIQStatus();
      setStatus({ state: service.ready ? "ready" : "warming", version: service.version });
    } catch {
      setStatus({ state: "offline", version: "—" });
    }
  }, []);

  useEffect(() => {
    refreshStatus();
    const timer = window.setInterval(refreshStatus, 30000);
    return () => window.clearInterval(timer);
  }, [refreshStatus]);

  async function submitQuestion(overrideQuestion) {
    const finalQuestion = (overrideQuestion ?? question).trim();
    if (finalQuestion.length < 3 || finalQuestion.length > 1000 || loading) return;

    setQuestion(finalQuestion);
    setLoading(true);
    setResult(null);
    setError("");

    requestAnimationFrame(() => {
      document.getElementById("response-area")?.scrollIntoView({ behavior: "smooth", block: "start" });
    });

    try {
      const response = await askPolicyIQ(finalQuestion);
      setResult(response);
    } catch (requestError) {
      setError(requestError.message || "Something went wrong.");
      refreshStatus();
    } finally {
      setLoading(false);
    }
  }

  function selectPrompt(prompt) {
    setQuestion(prompt);
    submitQuestion(prompt);
  }

  return (
    <div className="app-shell">
      <header className="site-header">
        <div className="container header-inner">
          <Brand />
          <StatusPill status={status} onRefresh={refreshStatus} />
        </div>
      </header>

      <main>
        <section className="hero">
          <div className="container hero-grid">
            <div className="hero-copy">
              <p className="eyebrow">Grounded insurance answers</p>
              <h1>Read the policy,<br/><span>without reading every page.</span></h1>
              <p className="hero-description">
                Ask an insurance question in plain language. PolicyIQ finds the relevant passages,
                compares the evidence, and answers with the source kept in view.
              </p>

              <div className="quiet-stats" aria-label="PolicyIQ summary">
                <div><strong>11</strong><span>public documents</span></div>
                <span className="quiet-divider" />
                <div><strong>1,144</strong><span>indexed chunks</span></div>
                <span className="quiet-divider" />
                <div><strong>Grounded</strong><span>by design</span></div>
              </div>
            </div>

            <div className="hero-action">
              <QuestionComposer
                value={question}
                onChange={setQuestion}
                onSubmit={() => submitQuestion()}
                loading={loading}
                serviceReady={status.state === "ready"}
              />
              <QuickPrompts
                onSelect={selectPrompt}
                disabled={loading || status.state !== "ready"}
              />
            </div>
          </div>
        </section>

        <div id="response-area" className="response-anchor" />

        <div className="container content-container">
          {loading && <LoadingState />}
          {!loading && error && <ErrorCard message={error} onRetry={() => submitQuestion()} />}
          {!loading && result && (
            <div className="result-stack">
              <AnswerPanel result={result} />
              <SourcesPanel sources={result.sources} />
              <TimingPanel timings={result.timings} />
            </div>
          )}
          {!loading && !result && !error && <EmptyState />}
        </div>
      </main>

      <footer className="site-footer">
        <div className="container footer-inner">
          <p>PolicyIQ answers from retrieved public insurance and regulatory documents.</p>
          <p>For important decisions, verify the cited policy wording and current insurer or regulator guidance.</p>
        </div>
      </footer>
    </div>
  );
}
