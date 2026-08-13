import { useEffect, useState } from "react";

const LINES = [
  { text: "booting candidate_interface.sh" },
  { text: "mounting resume.pdf", suffix: "OK" },
  { text: "mounting profile_data.json", suffix: "OK" },
  { text: "establishing model session", suffix: "OK" },
];

export default function BootSequence({ onComplete }) {
  const [visibleLines, setVisibleLines] = useState(0);
  const [done, setDone] = useState(false);

  useEffect(() => {
    const reduceMotion = window.matchMedia(
      "(prefers-reduced-motion: reduce)"
    ).matches;

    if (reduceMotion) {
      onComplete();
      return;
    }

    if (visibleLines < LINES.length) {
      const t = setTimeout(() => setVisibleLines((n) => n + 1), 240);
      return () => clearTimeout(t);
    }

    const t = setTimeout(() => {
      setDone(true);
      setTimeout(onComplete, 450);
    }, 450);
    return () => clearTimeout(t);
  }, [visibleLines, onComplete]);

  return (
    <div className={`boot ${done ? "boot-done" : ""}`}>
      {LINES.slice(0, visibleLines).map((line, i) => (
        <div className="boot-line" key={i}>
          <span className="boot-caret">&gt;</span>
          {line.text}
          {line.suffix && <span className="boot-ok">......... {line.suffix}</span>}
        </div>
      ))}
      {visibleLines >= LINES.length && (
        <div className="boot-line boot-ready">
          <span className="boot-caret">&gt;</span>
          READY
          <span className="cursor-blink" />
        </div>
      )}
    </div>
  );
}
