import { useEffect, useRef, useState } from "react";
import PageHeader from "./components/PageHeader.jsx";
import BootSequence from "./components/BootSequence.jsx";
import TitleBar from "./components/TitleBar.jsx";
import MessageLog from "./components/MessageLog.jsx";
import QuickCommands from "./components/QuickCommands.jsx";
import InputBar from "./components/InputBar.jsx";
import { askQuestionStream, checkHealth } from "./api.js";

export default function App() {
  const [booted, setBooted] = useState(false);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [isThinking, setIsThinking] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const [online, setOnline] = useState(false);
  const typeTimeoutRef = useRef(null);
  const healthIntervalRef = useRef(null);

  useEffect(() => {
    let cancelled = false;

    const probe = async () => {
      const ok = await checkHealth();
      if (cancelled) return;
      setOnline(ok);
      // Backend just came up (or is down) — refresh status continuously
      // until we're online, then keep a slow heartbeat in case it dies.
      if (!ok) {
        clearInterval(healthIntervalRef.current);
        healthIntervalRef.current = setInterval(probe, 5000);
      } else {
        clearInterval(healthIntervalRef.current);
        healthIntervalRef.current = setInterval(probe, 30000);
      }
    };

    probe();

    return () => {
      cancelled = true;
      clearInterval(healthIntervalRef.current);
    };
  }, []);

  useEffect(() => {
    return () => clearTimeout(typeTimeoutRef.current);
  }, []);

  const sendQuestion = async (question) => {
    const trimmed = question.trim();
    if (!trimmed) return;

    setMessages((prev) => [...prev, { role: "user", content: trimmed }]);
    setInput("");
    setIsThinking(true);

    try {
      await askQuestionStream(trimmed, (chunk) => {
        setMessages((prev) => {
          const updated = [...prev];
          const lastIndex = updated.length - 1;

          // No placeholder message is pre-appended: if the stream
          // hasn't started yet, the last message is still the user's.
          // Create the assistant message on its first chunk so we never
          // render a blank bubble while waiting.
          if (updated[lastIndex].role !== "assistant") {
            updated.push({ role: "assistant", content: chunk });
          } else {
            updated[lastIndex] = {
              ...updated[lastIndex],
              content: updated[lastIndex].content + chunk,
            };
          }
          return updated;
        });
      });
    } catch (err) {
      setMessages((prev) => {
        const updated = [...prev];
        const lastIndex = updated.length - 1;
        const errorText = `Error: ${err.message}. The backend may be offline or misconfigured.`;

        if (updated[lastIndex].role === "assistant") {
          // Stream started but died mid-way — annotate the partial answer.
          updated[lastIndex] = {
            ...updated[lastIndex],
            content: `${updated[lastIndex].content}\n\n${errorText}`,
            isError: true,
          };
        } else {
          updated.push({ role: "assistant", content: errorText, isError: true });
        }
        return updated;
      });
    } finally {
      setIsThinking(false);
    }
  };

  const runCommand = (question) => {
    if (isTyping || isThinking) return;
    setIsTyping(true);
    setInput("");

    let i = 0;
    const typeNext = () => {
      if (i <= question.length) {
        setInput(question.slice(0, i));
        i += 1;
        typeTimeoutRef.current = setTimeout(typeNext, 18);
      } else {
        setIsTyping(false);
        typeTimeoutRef.current = setTimeout(() => sendQuestion(question), 250);
      }
    };
    typeNext();
  };

  const busy = isThinking || isTyping;

  return (
    <>
      <div className="ambient" aria-hidden="true">
        <div className="ambient-grid" />
        <div className="ambient-glow" />
        <div className="ambient-vignette" />
      </div>

      <div className="page">
        <div className="page-inner">
          <PageHeader />

          <div className="terminal">
            <TitleBar online={online} />
            {!booted ? (
              <BootSequence onComplete={() => setBooted(true)} />
            ) : (
              <>
                <MessageLog messages={messages} isThinking={isThinking} />
                <QuickCommands onSelect={runCommand} disabled={busy} />
                <InputBar
                  value={input}
                  onChange={setInput}
                  onSubmit={() => sendQuestion(input)}
                  disabled={busy}
                />
              </>
            )}
          </div>

          <p className="footnote">
            grounded in resume.pdf + profile_data.json — no invented answers
          </p>
        </div>
      </div>
    </>
  );
}
