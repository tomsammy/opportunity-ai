import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

DB_PATH = os.path.join(DATA_DIR, "opportunities.json")
CHROMA_DB_DIR = os.path.join(DATA_DIR, "chroma_db")

# Default Seed Sources for High-Value Opportunities & News
SEED_SOURCES = [
    {
        "name": "DAAD Scholarships Portal",
        "url": "https://www me.daad.de/en/",  # Mocked/Handled with fallback structured generator
        "type": "scholarship",
        "category": "Scholarship",
        "region": "Germany / Europe"
    },
    {
        "name": "Opportunities For Africans & International Students",
        "url": "https://www.opportunitiesforafricans.com/feed/",
        "type": "rss",
        "category": "Scholarship",
        "region": "Global"
    },
    {
        "name": "We Work Remotely",
        "url": "https://weworkremotely.com/remote-jobs.rss",
        "type": "rss",
        "category": "Job",
        "region": "Remote"
    },
    {
        "name": "TechCrunch AI & Tech News",
        "url": "https://techcrunch.com/category/artificial-intelligence/feed/",
        "type": "rss",
        "category": "News",
        "region": "Global"
    }
]

HOST = os.environ.get("HOST", "0.0.0.0")
PORT = int(os.environ.get("PORT", 8000))
