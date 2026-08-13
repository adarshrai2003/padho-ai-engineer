export default function TitleBar({ online }) {
  return (
    <div className="titlebar">
      <div className="titlebar-dots" aria-hidden="true">
        <span className="titlebar-dot" />
        <span className="titlebar-dot" />
        <span className="titlebar-dot" />
      </div>
      <span className="titlebar-title">
        candidate@portfolio <span className="titlebar-dir">~/interview</span>
      </span>
      <span
        className={`status-dot ${online ? "online" : "offline"}`}
        title={online ? "online" : "offline"}
        aria-label={online ? "Backend online" : "Backend offline"}
      />
    </div>
  );
}
