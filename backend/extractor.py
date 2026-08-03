import re
from datetime import datetime, timedelta

def clean_text(text: str) -> str:
    """Removes HTML tags, extra whitespace, and noisy characters."""
    if not text:
        return ""
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def extract_metadata_from_content(title: str, content: str, source_name: str, category_override: str = None) -> dict:
    """
    Extracts structured schema fields from raw opportunity content.
    """
    clean_desc = clean_text(content)
    lower_text = (title + " " + clean_desc).lower()

    # Determine Category
    if category_override:
        category = category_override
    elif any(k in lower_text for k in ["scholarship", "fellowship", "bursary", "grant", "tuition", "phd", "master"]):
        category = "Scholarship"
    elif any(k in lower_text for k in ["job", "hiring", "engineer", "developer", "designer", "remote", "salary", "analyst"]):
        category = "Job"
    else:
        category = "News"

    # If category is News, set clean news-specific defaults
    if category == "News":
        funding_amount = "Editorial / News Article"
        deadline = "N/A"
        eligibility = "General Public / Readers"
    else:
        # Extract Funding or Salary for Jobs & Scholarships
        funding_amount = "Full Funding / Market Rate"
        funding_match = re.search(r'(\$|€|£)\s?\d+[\d,]*(\s?-\s?(\$|€|£)?\s?\d+[\d,]*)?(\/year|\/month|\/yr|\/mo)?', clean_desc, re.IGNORECASE)
        if funding_match:
            funding_amount = funding_match.group(0)
        elif "fully funded" in lower_text or "full tuition" in lower_text:
            funding_amount = "100% Fully Funded (Tuition + Monthly Stipend)"
        elif "competitive salary" in lower_text:
            funding_amount = "Competitive Salary + Benefits"

        # Extract Deadline
        deadline = "Open / Rolling Application"
        deadline_match = re.search(r'(deadline|apply by|closing date):\s?([A-Za-z]+\s+\d{1,2},\s+\d{4}|\d{4}-\d{2}-\d{2})', clean_desc, re.IGNORECASE)
        if deadline_match:
            deadline = deadline_match.group(2)
        else:
            # Default projected deadline 60 days from now for active listings
            future_date = datetime.now() + timedelta(days=60)
            deadline = future_date.strftime("%B %d, %Y")

        # Extract Eligibility
        eligibility = "Open to International Applicants"
        if "undergraduate" in lower_text:
            eligibility = "Undergraduate Students & Fresh High School Graduates"
        elif "master" in lower_text or "postgraduate" in lower_text:
            eligibility = "Bachelor's Degree Holders / Master Applicants"
        elif "phd" in lower_text or "doctoral" in lower_text or "research" in lower_text:
            eligibility = "Master's Degree Holders / Doctoral Researchers"
        elif "years of experience" in lower_text or "senior" in lower_text:
            eligibility = "3+ Years Professional Experience"

    return {
        "title": clean_text(title),
        "category": category,
        "funding_amount": funding_amount,
        "deadline": deadline,
        "eligibility": eligibility,
        "source_name": source_name,
        "summary": clean_desc[:350] + "..." if len(clean_desc) > 350 else clean_desc,
        "content": clean_desc
    }
