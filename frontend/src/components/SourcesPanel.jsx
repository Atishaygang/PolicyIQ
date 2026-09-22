import { FileIcon } from "./Icons";

export default function SourcesPanel({ sources = [] }) {
  if (!sources.length) return null;

  return (
    <section className="sources-section">
      <div className="section-heading">
        <div><p className="result-eyebrow">Evidence used</p><h2>Sources</h2></div>
        <span className="source-count">{sources.length} {sources.length === 1 ? "source" : "sources"}</span>
      </div>

      <div className="sources-grid">
        {sources.map((source, index) => (
          <article id={`source-${index + 1}`} className="source-card" key={`${source.document_id}-${source.page}-${index}`}>
            <div className="source-icon"><FileIcon/></div>
            <div className="source-body">
              <span className="source-number">Source {index + 1}</span>
              <h3>{source.filename}</h3>
              <div className="source-meta"><span>{source.document_id}</span><span className="meta-divider"/><span>Page {source.page}</span></div>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}
