import { useState } from "react";
import AnswerContent from "./AnswerContent";
import { CheckIcon, CopyIcon, ShieldIcon } from "./Icons";

const ABSTENTION = "I could not find sufficient information in the provided documents.";

export default function AnswerPanel({ result }) {
  const [copied, setCopied] = useState(false);
  const isAbstention = result.answer?.trim().toLowerCase() === ABSTENTION.toLowerCase();

  async function copyAnswer() {
    try {
      await navigator.clipboard.writeText(result.answer);
      setCopied(true);
      window.setTimeout(() => setCopied(false), 1600);
    } catch { setCopied(false); }
  }

  function scrollToSource(sourceNumber) {
    document.getElementById(`source-${sourceNumber}`)?.scrollIntoView({ behavior: "smooth", block: "center" });
  }

  return (
    <section className={`answer-card ${isAbstention ? "answer-abstention" : ""}`}>
      <div className="answer-topline">
        <div>
          <p className="result-eyebrow">{isAbstention ? "Evidence check" : "Policy answer"}</p>
          <h2>{result.question}</h2>
        </div>
        {!isAbstention && (
          <button type="button" className="icon-text-button" onClick={copyAnswer}>
            {copied ? <CheckIcon/> : <CopyIcon/>}<span>{copied ? "Copied" : "Copy"}</span>
          </button>
        )}
      </div>

      {isAbstention ? (
        <div className="abstention-message">
          <span className="abstention-icon"><ShieldIcon/></span>
          <div>
            <h3>I don’t have enough evidence to answer that safely.</h3>
            <p>PolicyIQ could not find sufficient support in the available documents, so it chose not to guess.</p>
          </div>
        </div>
      ) : <AnswerContent text={result.answer} onSource={scrollToSource}/>} 
    </section>
  );
}
