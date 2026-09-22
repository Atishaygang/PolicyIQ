import { RefreshIcon } from "./Icons";

export default function StatusPill({ status, onRefresh }) {
  const label =
    status.state === "checking" ? "Checking service" :
    status.state === "ready" ? "PolicyIQ ready" :
    status.state === "warming" ? "Getting ready" : "Service offline";

  return (
    <button className={`status-pill status-${status.state}`} type="button" onClick={onRefresh} title="Check PolicyIQ service status">
      <span className="status-dot" />
      <span>{label}</span>
      <span className="status-refresh"><RefreshIcon /></span>
    </button>
  );
}
