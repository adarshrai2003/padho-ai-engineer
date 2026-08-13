import { useEffect, useRef } from "react";
import Message from "./Message.jsx";

export default function MessageLog({ messages, isThinking }) {
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isThinking]);

  return (
    <div className="log">
      {messages.length === 0 && (
        <div className="welcome">
          This terminal is connected to a live AI grounded in Adarsh's
          resume and profile.
          <br />
          Ask a real interview question, or run a command below.
          <span className="cursor-blink" />
        </div>
      )}

      {messages.map((msg, i) => (
        <Message key={i} role={msg.role} content={msg.content} isError={msg.isError} />
      ))}

      {isThinking && messages[messages.length - 1]?.role !== "assistant" && (
        <div className="msg assistant">
          <div className="msg-row">
            <span className="avatar avatar-ai">AI</span>
            <div className="msg-bubble">
              <span className="cursor-blink" />
            </div>
          </div>
        </div>
      )}

      <div ref={bottomRef} />
    </div>
  );
}
