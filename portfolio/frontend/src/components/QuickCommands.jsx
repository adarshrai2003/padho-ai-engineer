const COMMANDS = [
  { label: "whoami", question: "Tell me about your background and experience." },
  { label: "--strengths", question: "What are your key strengths?" },
  { label: "--weaknesses", question: "What's your biggest weakness?" },
  { label: "--five-year-plan", question: "Where do you see yourself in 5 years?" },
  { label: "--work-style", question: "How do you prefer to work?" },
  { label: "--hire-me", question: "Why should we hire you?" },
];

export default function QuickCommands({ onSelect, disabled }) {
  return (
    <div className="commands">
      {COMMANDS.map((cmd) => (
        <button
          key={cmd.label}
          className="chip"
          onClick={() => onSelect(cmd.question)}
          disabled={disabled}
          type="button"
        >
          {cmd.label}
        </button>
      ))}
    </div>
  );
}
