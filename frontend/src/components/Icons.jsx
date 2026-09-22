const iconProps = {
  width: 18,
  height: 18,
  viewBox: "0 0 24 24",
  fill: "none",
  stroke: "currentColor",
  strokeWidth: 1.8,
  strokeLinecap: "round",
  strokeLinejoin: "round",
  "aria-hidden": true,
};

export function ArrowUpRight() {
  return <svg {...iconProps}><path d="M7 17 17 7"/><path d="M8 7h9v9"/></svg>;
}
export function CopyIcon() {
  return <svg {...iconProps}><rect x="8" y="8" width="11" height="11" rx="2"/><path d="M16 8V6a2 2 0 0 0-2-2H6a2 2 0 0 0-2 2v8a2 2 0 0 0 2 2h2"/></svg>;
}
export function CheckIcon() {
  return <svg {...iconProps}><path d="m5 12 4 4L19 6"/></svg>;
}
export function FileIcon() {
  return <svg {...iconProps}><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8Z"/><path d="M14 2v6h6"/><path d="M8 13h8"/><path d="M8 17h6"/></svg>;
}
export function ClockIcon() {
  return <svg {...iconProps}><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg>;
}
export function RefreshIcon() {
  return <svg {...iconProps}><path d="M20 6v5h-5"/><path d="M4 18v-5h5"/><path d="M6.1 9a7 7 0 0 1 11.5-2.6L20 11"/><path d="M4 13l2.4 4.6A7 7 0 0 0 17.9 15"/></svg>;
}
export function ShieldIcon() {
  return <svg {...iconProps}><path d="M12 3 19 6v5c0 4.7-2.9 8-7 10-4.1-2-7-5.3-7-10V6l7-3Z"/><path d="m9 12 2 2 4-4"/></svg>;
}
export function ChevronDown() {
  return <svg {...iconProps}><path d="m7 10 5 5 5-5"/></svg>;
}
export function SparkIcon() {
  return <svg {...iconProps}><path d="M12 3c.8 4.3 2.7 6.2 7 7-4.3.8-6.2 2.7-7 7-.8-4.3-2.7-6.2-7-7 4.3-.8 6.2-2.7 7-7Z"/><path d="M19 16c.3 1.7 1 2.4 2.7 2.7C20 19 19.3 19.7 19 21.4c-.3-1.7-1-2.4-2.7-2.7 1.7-.3 2.4-1 2.7-2.7Z"/></svg>;
}
