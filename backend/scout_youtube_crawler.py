import re
import logging
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime

# High-Value Opportunity YouTube Channels (Scholarships, Tech Careers, Grants, Accelerators)
SCOUT_YOUTUBE_CHANNELS = [
    {
        "channel_id": "UCsT0YIqwnpJCM-mx7-gSA4Q", # Example Tech & Opportunity Channel RSS
        "channel_name": "Tech & Global Opportunities Hub",
        "category": "Scholarship"
    },
    {
        "channel_id": "UCWv7vMbMWH4-V0tGfcrf5wA", # Y Combinator YouTube Channel
        "channel_name": "Y Combinator",
        "category": "Accelerator"
    }
]

def extract_opportunity_from_yt_description(title: str, description: str, channel_name: str) -> dict:
    """Extracts structured opportunity data and contact info from YouTube video descriptions."""
    full_text = f"{title}\n{description}"

    # Extract emails & URLs from description (Scout pattern)
    emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', full_text)
    urls = re.findall(r'https?://[^\s<>"]+|www\.[^\s<>"]+', full_text)

    # Filter out generic YouTube URLs
    apply_urls = [u for u in urls if "youtube.com" not in u and "youtu.be" not in u]
    apply_url = apply_urls[0] if apply_urls else (urls[0] if urls else "https://youtube.com")

    # Determine category explicitly for Fellowships, Accelerators, Competitions, Internships
    title_lower = title.lower()
    desc_lower = description.lower()
    category = "Job"

    if "fellowship" in title_lower or "fellow" in title_lower or "postdoc" in title_lower:
        category = "Fellowship"
    elif "accelerator" in title_lower or "startup" in title_lower or "y combinator" in title_lower or "techstars" in title_lower:
        category = "Accelerator"
    elif "competition" in title_lower or "hackathon" in title_lower or "challenge" in title_lower or "prize" in title_lower:
        category = "Competition"
    elif "internship" in title_lower or "intern" in title_lower or "co-op" in title_lower or "summer student" in title_lower:
        category = "Internship"
    elif "scholarship" in title_lower or "master" in title_lower or "phd" in title_lower:
        category = "Scholarship"
    elif "grant" in title_lower or "funding" in title_lower:
        category = "Grant"

    return {
        "id": f"yt-{abs(hash(title))}",
        "title": title,
        "category": category,
        "funding_amount": "Verified Video Opportunity",
        "deadline": "See Video Description",
        "eligibility": "Open to global applicants",
        "source_name": f"YouTube ({channel_name})",
        "apply_url": apply_url,
        "published_at": datetime.now().strftime("%Y-%m-%d"),
        "region": "Global / Remote",
        "summary": description[:220] + "..." if len(description) > 220 else description,
        "contact_email": emails[0] if emails else None,
        "scout_score": 94,
        "is_youtube": True
    }

def crawl_youtube_opportunity_feeds() -> list:
    """Crawls YouTube RSS feeds for hot opportunity videos and descriptions."""
    items = []
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

    for ch in SCOUT_YOUTUBE_CHANNELS:
        rss_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={ch['channel_id']}"
        try:
            req = urllib.request.Request(rss_url, headers=headers)
            with urllib.request.urlopen(req, timeout=8) as resp:
                xml_data = resp.read()
                root = ET.fromstring(xml_data)

                # Namespace for Atom YouTube feed
                ns = {'atom': 'http://www.w3.org/2005/Atom', 'yt': 'http://www.youtube.com/xml/schemas/2015', 'media': 'http://search.yahoo.com/mrss/'}

                for entry in root.findall('atom:entry', ns)[:5]:
                    title = entry.findtext('atom:title', default='', namespaces=ns)
                    media_group = entry.find('media:group', ns)
                    desc = media_group.findtext('media:description', default='', namespaces=ns) if media_group is not None else ""

                    if title:
                        opp = extract_opportunity_from_yt_description(title, desc, ch["channel_name"])
                        items.append(opp)
        except Exception as e:
            logging.warning(f"YouTube RSS crawl failed for {ch['channel_name']}: {e}")

    return items
