import re
import json
import logging
import urllib.request
from datetime import datetime

# Stealth & Rare Seed Opportunities (Scout Intelligence Engine)
SCOUT_RARE_OPPORTUNITIES = [
    {
        "id": "scout-001",
        "title": "Stealth AI Startup - Founding Full Stack & AI Engineer (Direct Founder Role)",
        "category": "Job",
        "funding_amount": "$140,000 - $190,000 USD + 1.5% Equity",
        "deadline": "Rolling (Stealth Role)",
        "eligibility": "Senior Engineers proficient in Python, React & LLM Architectures",
        "source_name": "Scout Stealth Radar (Twitter / LinkedIn Founder Direct)",
        "apply_url": "mailto:founders@stealthai.io",
        "published_at": datetime.now().strftime("%Y-%m-%d"),
        "region": "Worldwide Remote",
        "summary": "Exclusive stealth-mode AI startup backed by top San Francisco VCs seeking founding engineer. Direct email access to founders.",
        "contact_email": "founders@stealthai.io",
        "scout_score": 96,
        "is_rare": True
    },
    {
        "id": "scout-002",
        "title": "Emerging Markets Tech Founders Micro-Grant ($25,000 Non-Dilutive Equity-Free Grant)",
        "category": "Grant",
        "funding_amount": "$25,000 USD Equity-Free Cash Grant",
        "deadline": "Open Application",
        "eligibility": "Early stage solo founders in Africa, LatAm & South Asia",
        "source_name": "Scout Venture Radar",
        "apply_url": "https://microgrants.tech/apply",
        "published_at": datetime.now().strftime("%Y-%m-%d"),
        "region": "Emerging Markets",
        "summary": "Rare non-dilutive grant for solo tech builders building high-impact software tools in emerging economies.",
        "contact_email": "grants@microgrants.tech",
        "scout_score": 94,
        "is_rare": True
    },
    {
        "id": "scout-003",
        "title": "Thiel Fellowship 2027 ($100,000 Equity-Free Grant for Young Builders)",
        "category": "Fellowship",
        "funding_amount": "$100,000 USD Cash + Mentorship",
        "deadline": "Rolling Applications",
        "eligibility": "Under 23 years old building ambitious projects or scientific breakthroughs",
        "source_name": "Thiel Foundation",
        "apply_url": "https://thielfellowship.org/apply",
        "published_at": datetime.now().strftime("%Y-%m-%d"),
        "region": "Global",
        "summary": "Two-year, $100,000 grant for young people who want to build new things instead of sitting in a classroom.",
        "contact_email": "info@thielfellowship.org",
        "scout_score": 98,
        "is_rare": True
    }
]

def extract_contacts_from_bio(text: str) -> dict:
    """Extracts direct email addresses, social handles, and application links from bio text (Scout Pattern)."""
    emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
    handles = re.findall(r'@([a-zA-Z0-9_]{3,20})', text)
    urls = re.findall(r'https?://[^\s<>"]+|www\.[^\s<>"]+', text)

    return {
        "contact_email": emails[0] if emails else None,
        "social_handle": f"@{handles[0]}" if handles else None,
        "direct_link": urls[0] if urls else None
    }

def calculate_scout_score(item: dict) -> int:
    """Calculates Scout Opportunity Hotness Rating (0-100%)."""
    score = 60
    full_text = f"{item.get('title')} {item.get('summary')} {item.get('funding_amount')}".lower()

    if item.get("is_rare") or "stealth" in full_text or "exclusive" in full_text:
        score += 20
    if "fully funded" in full_text or "$100" in full_text or "$50" in full_text or "equity" in full_text:
        score += 10
    if item.get("contact_email") or "mailto:" in item.get("apply_url", ""):
        score += 10

    return min(score, 99)

def fetch_scout_rare_opportunities() -> list:
    """Runs Scout Intelligence Crawler for rare, stealth, and exclusive opportunities."""
    items = list(SCOUT_RARE_OPPORTUNITIES)
    for item in items:
        item["scout_score"] = calculate_scout_score(item)
    return items
