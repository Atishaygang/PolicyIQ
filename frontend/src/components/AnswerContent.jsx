function normalizeText(text) {
  return (text || "").replace(/\[\*\*SOURCE\s+(\d+)\*\*\]/gi, "[SOURCE $1]");
}

function InlineText({ text, onSource }) {
  const parts = text.split(/(\*\*[^*]+\*\*|\[SOURCE\s+\d+\])/gi);

  return parts.map((part, index) => {
    const sourceMatch = part.match(/^\[SOURCE\s+(\d+)\]$/i);
    if (sourceMatch) {
      const sourceNumber = Number(sourceMatch[1]);
      return (
        <button key={`${part}-${index}`} type="button" className="inline-source" onClick={() => onSource(sourceNumber)}>
          Source {sourceNumber}
        </button>
      );
    }

    if (part.startsWith("**") && part.endsWith("**")) {
      return <strong key={`${part}-${index}`}>{part.slice(2, -2)}</strong>;
    }

    return <span key={`${part}-${index}`}>{part}</span>;
  });
}

export default function AnswerContent({ text, onSource }) {
  const lines = normalizeText(text).split(/\r?\n/);
  const blocks = [];
  let bullets = [];

  function flushBullets() {
    if (!bullets.length) return;
    blocks.push(
      <ul key={`list-${blocks.length}`} className="answer-list">
        {bullets.map((line, index) => <li key={`${line}-${index}`}><InlineText text={line} onSource={onSource}/></li>)}
      </ul>
    );
    bullets = [];
  }

  lines.forEach((rawLine, index) => {
    const line = rawLine.trim();
    if (!line) { flushBullets(); return; }
    if (/^[-•]\s+/.test(line)) { bullets.push(line.replace(/^[-•]\s+/, "")); return; }
    flushBullets();
    blocks.push(<p key={`paragraph-${index}`}><InlineText text={line} onSource={onSource}/></p>);
  });

  flushBullets();
  return <div className="answer-prose">{blocks}</div>;
}
