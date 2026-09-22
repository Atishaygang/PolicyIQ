const prompts = [
  { eyebrow: "Motor", question: "What is the maximum No Claim Bonus?" },
  { eyebrow: "Claims", question: "What information is available about claim settlement?" },
  { eyebrow: "Policy terms", question: "What does the free-look period allow a policyholder to do?" },
];

export default function QuickPrompts({ onSelect, disabled }) {
  return (
    <div className="quick-prompts" aria-label="Example questions">
      {prompts.map((prompt) => (
        <button key={prompt.question} className="quick-prompt" type="button" onClick={() => onSelect(prompt.question)} disabled={disabled}>
          <span className="quick-prompt-eyebrow">{prompt.eyebrow}</span>
          <span className="quick-prompt-question">{prompt.question}</span>
          <span className="quick-prompt-arrow" aria-hidden="true">→</span>
        </button>
      ))}
    </div>
  );
}
