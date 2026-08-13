export default function TitleBar({ online }) {
  return (
    <div className="titlebar">
      <span className={`status-dot ${online ? "online" : "offline"}`} />
      <span className="titlebar-path">guest@portfolio</span>
      <span>:</span>
      <span className="titlebar-path">~/interview</span>
      <span>{online ? "$" : " — connecting..."}</span>
    </div>
  );
}
