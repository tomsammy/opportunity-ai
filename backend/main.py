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

    if not opportunities_cache:
        # Seed initial data
        opportunities_cache = run_crawling_cycle()
        save_data()

    rag_engine.index_documents(opportunities_cache)

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
    data = opportunities_cache

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

# Mount static frontend directory
frontend_dir = os.path.join(BASE_DIR, "frontend")
if os.path.exists(frontend_dir):
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

    @app.get("/")
    def read_root():
        return FileResponse(os.path.join(frontend_dir, "index.html"))
