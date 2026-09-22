export default function Brand() {
  return (
    <div className="brand" aria-label="PolicyIQ">
      <div className="brand-mark" aria-hidden="true">
        <svg viewBox="0 0 44 44" fill="none">
          <path d="M12.5 12.5c4.3 0 6.9 1.1 9.5 3.8 2.6-2.7 5.2-3.8 9.5-3.8v17.2c-4.1 0-6.7 1-9.5 2.9-2.8-1.9-5.4-2.9-9.5-2.9V12.5Z" fill="currentColor"/>
          <path d="M22 16.6v15" stroke="#8EA58F" strokeWidth="1.8"/>
        </svg>
      </div>
      <div className="brand-copy">
        <span className="brand-name">PolicyIQ</span>
        <span className="brand-subtitle">Insurance, made readable</span>
      </div>
    </div>
  );
}
