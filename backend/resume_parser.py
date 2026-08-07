import re
import json

COMMON_SKILLS_KEYWORDS = [
    "Python", "JavaScript", "TypeScript", "React", "Node.js", "Express", "FastAPI", "Django", "Flask",
    "SQL", "PostgreSQL", "MongoDB", "Redis", "Git", "GitHub", "Docker", "Kubernetes", "AWS", "GCP", "Azure",
    "Machine Learning", "Deep Learning", "Data Analysis", "Pandas", "NumPy", "Scikit-Learn", "PyTorch", "TensorFlow",
    "HTML", "CSS", "Tailwind", "REST APIs", "GraphQL", "CI/CD", "Linux", "Cybersecurity", "Java", "C++", "C#", "Go", "Rust",
    "Project Management", "Agile", "Scrum", "UI/UX", "Figma", "Excel", "Power BI", "Tableau", "Public Speaking"
]

COMMON_ROLES_KEYWORDS = [
    "Software Engineer", "Full Stack Developer", "Backend Developer", "Frontend Developer", "Data Scientist",
    "Data Analyst", "AI Engineer", "Machine Learning Engineer", "DevOps Engineer", "Cloud Architect",
    "Product Manager", "Project Manager", "UI/UX Designer", "Cybersecurity Analyst", "Research Assistant"
]

def parse_resume_text(text: str) -> dict:
    """Parses raw text extracted from a CV/Resume to extract skills, education, target roles, and summary."""
    if not text:
        return {}

    text_lower = text.lower()

    # 1. Extract Skills
    extracted_skills = []
    for skill in COMMON_SKILLS_KEYWORDS:
        pattern = r'\b' + re.escape(skill.lower()) + r'\b'
        if re.search(pattern, text_lower):
            extracted_skills.append(skill)

    # 2. Extract Target Roles
    extracted_roles = []
    for role in COMMON_ROLES_KEYWORDS:
        pattern = r'\b' + re.escape(role.lower()) + r'\b'
        if re.search(pattern, text_lower):
            extracted_roles.append(role)
    if not extracted_roles:
        extracted_roles = ["Software Engineer", "Data Analyst"]

    # 3. Extract Education
    education = "Bachelor's Degree"
    if "phd" in text_lower or "doctorate" in text_lower:
        education = "Ph.D. / Doctorate"
    elif "master" in text_lower or "m.sc" in text_lower or "mba" in text_lower:
        education = "Master's Degree (M.Sc / MBA)"
    elif "bachelor" in text_lower or "b.sc" in text_lower or "b.a" in text_lower:
        education = "Bachelor's Degree (B.Sc / B.A)"
    elif "diploma" in text_lower or "associate" in text_lower:
        education = "Diploma / Associate Degree"

    # 4. Extract Name Candidate
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    candidate_name = lines[0] if lines else "Candidate"
    if len(candidate_name) > 40 or "@" in candidate_name:
        candidate_name = "Candidate"

    # 5. Extract Experience Summary
    summary = text[:350].replace('\n', ' ').strip()

    return {
        "name": candidate_name,
        "skills": extracted_skills if extracted_skills else ["Python", "JavaScript", "SQL", "Git"],
        "target_roles": extracted_roles,
        "education": education,
        "experience_summary": summary
    }
