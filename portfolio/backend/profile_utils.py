import json
from pathlib import Path

from models import PersonalProfile


def load_profile(file_path: Path) -> PersonalProfile:
    if not file_path.exists():
        raise FileNotFoundError(
            f"Profile data not found at: {file_path}. Create it with your. "
            f"weaknesses, hobbies, five-year vision, etc."
        )

    try:
        with open(file_path, "r") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"profile_data.json is not valid JSON: {e}")

    return PersonalProfile(**data)