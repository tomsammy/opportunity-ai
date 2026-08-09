import re
import json
import logging
from datetime import datetime

# Ingestion Database for WhatsApp Channel Postings
WHATSAPP_CHANNEL_SEED_OPPORTUNITIES = [
    {
        "id": "wa-001",
        "title": "Content Production & Social Media Manager",
        "organization": "Topsy Travel & Tours and Topsy Living",
        "category": "Job",
        "funding_amount": "Competitive Salary (Hybrid: Mon, Wed, Fri On-Site / Tue, Thu Remote)",
        "deadline": "Rolling (Immediate Hire)",
        "eligibility": "Strong Graphic Design, Video Editing & Social Media Management Skills",
        "source_name": "WhatsApp Channel (Lagos Tech & Hiring Radar)",
        "apply_url": "mailto:gt15recruit@gmail.com",
        "published_at": datetime.now().strftime("%Y-%m-%d"),
        "region": "Lekki, Lagos, Nigeria (Hybrid)",
        "summary": "Topsy Travel & Tours is hiring a creative Content Production & Social Media Manager in Lekki, Lagos. Send CV & Portfolio to gt15recruit@gmail.com.",
        "contact_email": "gt15recruit@gmail.com",
        "scout_score": 95,
        "is_whatsapp": True
    }
]

def parse_whatsapp_message(text: str) -> dict:
    """Parses raw unstructured WhatsApp channel job postings into structured JSON data."""
    lines = [l.strip() for l in text.split('\n') if l.strip()]

    # Extract emails
    emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
    email = emails[0] if emails else "mailto:contact@whatsapp.org"

    # Extract links
    urls = re.findall(r'https?://[^\s<>"]+|www\.[^\s<>"]+', text)
    apply_url = urls[0] if urls else f"mailto:{email}"

    # Extract job title & company
    first_line = lines[0] if lines else "WhatsApp Opportunity"
    clean_title = re.sub(r'[^\w\s-]', '', first_line).strip()
    if not clean_title or len(clean_title) < 5:
        clean_title = "Opportunity from WhatsApp Channel"

    return {
        "id": f"wa-{abs(hash(text[:50]))}",
        "title": clean_title,
        "category": "Job",
        "funding_amount": "Verified WhatsApp Listing",
        "deadline": "See WhatsApp Details",
        "eligibility": "See Channel Details",
        "source_name": "WhatsApp Channel (Scout Intelligence)",
        "apply_url": apply_url,
        "published_at": datetime.now().strftime("%Y-%m-%d"),
        "region": "Global / Remote / Local",
        "summary": text[:240] + "..." if len(text) > 240 else text,
        "contact_email": email,
        "scout_score": 93,
        "is_whatsapp": True
    }

def format_opportunity_for_whatsapp_channel(opportunity: dict) -> str:
    """Formats an Opportunity AI listing into a clean WhatsApp channel broadcast text."""
    title = opportunity.get("title", "Hot Opportunity")
    org = opportunity.get("source_name", "Global Sponsor")
    category = opportunity.get("category", "Opportunity")
    funding = opportunity.get("funding_amount", "Fully Funded")
    deadline = opportunity.get("deadline", "Open")
    apply_url = opportunity.get("apply_url", "https://opportunity-ai-kn1i.onrender.com")
    email = opportunity.get("contact_email", "")

    msg = f"🔻 *NEW {category.upper()} OPPORTUNITY!*\n\n"
    msg += f"📌 *{title}*\n"
    msg += f"🏢 *Source/Sponsor:* {org}\n"
    msg += f"💰 *Funding/Salary:* {funding}\n"
    msg += f"🗓️ *Deadline:* {deadline}\n\n"
    msg += f"📧 *How to Apply:* {email if email else 'Click link below'}\n"
    msg += f"🔗 *Direct Link:* {apply_url}\n\n"
    msg += f"✨ _Discovered by Opportunity AI Engine_"

    return msg
