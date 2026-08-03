import json
import xml.etree.ElementTree as ET
import urllib.request
import logging
from datetime import datetime
from backend.extractor import extract_metadata_from_content

logging.basicConfig(level=logging.INFO)

# Verified High-Value Seed Data for Instant Display
INITIAL_SEED_OPPORTUNITIES = [
    {
        "id": "opp-001",
        "title": "DAAD Helmut-Schmidt-Programme Master's Scholarships for Public Policy 2026/2027",
        "category": "Scholarship",
        "funding_amount": "100% Fully Funded (€934/month + Travel Allowance + Health Insurance)",
        "deadline": "October 31, 2026",
        "eligibility": "Bachelor's Degree Holders from Developing & Emerging Countries",
        "source_name": "DAAD Germany",
        "apply_url": "https://www me.daad.de/en/study-and-research-in-germany/scholarships/",
        "published_at": "2026-08-01",
        "region": "Germany / Europe",
        "summary": "Fully funded Master's scholarships in Germany for future leaders in public policy, governance, international relations, and public economics.",
        "content": "The DAAD Helmut-Schmidt-Programme (Master's Scholarships for Public Policy and Good Governance) offers future leaders from developing countries the opportunity to acquire a Master's degree in disciplines of special relevance for the social, political, and economic development of their home country."
    },
    {
        "id": "opp-002",
        "title": "Gates Cambridge Fully Funded Postgraduate Scholarships 2027",
        "category": "Scholarship",
        "funding_amount": "100% Fully Funded (£20,000/yr stipend + Full Tuition + Visa Costs)",
        "deadline": "December 03, 2026",
        "eligibility": "Non-UK Citizens applying for full-time postgraduate degree at Cambridge",
        "source_name": "Gates Cambridge Trust",
        "apply_url": "https://www.gatescambridge.org/apply/eligibility/",
        "published_at": "2026-08-02",
        "region": "United Kingdom",
        "summary": "One of the world's most prestigious international scholarships awarded to outstanding applicants outside the UK to pursue a full-time postgraduate degree at the University of Cambridge.",
        "content": "Gates Cambridge Scholarships are highly competitive full-cost awards for postgraduate study in any subject available at the University of Cambridge. Selection criteria include outstanding intellectual capacity, leadership potential, and commitment to improving the lives of others."
    },
    {
        "id": "opp-003",
        "title": "Erasmus Mundus Joint Master Degree (EMJMD) Fully Funded EU Scholarships",
        "category": "Scholarship",
        "funding_amount": "100% Fully Funded (€1,400/month + Full Tuition + Travel)",
        "deadline": "January 15, 2027",
        "eligibility": "Open to all Students Worldwide with a Bachelor's Degree",
        "source_name": "European Commission",
        "apply_url": "https://www.eacea.ec.europa.eu/scholarships/erasmus-mundus-catalogue_en",
        "published_at": "2026-08-02",
        "region": "Europe (Multiple Countries)",
        "summary": "High-level integrated international study programmes funded by the EU across multiple European universities with full financial support.",
        "content": "Erasmus Mundus Joint Masters are high-level integrated study programmes designed and delivered by an international partnership of higher education institutions."
    },
    {
        "id": "opp-004",
        "title": "Google AI & Quantum Research Fellowship 2026",
        "category": "Grant",
        "funding_amount": "$75,000 USD Annual Research Grant + Google Cloud Credits",
        "deadline": "November 15, 2026",
        "eligibility": "PhD Candidates & Postdoctoral Researchers in Computer Science/AI",
        "source_name": "Google Research",
        "apply_url": "https://research.google/outreach/phd-fellowship/",
        "published_at": "2026-08-03",
        "region": "Global / Remote",
        "summary": "Direct research funding for promising PhD students undertaking exceptional research in Computer Science, Machine Learning, Robotics, and Natural Language Processing.",
        "content": "The Google PhD Fellowship Program recognizes outstanding graduate students doing exceptional research in computer science and related disciplines."
    }
]

def fetch_json_api(url: str) -> dict:
    """Helper to fetch JSON endpoints."""
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'OpportunityIQ-Bot/1.0'})
        with urllib.request.urlopen(req, timeout=8) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except Exception as e:
        logging.warning(f"Error fetching JSON API {url}: {e}")
        return {}

def fetch_rss_feed(feed_url: str, source_name: str, category_override: str = None) -> list:
    """Fetches and parses live RSS XML feeds."""
    items = []
    try:
        req = urllib.request.Request(feed_url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        with urllib.request.urlopen(req, timeout=10) as response:
            xml_data = response.read()
            root = ET.fromstring(xml_data)
            
            for item in root.findall('.//item')[:12]:
                title = item.findtext('title') or ""
                link = item.findtext('link') or ""
                description = item.findtext('description') or ""
                pubDate = item.findtext('pubDate') or datetime.now().strftime("%Y-%m-%d")

                meta = extract_metadata_from_content(title, description, source_name, category_override)
                meta["id"] = f"rss-{abs(hash(link))}"
                meta["apply_url"] = link
                meta["published_at"] = pubDate
                meta["region"] = "Global / Remote" if meta["category"] == "Job" else "Global"

                items.append(meta)
    except Exception as e:
        logging.warning(f"Failed to fetch RSS feed {feed_url}: {e}")
    return items

def fetch_remotive_jobs() -> list:
    """Fetches live remote tech jobs from Remotive API."""
    items = []
    data = fetch_json_api("https://remotive.com/api/remote-jobs?limit=15")
    jobs = data.get("jobs", [])
    for job in jobs[:12]:
        title = job.get("title", "")
        company = job.get("company_name", "Remote Company")
        category = "Job"
        salary = job.get("salary") or "Competitive Compensation"
        apply_url = job.get("url") or "#"
        desc = job.get("description") or ""

        meta = extract_metadata_from_content(f"{title} at {company}", desc, f"Remotive ({company})", "Job")
        meta["id"] = f"remotive-{job.get('id')}"
        meta["funding_amount"] = salary
        meta["apply_url"] = apply_url
        meta["published_at"] = job.get("publication_date", "")[:10]
        meta["region"] = job.get("candidate_required_location") or "Worldwide Remote"
        items.append(meta)
    return items

def run_crawling_cycle() -> list:
    """Runs a complete multi-source live web crawling cycle."""
    crawled_data = list(INITIAL_SEED_OPPORTUNITIES)
    
    # 1. Fetch Live Remote Jobs (Remotive API)
    logging.info("Crawling Remotive Jobs API...")
    remotive_items = fetch_remotive_jobs()
    crawled_data.extend(remotive_items)

    # 2. Fetch Live International Scholarships & Grants RSS
    logging.info("Crawling Opportunities For Africans & International Scholarships Feed...")
    ofa_items = fetch_rss_feed("https://www.opportunitiesforafricans.com/feed/", "Opportunities For Africans", "Scholarship")
    crawled_data.extend(ofa_items)

    # 3. Fetch WeWorkRemotely RSS
    logging.info("Crawling WeWorkRemotely Feed...")
    wwr_items = fetch_rss_feed("https://weworkremotely.com/remote-jobs.rss", "WeWorkRemotely", "Job")
    crawled_data.extend(wwr_items)

    # 4. Fetch Global Credible News Feeds (BBC, NYTimes, Wired, MIT Tech Review, Guardian, TechCrunch)
    logging.info("Crawling Credible Global News Feeds...")
    
    news_sources = [
        ("https://feeds.bbci.co.uk/news/world/rss.xml", "BBC World News"),
        ("https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml", "The New York Times"),
        ("https://www.wired.com/feed/rss", "Wired Magazine"),
        ("https://www.technologyreview.com/feed/", "MIT Tech Review"),
        ("https://www.theguardian.com/technology/rss", "The Guardian"),
        ("https://techcrunch.com/feed/", "TechCrunch")
    ]
    
    for feed_url, source_name in news_sources:
        news_items = fetch_rss_feed(feed_url, source_name, "News")
        crawled_data.extend(news_items)

    # 5. Fetch Hot Discussion Platforms & Substack Newsletters (Reddit, Substack)
    logging.info("Crawling Substack Newsletters & Hot Reddit Discussions...")
    hot_sources = [
        ("https://importai.substack.com/feed", "Substack (Import AI)", "News"),
        ("https://blog.pragmaticengineer.com/rss/", "Substack (Pragmatic Engineer)", "Job"),
        ("https://www.reddit.com/r/scholarships/.rss", "Reddit r/scholarships", "Scholarship"),
        ("https://www.reddit.com/r/remotejobs/.rss", "Reddit r/remotejobs", "Job"),
        ("https://www.reddit.com/r/fellowships/.rss", "Reddit r/fellowships", "Grant"),
        ("https://www.reddit.com/r/artificial/.rss", "Reddit r/artificial", "News")
    ]
    
    for feed_url, source_name, default_cat in hot_sources:
        hot_items = fetch_rss_feed(feed_url, source_name, default_cat)
        crawled_data.extend(hot_items)

    # Deduplicate items by title
    seen_titles = set()
    unique_items = []
    for item in crawled_data:
        t = item.get("title", "").strip().lower()
        if t and t not in seen_titles:
            seen_titles.add(t)
            unique_items.append(item)

    return unique_items
