from pathlib import Path
from pypdf import PdfReader


def read_pdf(file_path: Path) -> str:
    """Extracts text from a PDF file on disk."""
    if not file_path.exists():
        raise FileNotFoundError(f"PDF not found at: {file_path}")

    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"

    return text