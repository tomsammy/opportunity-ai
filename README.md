# OpportunityIQ - High-Value Web Intelligence & RAG Platform

OpportunityIQ is a specialized AI web intelligence engine designed to automatically crawl, extract, clean, categorize, and index high-value **Scholarships, Remote Jobs, Fellowships, and Tech/Grant News**.

It features a high-speed Python scraping backend, structured JSON/Markdown schema extractor, semantic vector search, and a glassmorphism web dashboard with an embedded RAG AI Copilot.

---

## 🌟 Key Features

1. **Tiered Web Crawler:** Ingests data from RSS feeds, static web portals, and dynamic Playwright browser pages.
2. **AI Schema Extractor:** Normalizes raw content into verified JSON (`title`, `category`, `funding_amount`, `deadline`, `eligibility`, `apply_url`, `source_name`).
3. **Semantic RAG Assistant:** Interactive conversational assistant answering student/job seeker queries grounded in live web intelligence.
4. **Live Categories & Search:** Dynamic tabs (`Scholarship`, `Job`, `Grant`, `News`), keyword search, and statistics dashboard.
5. **Ready for One-Click Hosting:** Built for easy deployment to Vercel (frontend) and Render / Railway / Docker (backend).

---

## 🚀 Quick Start (Local Run)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Launch the Application
```bash
python run_server.py
```

Open your browser and navigate to: **`http://localhost:8000`**

---

## 🌐 API Reference

* `GET /api/opportunities`: Filtered opportunity directory. Query parameters: `category` (All, Scholarship, Job, Grant, News), `search` (keyword).
* `GET /api/stats`: Counter statistics per category.
* `POST /api/chat`: Grounded RAG conversational endpoint (`{ "query": "..." }`).
* `POST /api/crawl`: Triggers live web crawler cycle.

---

## ☁️ Deployment Guide

### Deploying Backend to Render / Railway
1. Push this code repository to GitHub.
2. Connect your GitHub repository to **Render** or **Railway**.
3. Set Build Command: `pip install -r requirements.txt`
4. Set Start Command: `python run_server.py`

### Deploying Frontend to Vercel
1. Set Vercel root directory to `/frontend`.
2. Configure the API endpoint in `app.js` to point to your live Render backend URL.
