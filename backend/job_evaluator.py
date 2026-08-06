import os
import json

# Default candidate profile
DEFAULT_USER_PROFILE = {
    "name": "Candidate",
    "target_roles": ["Software Engineer", "Full Stack Developer", "Data Analyst", "AI Engineer"],
    "skills": ["Python", "JavaScript", "FastAPI", "React", "SQL", "Git", "Machine Learning", "REST APIs"],
    "experience_summary": "Experienced developer with a strong foundation in building web applications, software tools, and data-driven systems.",
    "education": "Bachelor's Degree in Computer Science / Engineering",
    "preferred_locations": ["Remote", "Europe", "Canada", "UK"]
}

user_profile_store = dict(DEFAULT_USER_PROFILE)

def get_user_profile() -> dict:
    return user_profile_store

def update_user_profile(new_data: dict) -> dict:
    global user_profile_store
    if "skills" in new_data and isinstance(new_data["skills"], str):
        new_data["skills"] = [s.strip() for s in new_data["skills"].split(",") if s.strip()]
    if "target_roles" in new_data and isinstance(new_data["target_roles"], str):
        new_data["target_roles"] = [r.strip() for r in new_data["target_roles"].split(",") if r.strip()]
    user_profile_store.update(new_data)
    return user_profile_store

def evaluate_job_fit(opportunity_item: dict, candidate_profile: dict = None) -> dict:
    """Evaluates candidate fit score (0-100%) against a job/scholarship posting."""
    if not candidate_profile:
        candidate_profile = user_profile_store

    title = opportunity_item.get("title", "")
    summary = opportunity_item.get("summary", "")
    eligibility = opportunity_item.get("eligibility", "")
    content = opportunity_item.get("content", "")
    full_text = f"{title} {summary} {eligibility} {content}".lower()

    skills = candidate_profile.get("skills", [])
    matched_skills = [s for s in skills if s.lower() in full_text]
    skill_score = (len(matched_skills) / max(len(skills), 1)) * 50

    target_roles = candidate_profile.get("target_roles", [])
    matched_roles = [r for r in target_roles if any(word in full_text for word in r.lower().split())]
    role_score = 30 if matched_roles else 15

    base_score = 20
    total_score = min(int(skill_score + role_score + base_score), 98)

    pros = []
    cons = []

    if matched_skills:
        pros.append(f"Strong skill alignment in: {', '.join(matched_skills[:4])}")
    else:
        pros.append("General alignment with candidate's core technical profile")

    if matched_roles:
        pros.append(f"Matches target focus area: {matched_roles[0]}")

    missing_skills = [s for s in skills if s not in matched_skills]
    if missing_skills:
        cons.append(f"Posting does not explicitly mention: {', '.join(missing_skills[:3])}")
    else:
        cons.append("Requires verifying specific seniority/experience level details")

    recommendation = "HIGHLY RECOMMENDED: Great overall match for your background!" if total_score >= 70 else \
                     "GOOD MATCH: Worth applying with a tailored cover letter." if total_score >= 50 else \
                     "MODERATE FIT: Review requirements before submitting."

    return {
        "fit_score": total_score,
        "matched_skills": matched_skills,
        "pros": pros,
        "cons": cons,
        "recommendation": recommendation,
        "item_id": opportunity_item.get("id")
    }

def generate_cover_letter(opportunity_item: dict, candidate_profile: dict = None) -> str:
    """Generates a tailored professional cover letter draft for the opportunity."""
    if not candidate_profile:
        candidate_profile = user_profile_store

    title = opportunity_item.get("title", "")
    source = opportunity_item.get("source_name", "the organization")
    category = opportunity_item.get("category", "Opportunity")
    skills_str = ", ".join(candidate_profile.get("skills", [])[:5])
    name = candidate_profile.get("name", "Candidate")
    exp = candidate_profile.get("experience_summary", "")
    edu = candidate_profile.get("education", "")

    if category.lower() in ["scholarship", "grant"]:
        letter = f"""Dear Selection Committee for {title},

I am writing to express my strong enthusiasm for applying to the {title} as advertised via {source}. With my background in {edu} and hands-on experience in {skills_str}, I am deeply committed to advancing my research and professional goals in this field.

{exp}

My foundation in {skills_str} equips me with the technical rigor and analytical mindset required to excel in this program. I am particularly drawn to this opportunity because it offers an exceptional framework to expand my impact.

Thank you for your time and consideration of my application. I look forward to the possibility of contributing to your academic and professional community.

Sincerely,
{name}"""
    else:
        letter = f"""Dear Hiring Team at {source},

I am excited to submit my application for the position of {title}. Having reviewed the requirements, I believe my background in {skills_str} and proven experience building software applications make me a strong fit for this role.

{exp}

Key highlights I bring to your team include:
• Core Technical Skills: {skills_str}
• Educational Background: {edu}
• Proven track record delivering reliable solutions, writing clean code, and working effectively in remote/distributed team environments.

I would welcome the opportunity to discuss how my technical qualifications align with your current goals. Thank you for your time and consideration.

Sincerely,
{name}"""

    return letter
