import logging
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from models import ChatRequest, Resume, PersonalProfile
from pdf_utils import read_pdf
from profile_utils import load_profile
from llm import parse_resume, ask_candidate_stream

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Personal AI Assistant")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "https://padho-ai-engineer-b2g4a4ud2-raiadarsh127-1015s-projects.vercel.app/"
        "https://padho-ai-engineer-git-main-raiadarsh127-1015s-projects.vercel.app/",
        "https://padho-ai-engineer-b2g4a4ud2-raiadarsh127-1015s-projects.vercel.app/"
    ],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).parent
RESUME_PATH = BASE_DIR / "Adarsh3_resume_.pdf"
PROFILE_PATH = BASE_DIR / "profile_data.json"

_cached_resume: Optional[Resume] = None
_cached_profile: Optional[PersonalProfile] = None


def get_resume() -> Resume:
    global _cached_resume
    if _cached_resume is None:
        logger.info(f"Parsing resume from {RESUME_PATH} ...")
        resume_text = read_pdf(RESUME_PATH)
        _cached_resume = parse_resume(resume_text)
        logger.info("Resume parsed and cached.")
    return _cached_resume


def get_profile() -> PersonalProfile:
    global _cached_profile
    if _cached_profile is None:
        logger.info(f"Loading profile from {PROFILE_PATH} ...")
        _cached_profile = load_profile(PROFILE_PATH)
        logger.info("Profile loaded and cached.")
    return _cached_profile


@app.get("/")
def home():
    return {"message": "Personal AI Assistant is running"}


def _http_error(e: Exception) -> HTTPException:
    """Maps any exception to a clean 500 with a readable message."""
    logger.error("Request failed: %s", e, exc_info=True)
    return HTTPException(status_code=500, detail=str(e))


@app.get("/resume", response_model=Resume)
def get_resume_route():
    try:
        return get_resume()
    except Exception as e:
        raise _http_error(e)


@app.get("/profile", response_model=PersonalProfile)
def get_profile_route():
    try:
        return get_profile()
    except Exception as e:
        raise _http_error(e)


@app.post("/chat")
def chat(request: ChatRequest):
    # Load resume/profile BEFORE starting the stream — once StreamingResponse
    # starts, headers are already sent, so we can't raise a clean
    # HTTPException mid-stream if loading fails.
    try:
        resume = get_resume()
        profile = get_profile()
    except Exception as e:
        raise _http_error(e)

    def event_stream():
        try:
            for chunk in ask_candidate_stream(request.question, resume, profile):
                yield chunk
        except Exception as e:
            logger.exception("Error during streaming in /chat")
            # Marker the frontend detects to surface this as an error instead
            # of plain assistant text (headers are already sent by now).
            yield f"\n\n__STREAM_ERROR__ {e}"

    return StreamingResponse(event_stream(), media_type="text/plain")


@app.post("/reload-data")
def reload_data():
    global _cached_resume, _cached_profile
    _cached_resume = None
    _cached_profile = None
    return {"message": "Resume and profile cache cleared, will reload on next request."}
