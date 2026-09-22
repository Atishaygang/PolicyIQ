import { ShieldIcon, SparkIcon, FileIcon } from "./Icons";

const items = [
  { icon: <FileIcon/>, title: "Document-grounded", text: "Answers are built from retrieved policy and regulatory passages." },
  { icon: <ShieldIcon/>, title: "Comfortable saying “not enough”", text: "When evidence is insufficient, PolicyIQ abstains instead of guessing." },
  { icon: <SparkIcon/>, title: "Clear by design", text: "Sources and page numbers stay close to every answer." },
];

export default function EmptyState() {
  return (
    <section className="principles-section">
      <div className="section-heading principles-heading"><div><p className="result-eyebrow">Designed for clarity</p><h2>Useful answers, with the evidence kept visible.</h2></div></div>
      <div className="principle-grid">
        {items.map((item) => <article className="principle-card" key={item.title}><span className="principle-icon">{item.icon}</span><h3>{item.title}</h3><p>{item.text}</p></article>)}
      </div>
    </section>
  );
}
