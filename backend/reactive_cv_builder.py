import json
import logging
from datetime import datetime
from backend.job_evaluator import get_user_profile

TEMPLATES = {
    "tech": "💼 Software & Tech Engineer CV (ATS Optimized)",
    "academic": "🎓 Academic & Scholarship CV (Research & Publications)",
    "fellowship": "🔬 Research & Fellowship CV (Grants & Lab Experience)",
    "founder": "🚀 Startup Founder & Accelerator Bio CV (Traction & Metrics)"
}

def generate_reactive_resume_json(profile: dict, template_type: str = "tech") -> dict:
    """Generates standard Reactive Resume compatible JSON schema structure."""
    name = profile.get("name", "John Doe")
    skills = profile.get("skills", ["Python", "JavaScript", "SQL"])
    roles = profile.get("target_roles", ["Software Engineer"])
    edu = profile.get("education", "B.Sc Computer Science")
    exp = profile.get("experience_summary", "Experienced software developer building web applications.")

    return {
        "basics": {
            "name": name,
            "headline": roles[0] if roles else "Professional Candidate",
            "email": "candidate@example.com",
            "phone": "+1 (555) 019-2834",
            "location": "Global / Remote",
            "summary": exp
        },
        "skills": [{"name": s, "level": "Advanced"} for s in skills],
        "education": [{
            "institution": edu,
            "area": "Computer Science / Higher Education",
            "studyType": "Bachelor / Postgraduate",
            "startDate": "2020-09-01",
            "endDate": "2024-06-01"
        }],
        "work": [{
            "company": "Tech Solutions Inc.",
            "position": roles[0] if roles else "Developer",
            "startDate": "2024-06-01",
            "endDate": "Present",
            "summary": f"Built scalable data pipelines and software tools utilizing {', '.join(skills[:3])}."
        }],
        "meta": {
            "template": template_type,
            "version": "4.0.0",
            "generator": "Opportunity AI x Reactive Resume Engine"
        }
    }

def render_cv_template_html(profile: dict, target_opportunity: dict = None, template_type: str = "tech") -> str:
    """Renders a beautiful ATS-optimized HTML/CSS printable resume matching Reactive Resume styling."""
    name = profile.get("name", "John Doe")
    skills = profile.get("skills", ["Python", "JavaScript", "React", "FastAPI", "SQL"])
    roles = profile.get("target_roles", ["Software Engineer"])
    edu = profile.get("education", "B.Sc Computer Science")
    exp = profile.get("experience_summary", "Dedicated software professional with a strong track record.")

    target_title = target_opportunity.get("title") if target_opportunity else "Target Opportunity"
    target_org = target_opportunity.get("source_name") if target_opportunity else "Global Organization"

    if template_type == "academic":
        accent_color = "#6d28d9" # Deep Purple for Academic
        header_tag = "ACADEMIC & SCHOLARSHIP CURRICULUM VITAE"
    elif template_type == "fellowship":
        accent_color = "#0284c7" # Sky Blue for Fellowship
        header_tag = "FELLOWSHIP & RESEARCH RESUME"
    elif template_type == "founder":
        accent_color = "#d97706" # Amber for Founder
        header_tag = "STARTUP FOUNDER & EXECUTIVE PROFILE"
    else:
        accent_color = "#2563eb" # Royal Blue for Tech
        header_tag = "PROFESSIONAL ATS SOFTWARE RESUME"

    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>{name} - {header_tag}</title>
<style>
    body {{ font-family: 'Inter', Helvetica, Arial, sans-serif; color: #1e293b; margin: 0; padding: 40px; background: #fff; line-height: 1.5; }}
    .header {{ border-bottom: 2px solid {accent_color}; padding-bottom: 16px; margin-bottom: 24px; }}
    .name {{ font-size: 28px; font-weight: 800; color: #0f172a; margin: 0; text-transform: uppercase; letter-spacing: 0.5px; }}
    .tagline {{ font-size: 14px; font-weight: 600; color: {accent_color}; margin-top: 4px; text-transform: uppercase; }}
    .contact {{ font-size: 12px; color: #64748b; margin-top: 8px; }}
    .section-title {{ font-size: 14px; font-weight: 700; color: {accent_color}; text-transform: uppercase; letter-spacing: 1px; margin-top: 24px; margin-bottom: 10px; border-bottom: 1px solid #e2e8f0; padding-bottom: 4px; }}
    .summary {{ font-size: 13px; color: #334155; text-align: justify; }}
    .skills-grid {{ display: flex; flex-wrap: wrap; gap: 6px; margin-top: 8px; }}
    .skill-badge {{ background: #f1f5f9; color: #0f172a; padding: 4px 10px; border-radius: 4px; font-size: 12px; font-weight: 600; border: 1px solid #cbd5e1; }}
    .item {{ margin-bottom: 16px; }}
    .item-header {{ display: flex; justify-content: space-between; font-size: 13px; font-weight: 700; color: #0f172a; }}
    .item-sub {{ font-size: 12px; color: #64748b; font-style: italic; margin-bottom: 6px; }}
    .bullet {{ font-size: 12px; color: #334155; margin-left: 16px; margin-bottom: 4px; }}
</style>
</head>
<body>
    <div class="header">
        <h1 class="name">{name}</h1>
        <div class="tagline">{roles[0] if roles else 'Candidate Profile'} • Tailored for {target_org}</div>
        <div class="contact">📍 Location: Remote / Global | ✉️ candidate@example.com | 🔗 Reactive Resume Format</div>
    </div>

    <div class="section-title">Objective & Target Alignment</div>
    <div class="summary">
        Highly qualified candidate applying for <strong>{target_title}</strong> at <strong>{target_org}</strong>. {exp} Demonstrated expertise in {', '.join(skills[:4])}.
    </div>

    <div class="section-title">Core Technical & Domain Skills</div>
    <div class="skills-grid">
        {"".join([f'<span class="skill-badge">{s}</span>' for s in skills])}
    </div>

    <div class="section-title">Education & Academic Achievements</div>
    <div class="item">
        <div class="item-header">
            <span>{edu}</span>
            <span>Graduated</span>
        </div>
        <div class="item-sub">Specialization in Software & Quantitative Systems</div>
        <div class="bullet">• Relevant coursework and project research in software engineering and data analysis.</div>
    </div>

    <div class="section-title">Key Work Experience & Major Projects</div>
    <div class="item">
        <div class="item-header">
            <span>Lead Developer / Researcher</span>
            <span>2024 - Present</span>
        </div>
        <div class="item-sub">Targeted Role for {target_title}</div>
        <div class="bullet">• Architected high-performance systems using {', '.join(skills[:3])}.</div>
        <div class="bullet">• Optimized workflows achieving 40% performance gains and streamlined data ingestion.</div>
        <div class="bullet">• Designed modular software solutions tailored for {target_org} specifications.</div>
    </div>

    <div style="margin-top: 40px; font-size: 10px; color: #94a3b8; text-align: center; border-top: 1px solid #f1f5f9; padding-top: 12px;">
        Generated by Opportunity AI x Reactive Resume Engine • {datetime.now().strftime("%B %Y")}
    </div>
</body>
</html>"""
    return html
