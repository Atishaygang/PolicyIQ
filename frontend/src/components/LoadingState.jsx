import { useEffect, useState } from "react";

const stages = [
  "Finding the most relevant policy clauses",
  "Comparing evidence across documents",
  "Preparing a grounded answer",
];

export default function LoadingState() {
  const [stage, setStage] = useState(0);

  useEffect(() => {
    const timer = window.setInterval(() => {
      setStage((current) => Math.min(current + 1, stages.length - 1));
    }, 9000);
    return () => window.clearInterval(timer);
  }, []);

  return (
    <section className="loading-card" aria-live="polite">
      <div className="loading-orbit" aria-hidden="true"><span/><span/><span/></div>
      <div>
        <p className="result-eyebrow">Reading the evidence</p>
        <h2>{stages[stage]}</h2>
        <p>PolicyIQ reranks retrieved passages before answering, so a response can take a little while.</p>
      </div>
    </section>
  );
}
