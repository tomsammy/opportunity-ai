import json
import xml.etree.ElementTree as ET
import urllib.request
import logging
from datetime import datetime
from backend.extractor import extract_metadata_from_content
from backend.scout_engine import fetch_scout_rare_opportunities

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
        "category": "Fellowship",
        "funding_amount": "$75,000 USD Annual Research Grant + Google Cloud Credits",
        "deadline": "November 15, 2026",
        "eligibility": "PhD Candidates & Postdoctoral Researchers in Computer Science/AI",
        "source_name": "Google Research",
        "apply_url": "https://research.google/outreach/phd-fellowship/",
        "published_at": "2026-08-03",
        "region": "Global / Remote",
        "summary": "Direct research funding for promising PhD students undertaking exceptional research in Computer Science, Machine Learning, Robotics, and Natural Language Processing.",
        "content": "The Google PhD Fellowship Program recognizes outstanding graduate students doing exceptional research in computer science and related disciplines."
    },
    {
        "id": "opp-005",
        "title": "Y Combinator W2027 Startup Accelerator Program ($500,000 Funding)",
        "category": "Accelerator",
        "funding_amount": "$500,000 Investment ($125k for 7% + $375k uncapped MFN)",
        "deadline": "October 14, 2026",
        "eligibility": "Early-stage founders worldwide building technology startups",
        "source_name": "Y Combinator",
        "apply_url": "https://www.ycombinator.com/apply",
        "published_at": "2026-08-04",
        "region": "Global / San Francisco",
        "summary": "The premier 3-month startup accelerator providing $500,000 funding, intensive mentorship, and direct access to global venture capital investors.",
        "content": "Y Combinator created a new model for funding early stage startups. Twice a year we invest $500k per company in a large number of startups."
    },
    {
        "id": "opp-006",
        "title": "United Nations Global Youth AI Innovation Challenge 2026",
        "category": "Competition",
        "funding_amount": "$50,000 USD Cash Prize + Mentorship + UN Youth Summit Presentation",
        "deadline": "September 25, 2026",
        "eligibility": "Youth Innovators & Developers Aged 18–35",
        "source_name": "United Nations ITU",
        "apply_url": "https://www.itu.int/en/ITU-D/Youth/Pages/Global-Innovation-Challenge.aspx",
        "published_at": "2026-08-05",
        "region": "Global",
        "summary": "Global competition calling for AI-driven solutions addressing climate change, education, healthcare, and sustainable development goals.",
        "content": "The UN Youth Innovation Challenge invites young developers to build sustainable AI tools solving community challenges."
    },
    {
        "id": "opp-007",
        "title": "World Bank Group Climate Infrastructure Government Procurement Tender 2026",
        "category": "Tender",
        "funding_amount": "$1,200,000 USD Contract Budget",
        "deadline": "December 10, 2026",
        "eligibility": "Registered Engineering, Data Science & CleanTech Firms",
        "source_name": "World Bank Procurement",
        "apply_url": "https://projects.worldbank.org/en/projects-operations/procurement",
        "published_at": "2026-08-05",
        "region": "Global",
        "summary": "International government procurement tender for digital climate monitoring and clean infrastructure consultancy services.",
        "content": "The World Bank invites expression of interest tenders from qualified technology consultancies."
    },
    {
        "id": "opp-008",
        "title": "CERN OpenLab Summer Student Graduate Internship 2027",
        "category": "Internship",
        "funding_amount": "Fully Funded (90 CHF/day Stipend + Travel + Accommodation)",
        "deadline": "January 31, 2027",
        "eligibility": "Bachelor's or Master's students in Computer Science, Math, or Physics",
        "source_name": "CERN Switzerland",
        "apply_url": "https://openlab.cern/education/cern-openlab-summer-student-programme",
        "published_at": "2026-08-06",
        "region": "Switzerland / Europe",
        "summary": "9-week summer research internship at CERN Geneva working on cutting-edge cloud, AI, high-performance computing, and particle physics simulations.",
        "content": "CERN openlab summer students work on advanced computing projects alongside world-leading scientists."
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

def fetch_arbeitnow_jobs() -> list:
    """Fetches live remote tech jobs from Arbeitnow API."""
    items = []
    data = fetch_json_api("https://www.arbeitnow.com/api/job-board-api")
    jobs = data.get("data", [])
    for job in jobs[:15]:
        title = job.get("title", "")
        company = job.get("company_name", "Tech Company")
        salary = "Competitive Compensation"
        apply_url = job.get("url") or "#"
        desc = job.get("description") or ""

        meta = extract_metadata_from_content(f"{title} at {company}", desc, f"Arbeitnow ({company})", "Job")
        meta["id"] = f"arbeitnow-{abs(hash(apply_url))}"
        meta["funding_amount"] = salary
        meta["apply_url"] = apply_url
        meta["published_at"] = datetime.now().strftime("%Y-%m-%d")
        meta["region"] = "Remote / EU / Global"
        items.append(meta)
    return items

def run_crawling_cycle() -> list:
    """Runs a complete multi-source live web crawling cycle."""
    crawled_data = list(INITIAL_SEED_OPPORTUNITIES)
    
    # 0. Fetch Scout Rare & Stealth Opportunities (Direct Founder Roles & Micro-Grants)
    logging.info("Scouting Rare & Stealth Opportunities (Scout Engine)...")
    scout_items = fetch_scout_rare_opportunities()
    crawled_data.extend(scout_items)
    
    # 1. Fetch Live Remote Jobs (Remotive API + Arbeitnow API)
    logging.info("Crawling Remotive & Arbeitnow Job APIs...")
    remotive_items = fetch_remotive_jobs()
    crawled_data.extend(remotive_items)

    arbeitnow_items = fetch_arbeitnow_jobs()
    crawled_data.extend(arbeitnow_items)

    # 2. Fetch Job Marketplaces & Discussion Boards (Hacker News Jobs, Authentic Jobs, WeWorkRemotely)
    logging.info("Crawling Job Marketplaces (Hacker News Jobs, Authentic Jobs, WeWorkRemotely)...")
    job_marketplaces = [
        ("https://hnrss.org/jobs", "Hacker News Jobs"),
        ("https://authenticjobs.com/feed/", "Authentic Jobs"),
        ("https://weworkremotely.com/remote-jobs.rss", "WeWorkRemotely")
    ]
    for url, source in job_marketplaces:
        j_items = fetch_rss_feed(url, source, "Job")
        crawled_data.extend(j_items)

    # 3. Fetch Research Grants & Fellowships (NSF Grants, FundsForNGOs, OpportunityDesk, OFA)
    logging.info("Crawling Research Grants & Fellowships (NSF, FundsForNGOs, OpportunityDesk, OFA)...")
    grant_sources = [
        ("https://www.nsf.gov/rss/rss_www_funding.xml", "US National Science Foundation", "Grant"),
        ("https://www.fundsforngos.org/feed/", "FundsForNGOs", "Grant"),
        ("https://opportunitydesk.org/feed/", "OpportunityDesk", "Grant"),
        ("https://www.opportunitiesforafricans.com/feed/", "Opportunities For Africans", "Scholarship"),
        ("https://scholarships360.org/feed/", "Scholarships360", "Scholarship")
    ]
    for url, source, cat in grant_sources:
        g_items = fetch_rss_feed(url, source, cat)
        crawled_data.extend(g_items)

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

    # 6. Fetch Japa, Visa & Relocation Pathways News (UK Visas, Canada CIC, StudyGreen, Reddit r/IWantOut)
    logging.info("Crawling Japa & Relocation News (UK Visas, Canada CIC, StudyGreen, Reddit r/IWantOut)...")
    japa_sources = [
        ("https://www.gov.uk/government/organisations/uk-visas-and-immigration.atom", "UK Visas & Immigration", "News"),
        ("https://www.cicnews.com/feed", "Canada CIC Immigration News", "News"),
        ("https://studygreen.info/feed/", "StudyGreen (Japa Pathways)", "News"),
        ("https://www.reddit.com/r/IWantOut/.rss", "Reddit r/IWantOut", "News")
    ]
    
    for feed_url, source_name, default_cat in japa_sources:
        japa_items = fetch_rss_feed(feed_url, source_name, default_cat)
        crawled_data.extend(japa_items)

    # Deduplicate items by title
    seen_titles = set()
    unique_items = []
    for item in crawled_data:
        t = item.get("title", "").strip().lower()
        if t and t not in seen_titles:
            seen_titles.add(t)
            unique_items.append(item)

    return unique_items
