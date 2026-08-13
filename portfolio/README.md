# Portfolio — Ask Adarsh (AI Interview Agent)

An interactive, terminal-styled web app that answers interview questions **as Adarsh**, grounded strictly in two data sources:

- `backend/Adarsh3_resume_.pdf` — the candidate's actual resume
- `backend/profile_data.json` — Adarsh's own written answers to personal/reflective questions

The AI **never invents content**. Anything not present in those two files is answered with *"I don't have enough information to answer that."*

---

## 📁 Folder Structure

```
portfolio/
├── backend/                       # FastAPI server (Python)
│   ├── main.py                    # FastAPI app, routes, CORS, caching, streaming
│   ├── llm.py                     # Groq LLM client: resume parsing + interview answers
│   ├── models.py                  # Pydantic models (Resume, PersonalProfile, ChatRequest)
│   ├── pdf_utils.py               # PDF text extraction (pypdf)
│   ├── profile_utils.py           # profile_data.json loader -> PersonalProfile
│   ├── profile_data.json          # Personal answers (weaknesses, strengths, hobbies, ...)
│   ├── Adarsh3_resume_.pdf        # The resume that gets parsed
│   ├── .env.example               # Template for GROQ_API_KEY / GROQ_MODEL
│   └── .gitignore                 # Ignores .env, .DS_Store
├── frontend/                      # React + Vite SPA
│   ├── index.html                 # Entry HTML (fonts, favicon)
│   ├── vite.config.js             # Vite + React plugin
│   ├── package.json               # React 18, Vite 5
│   ├── public/favicon.svg         # Amber serif "A" favicon
│   ├── .env.example               # Template for VITE_API_URL
│   └── src/
│       ├── main.jsx               # React entry point
│       ├── App.jsx                # App state, streaming logic, boot flow
│       ├── api.js                 # askQuestionStream() + checkHealth()
│       ├── index.css              # Full design system (editorial-terminal theme)
│       └── components/
│           ├── BootSequence.jsx   # Terminal boot animation
│           ├── TitleBar.jsx       # Traffic-light window chrome + status dot
│           ├── PageHeader.jsx     # Serif headline "Ask Adarsh"
│           ├── MessageLog.jsx     # Scrollable chat log + thinking indicator
│           ├── Message.jsx        # Single user/AI message bubble
│           ├── QuickCommands.jsx  # One-click interview question chips
│           └── InputBar.jsx       # Prompt input + run button
├── main.py                        # Placeholder entry (uv project scaffold)
├── pyproject.toml                 # Python project metadata + dependencies
└── uv.lock                        # Locked Python dependencies
```

---

## 🧠 Tech Stack

| Layer    | Technology                                      |
| -------- | ----------------------------------------------- |
| Backend  | Python ≥ 3.12, FastAPI, Uvicorn, Pydantic v2    |
| LLM      | Groq SDK (`groq`), JSON-mode resume parsing     |
| PDF      | `pypdf` text extraction                         |
| Frontend | React 18, Vite 5, plain CSS (no UI framework)   |
| Fonts    | Fraunces (serif), Inter (sans), JetBrains Mono  |
| Env      | `python-dotenv`, `.env` files (gitignored)      |

---

## 🔌 How It Works

1. **On first request**, the backend reads `Adarsh3_resume_.pdf`, extracts text, and sends it to Groq with a strict parsing prompt (JSON mode, `temperature=0`). The result is validated into a `Resume` model and **cached in memory**.
2. `profile_data.json` is loaded once into a `PersonalProfile` model and also cached.
3. When a question arrives at `/chat`, FastAPI builds a system prompt containing **both** data sources and streams the LLM's answer back to the browser token-by-token.
4. The React frontend renders the stream incrementally, showing a blinking cursor while waiting for the first chunk.

All answers are grounded: the system prompt explicitly forbids hallucination and instructs the model to draw personal/reflective answers from `PersonalProfile`, not the resume.

---

## 🌐 API Reference

| Method | Endpoint          | Description                                                                 |
| ------ | ----------------- | --------------------------------------------------------------------------- |
| GET    | `/`               | Health check — `{"message": "Personal AI Assistant is running"}`           |
| GET    | `/resume`         | Returns the parsed `Resume` (LLM-parsed from the PDF, then cached)          |
| GET    | `/profile`        | Returns the `PersonalProfile` loaded from `profile_data.json`               |
| POST   | `/chat`           | Streams an interview answer. Body: `{"question": "..."}` → `text/plain` SSE |
| POST   | `/reload-data`    | Clears the resume/profile cache so data reloads on the next request         |

### `/chat` streaming protocol

- Response is `text/plain` with a continuous stream of text chunks.
- If the LLM stream fails **after** headers were sent, the backend appends:
  ```
  __STREAM_ERROR__ <message>
  ```
  The frontend detects this sentinel, stops streaming, and renders the partial answer + error in error styling.
- Non-stream errors return a JSON `{"detail": "..."}` with HTTP 500.

### CORS

Allowed origins: `http://localhost:5173`, `http://127.0.0.1:5173`, `http://localhost:5174`, `http://127.0.0.1:5174`. Methods: `GET`, `POST`.

---

## 🚀 Setup & Running

### Prerequisites

- Python ≥ 3.12 (with [uv](https://docs.astral.sh/uv/) recommended)
- Node.js ≥ 18 + npm
- A [Groq](https://console.groq.com/) API key

### 1. Backend

```bash
cd portfolio/backend

# create your environment file
cp .env.example .env
# edit .env and set your real key:
#   GROQ_API_KEY=your_groq_key
#   GROQ_MODEL=openai/gpt-oss-120b   (optional, defaults to openai/gpt-oss-120b)

# install dependencies and start (from portfolio/ to use the project venv)
cd ..
uv sync
uv run uvicorn backend.main:app --reload --port 8000
```

The server runs at `http://localhost:8000`. Interactive docs at `http://localhost:8000/docs`.

> **Note:** If `GROQ_API_KEY` is missing, the backend refuses to start with a clear message instead of crashing obscurely. `load_dotenv()` picks up a `.env` from the current working directory — running uvicorn from `portfolio/` with a `.env` in `portfolio/` or `portfolio/backend/` both work.

### 2. Frontend

```bash
cd portfolio/frontend
npm install

# optional: point the API elsewhere (defaults to http://localhost:8000)
cp .env.example .env   # VITE_API_URL=http://localhost:8000

npm run dev
```

Open **http://localhost:5173**.

### 3. Quick smoke test

```bash
# health
curl http://localhost:8000/

# profile data
curl http://localhost:8000/profile

# streaming chat
curl -N -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"question":"Why should we hire you?"}'
```

---

## 🖥️ Frontend Features

- **Editorial terminal theme** — Fraunces serif headline with italic amber accent, JetBrains Mono terminal text, warm espresso palette, amber/sage glows, paper-grain background, animated entrance.
- **Boot sequence** — styled terminal boot lines ("mounting resume.pdf … OK") before the chat appears.
- **Traffic-light chrome** — macOS-style window dots (red/yellow/green), centered title `candidate@portfolio ~/-Adarsh`, and a live **status dot** (green = backend online, red = offline, pulsing while online).
- **Health polling** — checks the backend every 5s while offline, every 30s while online, so the status dot self-heals.
- **Streaming responses** — answers appear token-by-token; a thin amber caret blinks until the first chunk arrives, then sits inline while text streams.
- **Typewriter quick commands** — chip buttons ("whoami", "--strengths", "--weaknesses", "--five-year-plan", "--work-style", "--hire-me") simulate typing the question into the input bar before submitting.
- **Error handling** — failed requests and mid-stream failures render in red error styling, never as silent failures.
- **Accessibility & polish** — `prefers-reduced-motion` respected, keyboard focus indicators, mobile full-height layout, custom scrollbars.
- **Multi-byte safe streaming** — uses `TextDecoder(stream: true)` so UTF-8 characters are never split incorrectly.

### Quick commands

| Command            | Asks                                                                            |
| ------------------ | ------------------------------------------------------------------------------- |
| `whoami`           | Tell me about your background and experience.                                   |
| `--strengths`      | What are your key strengths?                                                    |
| `--weaknesses`     | What's your biggest weakness?                                                   |
| `--five-year-plan` | Where do you see yourself in 5 years?                                          |
| `--work-style`     | How do you prefer to work?                                                      |
| `--hire-me`        | Why should we hire you?                                                         |

---

## 🗂️ Data Files

### `backend/profile_data.json` — all keys must match `PersonalProfile` in `models.py`

```json
{
  "weaknesses": ["..."],
  "strengths": ["..."],
  "hobbies": ["..."],
  "five_year_vision": "...",
  "values": ["..."],
  "work_style": "...",
  "fun_facts": ["..."],
  "family_members": ["..."],
  "hire_me": ["..."]
}
```

> ⚠️ **Case matters.** The key is `hire_me` (lowercase `h`). A mismatched key is silently ignored by Pydantic, and the model will answer "not enough information" for hire-me questions.

### `backend/Adarsh3_resume_.pdf`

Must be a PDF with an **extractable text layer** (not a scanned image). It is read once and LLM-parsed into a `Resume` model:

```python
class Resume(BaseModel):
    name, email, phone, location, total_experience_years
    skills: list[str]
    experiences: list[Experience]   # company, role, duration, description, skills_used
    education, projects, certifications, achievements: list[str]
```

To use a different resume, replace the PDF and restart the backend (or call `POST /reload-data`).

---

## 🛠️ Backend Code Map

| File              | Responsibility                                                                 |
| ----------------- | ------------------------------------------------------------------------------ |
| `main.py`         | FastAPI app, CORS middleware, route handlers, in-memory caching, `_http_error` helper, stream error sentinel |
| `llm.py`          | Groq client; `parse_resume()` (strict JSON extraction) and `ask_candidate_stream()` (grounded interview answers); API-key guard + model selection via env |
| `models.py`       | Pydantic schemas: `Experience`, `Resume`, `PersonalProfile`, `ChatRequest`     |
| `pdf_utils.py`    | `read_pdf()` — extracts text from a PDF path with a friendly error if missing  |
| `profile_utils.py`| `load_profile()` — loads + validates `profile_data.json` into `PersonalProfile`|

### Prompt design highlights

- **Resume parsing** uses JSON mode, `temperature=0`, merges experience-like sections by meaning, extracts skills from anywhere, deduplicates, and requires all keys (empty lists / nulls instead of omissions).
- **Interview answering** uses `temperature=0.3`, first-person voice ("I …"), explicit no-hallucination rules, and directs reflective questions to `PersonalProfile`.

---

## ⚠️ Troubleshooting

| Symptom                                  | Fix                                                                                   |
| ---------------------------------------- | ------------------------------------------------------------------------------------- |
| Backend won't start                      | `GROQ_API_KEY` missing → create `portfolio/backend/.env` from `.env.example`          |
| "model not found" on every LLM call      | `GROQ_MODEL` isn't served by your Groq account → set one that is (e.g. `llama-3.3-70b-versatile`) |
| Frontend status dot stays red            | Backend not running or CORS origin mismatch → start backend on :8000; dev server on :5173/:5174 |
| `--hire-me` answers "not enough info"    | `profile_data.json` must use the lowercase `hire_me` key                              |
| Chat error style / `__STREAM_ERROR__`    | Transient Groq/network failure mid-stream — retry                                     |
| Page won't load                          | Vite dev server died → restart with `npm run dev` (backend at :8000 can stay up)      |

---

## 🔒 Notes & Limitations

- **No secrets in git.** `.env`, `node_modules/`, `.venv/`, `__pycache__/`, and `dist/` are gitignored. Only `.env.example` templates are committed.
- `/reload-data` has no auth — fine for local dev; protect it if ever exposed publicly.
- CORS is limited to localhost dev origins only.
- Resume/profile are cached in memory (`_cached_resume`, `_cached_profile`) — edits to `profile_data.json` or the PDF require `POST /reload-data` or a restart.
- LLM answers are deterministic-grounded but still model-generated — always LLM output, never a verbatim file read.
