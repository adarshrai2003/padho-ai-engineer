export default function Message({ role, content, isError }) {
  const isUser = role === "user";

  return (
    <div className={`msg ${role}`}>
      <div className="msg-row">
        {!isUser && <span className="avatar avatar-ai">AI</span>}
        <div className={`msg-bubble ${isError ? "error" : ""}`}>{content}</div>
        {isUser && <span className="avatar avatar-user">&gt;</span>}
      </div>
    </div>
  );
}
