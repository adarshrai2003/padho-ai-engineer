export default function InputBar({ value, onChange, onSubmit, disabled }) {
  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !disabled && value.trim()) {
      onSubmit();
    }
  };

  return (
    <div className="input-bar">
      <span className="prompt-label">$</span>
      <input
        type="text"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="Ask a question..."
        disabled={disabled}
        aria-label="Ask a question"
      />
      <button
        className="send-btn"
        onClick={onSubmit}
        disabled={disabled || !value.trim()}
        type="button"
      >
        run
      </button>
    </div>
  );
}
