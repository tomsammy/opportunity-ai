import os
import json
import logging
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional, List

from backend.config import DB_PATH, BASE_DIR
from backend.scraper_engine import run_crawling_cycle
from backend.rag_service import RAGService

app = FastAPI(
    title="Opportunity & News AI Platform API",
    description="High-value web intelligence crawler and RAG query engine",
    version="1.0.0"
)

# Enable CORS for cross-origin frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

rag_engine = RAGService()
opportunities_cache = []

def load_data():
    global opportunities_cache
    if os.path.exists(DB_PATH):
        try:
            with open(DB_PATH, "r", encoding="utf-8") as f:
                opportunities_cache = json.load(f)
        except Exception as e:
            logging.error(f"Error loading DB: {e}")
            opportunities_cache = []

    # Completely purge any WhatsApp items
    opportunities_cache = [item for item in opportunities_cache if not is_whatsapp_item(item)]
    save_data()

    rag_engine.index_documents(opportunities_cache)

def is_whatsapp_item(item: dict) -> bool:
    """Helper to completely filter out any WhatsApp channel or text item."""
    title = str(item.get("title", "")).lower()
    source = str(item.get("source_name", "")).lower()
    item_id = str(item.get("id", "")).lower()
    return "whatsapp" in title or "whatsapp" in source or item_id.startswith("wa-") or item_id.startswith("wac-") or bool(item.get("is_whatsapp")) or bool(item.get("is_whatsapp_channel"))

def save_data():
    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump(opportunities_cache, f, indent=2)

@app.on_event("startup")
def startup_event():
    load_data()

@app.get("/api/opportunities")
def get_opportunities(
    category: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = 20
):
    """Retrieves filtered list of high-value opportunities."""
    data = [item for item in opportunities_cache if not is_whatsapp_item(item)]

    if category and category.lower() != "all":
        data = [item for item in data if item.get("category", "").lower() == category.lower()]

    if search:
        search_lower = search.lower()
        data = [
            item for item in data
            if search_lower in item.get("title", "").lower()
            or search_lower in item.get("summary", "").lower()
            or search_lower in item.get("eligibility", "").lower()
            or search_lower in item.get("source_name", "").lower()
        ]

    return {
        "status": "success",
        "total": len(data),
        "data": data[:limit]
    }

@app.get("/api/stats")
def get_stats():
    """Returns dashboard counter statistics."""
    total = len(opportunities_cache)
    scholarships = sum(1 for x in opportunities_cache if x.get("category") == "Scholarship")
    jobs = sum(1 for x in opportunities_cache if x.get("category") == "Job")
    grants = sum(1 for x in opportunities_cache if x.get("category") == "Grant")
    news = sum(1 for x in opportunities_cache if x.get("category") == "News")

    return {
        "total": total,
        "scholarships": scholarships,
        "jobs": jobs,
        "grants": grants,
        "news": news
    }

class ChatQuery(BaseModel):
    query: str

@app.post("/api/chat")
def chat_rag_endpoint(payload: ChatQuery):
    """RAG-grounded AI conversational Q&A search endpoint."""
    if not payload.query or len(payload.query.strip()) == 0:
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    result = rag_engine.answer_query(payload.query)
    return result

@app.post("/api/crawl")
def trigger_crawl():
    """Triggers an updated web crawl cycle."""
    global opportunities_cache
    new_data = run_crawling_cycle()
    
    # Merge unique items by ID
    existing_ids = {x.get("id") for x in opportunities_cache}
    for item in new_data:
        if item.get("id") not in existing_ids:
            opportunities_cache.insert(0, item)
            existing_ids.add(item.get("id"))

    save_data()
    rag_engine.index_documents(opportunities_cache)

    return {
        "status": "success",
        "message": f"Crawl cycle completed. Total opportunities indexed: {len(opportunities_cache)}",
        "count": len(opportunities_cache)
    }

from backend.job_evaluator import get_user_profile, update_user_profile, evaluate_job_fit, generate_cover_letter, generate_skill_roadmap, generate_tailored_resume
from backend.resume_parser import parse_resume_text
from backend.application_tracker import get_applications, update_application_status
from backend.reactive_cv_builder import render_cv_template_html, generate_reactive_resume_json

class ProfileUpdate(BaseModel):
    name: Optional[str] = None
    skills: Optional[str] = None
    target_roles: Optional[str] = None
    experience_summary: Optional[str] = None
    education: Optional[str] = None

class ItemIdRequest(BaseModel):
    item_id: str

class ResumeUploadRequest(BaseModel):
    resume_text: str

class ApplicationUpdateRequest(BaseModel):
    item_id: str
    status: str

class CVBuilderRequest(BaseModel):
    item_id: Optional[str] = None
    template_type: Optional[str] = "tech"

@app.post("/api/cv/builder")
def cv_builder_endpoint(payload: CVBuilderRequest):
    """Generates application-tailored HTML and Reactive Resume JSON schema CV."""
    profile = get_user_profile()
    target_item = None
    if payload.item_id:
        target_item = next((item for item in opportunities_cache if item.get("id") == payload.item_id), None)

    html_cv = render_cv_template_html(profile, target_item, payload.template_type or "tech")
    json_cv = generate_reactive_resume_json(profile, payload.template_type or "tech")

    return {
        "status": "success",
        "html_cv": html_cv,
        "json_cv": json_cv,
        "template": payload.template_type
    }

@app.get("/api/profile")
def get_profile_endpoint():
    """Gets candidate profile settings."""
    return {"status": "success", "profile": get_user_profile()}

@app.post("/api/profile")
def update_profile_endpoint(payload: ProfileUpdate):
    """Updates candidate profile settings."""
    data = {k: v for k, v in payload.dict().items() if v is not None}
    updated = update_user_profile(data)
    return {"status": "success", "profile": updated}

@app.post("/api/resume/upload")
def upload_resume_text_endpoint(payload: ResumeUploadRequest):
    """Parses resume text and populates candidate profile automatically."""
    parsed = parse_resume_text(payload.resume_text)
    updated = update_user_profile(parsed)
    return {"status": "success", "profile": updated, "message": "Resume parsed and profile updated!"}

@app.post("/api/evaluate")
def evaluate_fit_endpoint(payload: ItemIdRequest):
    """Evaluates candidate fit score (0-100%) against a posting."""
    target_item = next((item for item in opportunities_cache if item.get("id") == payload.item_id), None)
    if not target_item:
        raise HTTPException(status_code=404, detail="Item not found")

    result = evaluate_job_fit(target_item)
    return {"status": "success", "evaluation": result}

@app.post("/api/ai/roadmap")
def skill_roadmap_endpoint(payload: ItemIdRequest):
    """Generates PRD Feature 13 Skill Gap Analysis & Learning Roadmap."""
    target_item = next((item for item in opportunities_cache if item.get("id") == payload.item_id), None)
    if not target_item:
        raise HTTPException(status_code=404, detail="Item not found")

    roadmap = generate_skill_roadmap(target_item)
    return {"status": "success", "roadmap": roadmap}

@app.post("/api/generate-letter")
def generate_cover_letter_endpoint(payload: ItemIdRequest):
    """Generates customized cover letter draft for a posting."""
    target_item = next((item for item in opportunities_cache if item.get("id") == payload.item_id), None)
    if not target_item:
        raise HTTPException(status_code=404, detail="Item not found")

    letter = generate_cover_letter(target_item)
    return {"status": "success", "cover_letter": letter}

@app.post("/api/generate-resume")
def generate_resume_endpoint(payload: ItemIdRequest):
    """Generates customized downloadable resume for a posting."""
    target_item = next((item for item in opportunities_cache if item.get("id") == payload.item_id), None)
    if not target_item:
        raise HTTPException(status_code=404, detail="Item not found")

    resume = generate_tailored_resume(target_item)
    return {"status": "success", "tailored_resume": resume}

@app.get("/api/applications")
def get_applications_endpoint():
    """Gets application tracker board list."""
    return {"status": "success", "applications": get_applications()}

@app.post("/api/applications/update")
def update_application_endpoint(payload: ApplicationUpdateRequest):
    """Updates status for an opportunity in application tracker."""
    target_item = next((item for item in opportunities_cache if item.get("id") == payload.item_id), None)
    app_entry = update_application_status(payload.item_id, payload.status, target_item)
    return {"status": "success", "application": app_entry}

# Mount static frontend directory
frontend_dir = os.path.join(BASE_DIR, "frontend")
if os.path.exists(frontend_dir):
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

    @app.get("/")
    def read_root():
        return FileResponse(os.path.join(frontend_dir, "index.html"))
