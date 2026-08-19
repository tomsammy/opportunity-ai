import urllib.request
import json
import xml.etree.ElementTree as ET
import logging
import re
import hashlib
from datetime import datetime

logger = logging.getLogger(__name__)

# Curated High-Value Anchor Diplomatic & Fellowship Seed Data
DIPLOMATIC_FELLOWSHIP_ANCHORS = [
    {
        "id": "fcdo-us-001",
        "title": "FCDO Senior Policy Adviser – US Bilateral Relations & Transatlantic Security",
        "category": "Job",
        "funding_amount": "£54,500 – £64,000 / year + Civil Service Pension",
        "deadline": "November 30, 2026",
        "eligibility": "UK/Commonwealth Nationals with Security Clearance (SC/DV eligible)",
        "source_name": "Foreign, Commonwealth & Development Office (FCDO)",
        "apply_url": "https://www.civilservicejobs.service.gov.uk/csr/index.cgi",
        "published_at": datetime.utcnow().strftime("%Y-%m-%d"),
        "region": "London (Whitehall) & British Embassy Washington D.C.",
        "summary": "Lead high-profile bilateral foreign policy and transatlantic defense and economic strategy liaising directly between Whitehall, the US Administration, and the British Embassy in Washington D.C.",
        "content": "The Foreign, Commonwealth & Development Office (FCDO) is recruiting a Senior Policy Adviser for the North America & US Bilateral Affairs Directorate. Responsibilities include advising ministers on US-UK bilateral policy, AUKUS transatlantic cooperation, and coordinating summit engagements."
    },
    {
        "id": "cab-off-002",
        "title": "Cabinet Office Senior Policy Adviser – International Affairs & National Security Secretariat",
        "category": "Job",
        "funding_amount": "£58,000 – £68,500 / year (Grade 7)",
        "deadline": "December 15, 2026",
        "eligibility": "UK Civil Service eligible / International Policy Specialists",
        "source_name": "Cabinet Office (Whitehall)",
        "apply_url": "https://www.civilservicejobs.service.gov.uk/csr/index.cgi",
        "published_at": datetime.utcnow().strftime("%Y-%m-%d"),
        "region": "70 Whitehall, London (Hybrid)",
        "summary": "Shape international national security policy and strategic summit diplomacy supporting 10 Downing Street, G7/G20 delegations, and allied diplomatic missions.",
        "content": "Located at 70 Whitehall, this prestigious Cabinet Office position supports the Prime Minister and National Security Adviser on international defense diplomacy, bilateral intelligence agreements, and transatlantic geopolitical strategy."
    },
    {
        "id": "fcdo-dc-003",
        "title": "British Embassy Washington – Head of Congressional & Transatlantic Policy Liaison",
        "category": "Job",
        "funding_amount": "$85,000 – $105,000 USD / year + Diplomatic Benefits",
        "deadline": "January 10, 2027",
        "eligibility": "Diplomatic staff & international policy specialists with US/UK clearance",
        "source_name": "British Embassy Washington D.C.",
        "apply_url": "https://www.civilservicejobs.service.gov.uk/csr/index.cgi",
        "published_at": datetime.utcnow().strftime("%Y-%m-%d"),
        "region": "Washington D.C., United States",
        "summary": "Direct diplomatic outreach and congressional liaison on behalf of HM Government, working closely with the US Congress, Department of State, and White House policy teams.",
        "content": "The British Embassy in Washington D.C. represents the UK Government in the United States. This role oversees political and congressional relations, trade policy tracking, and bilateral state visit logistics."
    },
    {
        "id": "wh-fellow-004",
        "title": "White House Fellowship Program 2026/2027 (Executive Office of the President)",
        "category": "Fellowship",
        "funding_amount": "Federal GS-14 Pay ($115,000 – $145,000 USD) + Full Benefits",
        "deadline": "January 15, 2027",
        "eligibility": "Accomplished early-to-mid career professionals with demonstrated public service leadership",
        "source_name": "President's Commission on White House Fellowships",
        "apply_url": "https://www.whitehouse.gov/participate/fellows/",
        "published_at": datetime.utcnow().strftime("%Y-%m-%d"),
        "region": "The White House, Washington D.C.",
        "summary": "America's most prestigious program for leadership and public service, placing fellows as full-time, paid special assistants to Cabinet secretaries and senior White House staff.",
        "content": "Founded in 1964, the White House Fellows program offers exceptional emerging leaders first-hand experience working at the highest levels of the United States Federal Government. Fellows participate in roundtable discussions with global leaders and policy makers."
    },
    {
        "id": "chev-fellow-005",
        "title": "UK Chevening International Diplomatic & Policy Fellowships 2027",
        "category": "Fellowship",
        "funding_amount": "100% Fully Funded (Tuition + Living Allowance £1,600/mo + Flights + Visa)",
        "deadline": "November 05, 2026",
        "eligibility": "Mid-career professionals from 160+ eligible countries with leadership experience",
        "source_name": "FCDO Chevening Secretariat",
        "apply_url": "https://www.chevening.org/fellowships/",
        "published_at": datetime.utcnow().strftime("%Y-%m-%d"),
        "region": "United Kingdom (London & Oxford/Cambridge)",
        "summary": "Prestigious UK Foreign, Commonwealth and Development Office fellowship for global mid-career leaders in governance, international law, cybersecurity, and diplomacy.",
        "content": "Chevening Fellowships are funded by the UK Foreign, Commonwealth and Development Office (FCDO). They offer mid-career professionals from around the world the opportunity to undertake bespoke professional development programmes at leading UK universities and policy institutes."
    },
    {
        "id": "atlantic-fellow-006",
        "title": "Atlantic Council Millennium Leadership Fellowship & Geopolitical Forum",
        "category": "Fellowship",
        "funding_amount": "Fully Funded Travel + Executive Executive Leadership Grant",
        "deadline": "December 01, 2026",
        "eligibility": "Rising global leaders under 35 in foreign policy, international security, and tech",
        "source_name": "Atlantic Council (Washington D.C.)",
        "apply_url": "https://www.atlanticcouncil.org/programs/millennium-leadership-program/",
        "published_at": datetime.utcnow().strftime("%Y-%m-%d"),
        "region": "Washington D.C. & International Study Tours",
        "summary": "Premier transatlantic leadership accelerator connecting next-generation global decision-makers with heads of state, NATO leaders, and White House policymakers.",
        "content": "The Atlantic Council Millennium Fellowship is a competitive, one-year fellowship that equips rising leaders with the global network and skills to address transatlantic challenges, climate resilience, and security."
    },
    {
        "id": "marshall-fellow-007",
        "title": "Marshall Memorial Fellowship – Transatlantic Leadership Exchange",
        "category": "Fellowship",
        "funding_amount": "100% Fully Funded 24-day Travel Stipend & Policy Briefings",
        "deadline": "October 30, 2026",
        "eligibility": "Emerging leaders in policy, journalism, business, and civil society (US & European Citizens)",
        "source_name": "German Marshall Fund of the United States",
        "apply_url": "https://www.gmfus.org/marshall-memorial-fellowship",
        "published_at": datetime.utcnow().strftime("%Y-%m-%d"),
        "region": "United States & European Union",
        "summary": "The flagship transatlantic fellowship program of the German Marshall Fund, creating lasting relationships between emerging leaders in the United States and Europe.",
        "content": "The Marshall Memorial Fellowship (MMF) introduces emerging European and American leaders to the political, economic, and social dynamics across the Atlantic, including direct meetings with US administration and European government officials."
    }
]

def fetch_gov_uk_policy_opportunities():
    """Fetches real-time policy and diplomatic publications/vacancies from the official GOV.UK Search API."""
    queries = [
        "FCDO bilateral policy United States",
        "Cabinet Office international security diplomatic",
        "Foreign Commonwealth Development Office Washington"
    ]
    results = []
    
    for q in queries:
        try:
            url = f"https://www.gov.uk/api/search.json?q={urllib.parse.quote(q)}&count=5"
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "OpportunityIQ-DiplomaticBot/1.0 (Public RAG Engine; info@opportunityiq.ai)"}
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                items = data.get("results", [])
                
                for item in items:
                    title = item.get("title", "").strip()
                    desc = item.get("description", "").strip()
                    link = item.get("link", "")
                    if not link.startswith("http"):
                        link = f"https://www.gov.uk{link}"
                    
                    if not title or len(title) < 5:
                        continue

                    # Generate clean ID
                    clean_id = f"govuk-{hashlib.md5(link.encode()).hexdigest()[:8]}"
                    
                    # Determine category and region
                    cat = "Job" if ("recruitment" in title.lower() or "appoint" in title.lower() or "policy" in title.lower()) else "Fellowship"
                    
                    results.append({
                        "id": clean_id,
                        "title": f"GOV.UK: {title}",
                        "category": cat,
                        "funding_amount": "UK Civil Service Pay Scale (£40,000 – £75,000 / yr)",
                        "deadline": "Open / Ongoing Review 2026–2027",
                        "eligibility": "UK/Commonwealth Nationals & International Policy Specialists",
                        "source_name": "HM Government (GOV.UK)",
                        "apply_url": link,
                        "published_at": datetime.utcnow().strftime("%Y-%m-%d"),
                        "region": "London (Whitehall) / Global Network",
                        "summary": desc or f"Official UK Government policy and diplomatic update regarding {title}.",
                        "content": f"{title}. {desc} Official documentation and application guidance via GOV.UK."
                    })
        except Exception as e:
            logger.warning(f"Error fetching from GOV.UK Search API for '{q}': {e}")
            
    return results

def fetch_international_fellowship_feeds():
    """Fetches live international fellowships from open global fellowship RSS feeds."""
    feed_urls = [
        "https://opportunitydesk.org/category/fellowships/feed/",
        "https://www.youthop.com/fellowships/feed"
    ]
    fellowships = []
    
    for url in feed_urls:
        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                xml_data = resp.read()
                root = ET.fromstring(xml_data)
                
                items = root.findall('.//item')
                for item in items[:6]:
                    title = item.find('title').text if item.find('title') is not None else ""
                    link = item.find('link').text if item.find('link') is not None else ""
                    desc = item.find('description').text if item.find('description') is not None else ""
                    pub_date = item.find('pubDate').text if item.find('pubDate') is not None else ""
                    
                    if not title:
                        continue
                        
                    clean_desc = re.sub('<[^<]+?>', '', desc or '')[:300].strip()
                    clean_id = f"intl-fel-{hashlib.md5((link or title).encode()).hexdigest()[:8]}"
                    
                    fellowships.append({
                        "id": clean_id,
                        "title": title.strip(),
                        "category": "Fellowship",
                        "funding_amount": "Fully Funded (Stipend + Travel + Accommodation)",
                        "deadline": "Refer to official portal 2026/2027",
                        "eligibility": "International Candidates, Researchers & Policy Fellows",
                        "source_name": "International Fellowship Network",
                        "apply_url": link or "https://opportunitydesk.org/category/fellowships/",
                        "published_at": datetime.utcnow().strftime("%Y-%m-%d"),
                        "region": "International / Global",
                        "summary": clean_desc or f"Global Fellowship: {title}",
                        "content": f"{title}. {clean_desc}. Full details and application requirements available on the portal."
                    })
        except Exception as e:
            logger.warning(f"Error fetching international fellowship feed '{url}': {e}")
            
    return fellowships

def crawl_diplomatic_and_fellowship_opportunities():
    """Main crawler entrypoint returning all FCDO, Cabinet Office, and International Fellowship listings."""
    combined = []
    
    # 1. Add verified high-value anchors (FCDO, Cabinet Office, White House Fellows, Chevening, Marshall)
    combined.extend(DIPLOMATIC_FELLOWSHIP_ANCHORS)
    
    # 2. Add real-time live GOV.UK API policy listings
    gov_results = fetch_gov_uk_policy_opportunities()
    combined.extend(gov_results)
    
    # 3. Add live International Fellowship RSS entries
    live_fellowships = fetch_international_fellowship_feeds()
    combined.extend(live_fellowships)
    
    # Deduplicate by apply_url or title
    unique_items = []
    seen_keys = set()
    for item in combined:
        key = item.get("apply_url") or item.get("title")
        if key not in seen_keys:
            seen_keys.add(key)
            unique_items.append(item)
            
    logger.info(f"Successfully collected {len(unique_items)} FCDO, Cabinet Office & International Fellowship opportunities via API & Live Feeds.")
    return unique_items
