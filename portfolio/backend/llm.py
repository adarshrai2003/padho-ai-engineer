import json
import logging
import os

from dotenv import load_dotenv
from groq import Groq

from models import Resume, PersonalProfile

load_dotenv()

logger = logging.getLogger(__name__)

API_KEY = os.getenv("GROQ_API_KEY")
if not API_KEY:
    raise RuntimeError(
        "GROQ_API_KEY is not set. Create a backend/.env file with "
        "GROQ_API_KEY=your_key (copy .env.example) and restart the server."
    )

client = Groq(api_key=API_KEY)
MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")


RESUME_EXAMPLE = {
    "name": "Jane Doe",
    "email": "jane@example.com",
    "phone": "+1-555-123-4567",
    "total_experience_years": 2.5,
    "skills": ["Python", "FastAPI", "SQL"],
    "experiences": [
        {
            "company": "Acme Corp",
            "role": "Software Engineer Intern",
            "duration": "Jun 2023 - Aug 2023",
            "description": "Built internal tools using Python and FastAPI.",
            "skills_used": ["Python", "FastAPI"],
        }
    ],
    "education": ["B.Tech in Computer Science, XYZ University, 2024"],
    "projects": ["Resume parsing pipeline using LLMs"],
    "certifications": ["AWS Certified Cloud Practitioner"],
}

RESUME_PARSER_SYSTEM_PROMPT = f"""You are an expert resume parser.

Extract information from the resume based on its MEANING, not only exact
section headings — different resumes label the same content differently.
Merge "Experience", "Professional Experience", "Work History",
"Employment", and "Internships" all into the "experiences" list. Skills
may appear in a dedicated skills section, or scattered across experience,
internships, or project descriptions — extract them from anywhere.

Return ONLY valid JSON matching this exact shape (example, not real data):

{json.dumps(RESUME_EXAMPLE, indent=2)}

Rules:
1. Extract ONLY information explicitly present in the resume text. Never
   invent, guess, or infer missing details.
2. If a single value isn't available, use null. If a list has no items,
   use an empty list — never omit a key.
3. Include internships inside "experiences", not as a separate category.
4. Deduplicate skills.
5. Return ONLY the JSON object. No markdown fences, no commentary.
"""


def parse_resume(resume_text: str) -> Resume:
    if not resume_text or not resume_text.strip():
        raise ValueError(
            "resume_text is empty — check the PDF path and confirm the "
            "PDF actually has an extractable text layer."
        )

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": RESUME_PARSER_SYSTEM_PROMPT},
            {"role": "user", "content": f"Parse the following resume:\n\n{resume_text}"},
        ],
        temperature=0,
        response_format={"type": "json_object"},
    )

    raw_output = response.choices[0].message.content

    try:
        data = json.loads(raw_output)
    except json.JSONDecodeError as e:
        logger.error(f"Model returned invalid JSON: {raw_output}")
        raise ValueError(f"Failed to parse model output as JSON: {e}")

    return Resume(**data)


def _build_candidate_system_prompt(resume: Resume, profile: PersonalProfile) -> str:
    return f"""You are an AI assistant representing a job candidate
in an interview-style conversation.

RESUME DATA (verified facts from their resume):
{resume.model_dump_json(indent=2)}

PERSONAL PROFILE (their own stated answers to common interview questions —
weaknesses, strengths, hobbies, career vision, work style):
{profile.model_dump_json(indent=2)}

Rules:
1. Answer ONLY using information present above. Never invent, guess, or
   infer details not explicitly stated in either section.
2. Never hallucinate specifics (dates, numbers, company names) not
   present above.
3. If information genuinely isn't available in either section, say
   "I don't have enough information to answer that."
4. Be professional and conversational — answer in first person ("I ..."),
   as if the candidate is speaking for themselves.
5. Deduplicate skills if listed multiple times.
6. For personal/reflective questions (weaknesses, five-year vision,
   hobbies), draw from the PERSONAL PROFILE section, not the resume.
"""


def ask_candidate_stream(question: str, resume: Resume, profile: PersonalProfile):
    """Streaming generator — yields text chunks as the model produces them,
    instead of waiting for the full answer. This is what /chat now uses so
    the frontend can render text progressively, like ChatGPT."""
    system_prompt = _build_candidate_system_prompt(resume, profile)

    stream = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question},
        ],
        temperature=0.3,
        stream=True,
    )

    for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta:
            yield delta
