export default function ErrorCard({ message, onRetry }) {
  return (
    <section className="error-card" role="alert">
      <div><p className="result-eyebrow">Something interrupted the request</p><h2>PolicyIQ couldn’t finish that answer.</h2><p>{message}</p></div>
      <button type="button" className="secondary-button" onClick={onRetry}>Try again</button>
    </section>
  );
}
