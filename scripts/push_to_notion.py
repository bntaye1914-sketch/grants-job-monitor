#!/usr/bin/env python3
"""
Job Monitor → Notion Integration
UPGRADED TO API VERSION 2025-09-03 (Multi-source database support)
"""
import os
import sys
import json
import hashlib
import requests
from datetime import datetime
from typing import Dict, Optional

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
NOTION_DB_ID = os.getenv("NOTION_DB_ID")

# STEP 5: Upgraded to API version 2025-09-03
HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2025-09-03"
}

# Cache for data_source_id to avoid repeated API calls
DATA_SOURCE_ID_CACHE = None

TARGET_AGENCIES = [
    "dod", "defense", "army", "navy", "air force",
    "va", "veterans affairs", "gsa", "general services",
    "dhs", "homeland security", "hhs", "health and human services",
    "doe", "energy", "dot", "transportation", "usaid",
    "census", "noaa", "reclamation"
]

HIGH_PRIORITY_KEYWORDS = [
    "capital", "infrastructure", "construction",
    "senior", "lead", "manager", "director", "portfolio"
]


def get_data_source_id() -> Optional[str]:
    """
    STEP 1: Add discovery step to fetch and store the data_source_id
    Retrieves the data_source_id from the database for use in subsequent API calls.
    """
    global DATA_SOURCE_ID_CACHE
    
    if DATA_SOURCE_ID_CACHE:
        return DATA_SOURCE_ID_CACHE
    
    try:
        # Get Database returns data_sources array in 2025-09-03
        response = requests.get(
            f"https://api.notion.com/v1/databases/{NOTION_DB_ID}",
            headers=HEADERS,
            timeout=10
        )
        response.raise_for_status()
        
        data = response.json()
        data_sources = data.get("data_sources", [])
        
        if not data_sources:
            print("❌ No data sources found in database")
            return None
        
        # Use the first data source (most databases will have only one initially)
        DATA_SOURCE_ID_CACHE = data_sources[0]["id"]
        print(f"✓ Retrieved data_source_id: {DATA_SOURCE_ID_CACHE}")
        return DATA_SOURCE_ID_CACHE
        
    except Exception as e:
        print(f"❌ Failed to get data_source_id: {e}")
        return None


def generate_job_hash(agency: str, title: str, location: str) -> str:
    content = f"{agency.lower()}{title.lower()}{location.lower()}"
    return hashlib.md5(content.encode()).hexdigest()


def check_duplicate(job_hash: str) -> bool:
    """
    STEP 3: Migrated to use data source query endpoint
    """
    data_source_id = get_data_source_id()
    if not data_source_id:
        return False
    
    query = {"filter": {"property": "Job Hash", "rich_text": {"equals": job_hash}}}
    
    try:
        # STEP 3: Changed from /v1/databases/:database_id/query to /v1/data_sources/:data_source_id/query
        response = requests.post(
            f"https://api.notion.com/v1/data_sources/{data_source_id}/query",
            headers=HEADERS, 
            json=query, 
            timeout=10
        )
        response.raise_for_status()
        return len(response.json().get("results", [])) > 0
    except:
        return False


def calculate_priority(job_data: Dict) -> str:
    title = job_data.get("title", "").lower()
    agency = job_data.get("agency", "").lower()
    salary_str = str(job_data.get("salary", ""))
    
    high_signals = []
    
    if "$" in salary_str:
        try:
            nums = ''.join(filter(str.isdigit, salary_str.replace(",", "")))
            if nums and int(nums[:6]) >= 120000:
                high_signals.append("salary")
        except:
            pass
    
    if "gs-14" in salary_str.lower() or "gs-15" in salary_str.lower():
        high_signals.append("gs_level")
    
    if any(target in agency for target in TARGET_AGENCIES):
        high_signals.append("agency")
    
    if any(kw in title for kw in HIGH_PRIORITY_KEYWORDS):
        high_signals.append("keywords")
    
    if len(high_signals) >= 1:
        return "High"
    
    if "gs-12" in salary_str.lower() or "gs-13" in salary_str.lower():
        return "Medium"
    
    if "$" in salary_str:
        try:
            nums = ''.join(filter(str.isdigit, salary_str.replace(",", "")))
            if nums and 90000 <= int(nums[:6]) < 120000:
                return "Medium"
        except:
            pass
    
    return "Low"


def classify_type(job_data: Dict) -> str:
    title = job_data.get("title", "").lower()
    description = job_data.get("description", "").lower()
    combined = f"{title} {description}"
    
    if "capital" in combined or "construction" in combined:
        return "Federal Capital"
    elif "infrastructure" in combined:
        return "Infrastructure"
    elif "contract" in combined or "contractor" in combined:
        return "Contract"
    else:
        return "Federal General"


def create_notion_page(job_data: Dict, debug: bool = False) -> bool:
    """
    STEP 2: Updated to use data_source_id when creating pages
    """
    # Get data_source_id for this database
    data_source_id = get_data_source_id()
    if not data_source_id:
        print("❌ Cannot create page: no data_source_id available")
        return False
    
    job_hash = generate_job_hash(
        job_data.get("agency", "Unknown"),
        job_data["title"],
        job_data.get("location", "Remote")
    )
    
    if check_duplicate(job_hash):
        print(f"⏭️  Skipped (duplicate): {job_data['title']}")
        return False
    
    priority = calculate_priority(job_data)
    job_type = classify_type(job_data)
    
    # Build notes (limit to 2000 chars)
    notes_parts = []
    if job_data.get("agency"):
        notes_parts.append(f"Agency: {job_data['agency']}")
    if job_data.get("salary"):
        notes_parts.append(f"Salary: {job_data['salary']}")
    if job_data.get("posted_date"):
        notes_parts.append(f"Posted: {job_data['posted_date']}")
    if job_data.get("closing_date"):
        notes_parts.append(f"Closes: {job_data['closing_date']}")
    if job_data.get("description"):
        desc = job_data['description'][:400]
        notes_parts.append(f"\n{desc}...")
    
    notes_content = "\n".join(notes_parts) if notes_parts else "No details"
    if len(notes_content) > 1900:
        notes_content = notes_content[:1900] + "..."
    
    job_url = job_data.get("url")
    if not job_url or not job_url.strip():
        job_url = "https://placeholder.com"
    
    # STEP 2: Changed parent from database_id to data_source_id
    payload = {
        "parent": {
            "type": "data_source_id",
            "data_source_id": data_source_id
        },
        "properties": {
            "Opportunity": {"title": [{"text": {"content": job_data["title"]}}]},
            "Source": {"select": {"name": job_data.get("source", "Other")}},
            "URL": {"url": job_url},
            "Priority": {"select": {"name": priority}},
            "Status": {"status": {"name": "Monitoring"}},
            "Type": {"select": {"name": job_type}},
            "Job Hash": {"rich_text": [{"text": {"content": job_hash}}]},
            "Notes": {"rich_text": [{"text": {"content": notes_content}}]},
            "Date Added": {"date": {"start": datetime.now().strftime("%Y-%m-%d")}}
        }
    }
    
    if debug:
        print(f"\n🔍 DEBUG - Payload for: {job_data['title']}")
        print(json.dumps(payload, indent=2))
    
    try:
        response = requests.post(
            "https://api.notion.com/v1/pages",
            headers=HEADERS,
            json=payload,
            timeout=10
        )
        
        # ALWAYS print full error on failure
        if response.status_code != 200:
            print(f"\n❌ Failed: {job_data['title']}")
            print(f"   Status: {response.status_code}")
            print(f"   Full API Response:")
            try:
                print(json.dumps(response.json(), indent=4))
            except:
                print(response.text)
            return False
        
        print(f"✅ Created: {job_data['title']} [Priority: {priority}, Type: {job_type}]")
        return True
        
    except Exception as e:
        print(f"❌ Exception for {job_data['title']}: {e}")
        return False


def main():
    if not NOTION_TOKEN or not NOTION_DB_ID:
        print("❌ Missing NOTION_TOKEN or NOTION_DB_ID")
        sys.exit(1)
    
    print(f"\n🔄 Notion API Migration Status:")
    print(f"   ✓ API Version: 2025-09-03 (multi-source database support)")
    print(f"   ✓ Using data_source_id for page creation")
    print(f"   ✓ Using data source query endpoint")
    
    jobs_file = "jobs_output.json"
    
    if not os.path.exists(jobs_file):
        print(f"ℹ️  No jobs file found: {jobs_file}")
        sys.exit(0)
    
    try:
        with open(jobs_file, 'r') as f:
            jobs = json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON: {e}")
        sys.exit(1)
    
    if not jobs:
        print("ℹ️  No jobs to process")
        sys.exit(0)
    
    print(f"\n🔄 Processing {len(jobs)} opportunities...\n")
    
    created = 0
    skipped = 0
    failed = 0
    
    # Process first job with debug output
    debug_first = True
    
    for idx, job in enumerate(jobs):
        if not job.get("title"):
            print("⚠️  Skipped job with no title")
            failed += 1
            continue
        
        result = create_notion_page(job, debug=debug_first and idx == 0)
        
        if result:
            created += 1
        else:
            job_hash = generate_job_hash(
                job.get("agency", "Unknown"),
                job["title"],
                job.get("location", "Remote")
            )
            if check_duplicate(job_hash):
                skipped += 1
            else:
                failed += 1
    
    print(f"\n📊 Summary:")
    print(f"   ✅ Created: {created}")
    print(f"   ⏭️  Skipped (duplicates): {skipped}")
    print(f"   ❌ Failed: {failed}")
    
    if failed > 0 and created == 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
