import json
import os
from datetime import datetime
from backend.config import BASE_DIR

APPLICATIONS_DB_PATH = os.path.join(BASE_DIR, "backend", "data", "applications.json")

applications_store = {}

def load_applications():
    global applications_store
    if os.path.exists(APPLICATIONS_DB_PATH):
        try:
            with open(APPLICATIONS_DB_PATH, "r", encoding="utf-8") as f:
                applications_store = json.load(f)
        except Exception:
            applications_store = {}

def save_applications():
    os.makedirs(os.path.dirname(APPLICATIONS_DB_PATH), exist_ok=True)
    with open(APPLICATIONS_DB_PATH, "w", encoding="utf-8") as f:
        json.dump(applications_store, f, indent=2)

load_applications()

def get_applications() -> list:
    return list(applications_store.values())

def update_application_status(item_id: str, status: str, item_details: dict = None) -> dict:
    global applications_store
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")

    if item_id in applications_store:
        applications_store[item_id]["status"] = status
        applications_store[item_id]["updated_at"] = now_str
        if status == "Applied" and not applications_store[item_id].get("applied_at"):
            applications_store[item_id]["applied_at"] = now_str
    else:
        title = item_details.get("title", "Opportunity") if item_details else "Opportunity"
        category = item_details.get("category", "Job") if item_details else "Job"
        source = item_details.get("source_name", "Verified Source") if item_details else "Verified Source"
        deadline = item_details.get("deadline", "Rolling") if item_details else "Rolling"

        applications_store[item_id] = {
            "item_id": item_id,
            "title": title,
            "category": category,
            "source_name": source,
            "deadline": deadline,
            "status": status,
            "saved_at": now_str,
            "applied_at": now_str if status == "Applied" else None,
            "updated_at": now_str
        }

    save_applications()
    return applications_store[item_id]
