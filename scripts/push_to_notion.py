#!/usr/bin/env python3
"""
Job Monitor → Notion Integration
Auto-populates Opportunity Intelligence database with deduplication.
"""

import os
import sys
import json
import hashlib
import requests
from datetime import datetime
from typing import Dict, List, Optional

# Configuration
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
NOTION_DB_ID = os.getenv("NOTION_DB_ID")
HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

# Target agencies for high-priority scoring
TARGET_AGENCIES = [
    "dod", "defense", "army", "navy", "air force",
    "va", "veterans affairs",
    "gsa", "general services",
    "dhs", "homeland security",
    "hhs", "health and human services",
    "doe", "energy",
    "dot", "transportation",
    "usaid",
    "census", "noaa", "reclamation"
]

# High-priority keywords
HIGH_PRIORITY_KEYWORDS = [
    "capital", "infrastructure", "construction",
    "senior", "lead", "manager", "director",
    "portfolio"
]

def generate_job_hash(agency: str, title: str, location: str) -> str:
    """Generate MD5 hash for deduplication."""
    content = f"{agency.lower()}{title.lower()}{location.lower()}"
    return hashlib.md5(content.encode()).hexdigest()

def check_duplicate(job_hash: str) -> bool:
    """Check if job already exists in database."""
    query = {
        "filter": {
            "property": "Job Hash",
            "rich_text": {"equals": job_hash}
        }
    }
    
    try:
        response = requests.post(
            f"https://api.notion.com/v1/databases/{NOTION_DB_ID}/query",
            headers=HEADERS,
            json=query,
            timeout=10
        )
        response.raise_for_status()
        results = response.json().get("results", [])
        return len(results) > 0
    except Exception as e:
        print(f"⚠️  Duplicate check failed: {e}")
        return False

def calculate_priority(job_data: Dict) -> str:
    """Assign priority based on fit signals."""
    title = job_data.get("title", "").lower()
    agency = job_data.get("agency", "").lower()
    salary_str = job_data.get("salary", "")
    
    # High priority conditions
    high_signals = []
    
    # Salary threshold (≥$120k or GS-14+)
    if "$" in salary_str:
        try:
            # Extract first number after $ (rough parse)
            amount = int(''.join(filter(str.isdigit, salary_str.split("$")[1])))
            if amount >= 120000:
                high_signals.append("salary")
        except:
            pass
    
    if "gs-14" in salary_str.lower() or "gs-15" in salary_str.lower():
        high_signals.append("gs_level")
    
    # Target agency
    if any(target in agency for target in TARGET_AGENCIES):
        high_signals.append("agency")
    
    # Keywords in title
    if any(kw in title for kw in HIGH_PRIORITY_KEYWORDS):
        high_signals.append("keywords")
    
    # Portfolio value (if mentioned)
    if "$50m" in title or "$100m" in title or "million" in title:
        high_signals.append("portfolio")
    
    # Decision logic
    if len(high_signals) >= 1:
        return "High"
    
    # Medium priority: Federal + reasonable salary
    if "gs-12" in salary_str.lower() or "gs-13" in salary_str.lower():
        return "Medium"
    
    if "$" in salary_str:
        try:
            amount = int(''.join(filter(str.isdigit, salary_str.split("$")[1])))
            if 90000 <= amount < 120000:
                return "Medium"
        except:
            pass
    
    return "Low"

def classify_type(job_data: Dict) -> str:
    """Classify opportunity type based on keywords."""
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

def create_notion_page(job_data: Dict) -> bool:
    """Create new page in Notion database."""
    job_hash = generate_job_hash(
        job_data.get("agency", "Unknown"),
        job_data["title"],
        job_data.get("location", "Remote")
    )
    
    # Check for duplicate
    if check_duplicate(job_hash):
        print(f"⏭️  Skipped (duplicate): {job_data['title']}")
        return False
    
    priority = calculate_priority(job_data)
    job_type = classify_type(job_data)
    
    # Build notes field
    notes_parts = []
    if job_data.get("agency"):
        notes_parts.append(f"**Agency:** {job_data['agency']}")
    if job_data.get("salary"):
        notes_parts.append(f"**Salary:** {job_data['salary']}")
    if job_data.get("posted_date"):
        notes_parts.append(f"**Posted:** {job_data['posted_date']}")
    if job_data.get("closing_date"):
        notes_parts.append(f"**Closes:** {job_data['closing_date']}")
    if job_data.get("description"):
        # Truncate description to avoid hitting Notion's limits
        desc = job_data['description'][:500]
        notes_parts.append(f"\n{desc}...")
    
    notes_content = "\n".join(notes_parts) if notes_parts else "No additional details"
    
    # Handle missing URL
    job_url = job_data.get("url")
    if not job_url or job_url.strip() == "":
        job_url = "https://placeholder.com"
    
    # Construct payload - FIXED DATE FORMAT
    payload = {
        "parent": {"database_id": NOTION_DB_ID},
        "properties": {
            "Opportunity": {
                "title": [{"text": {"content": job_data["title"]}}]
            },
            "Source": {
                "select": {"name": job_data.get("source", "Other")}
            },
            "userDefined:URL": {
                "url": job_url
            },
            "Priority": {
                "select": {"name": priority}
            },
            "Status": {
                "status": {"name": "Monitoring"}
            },
            "Type": {
                "select": {"name": job_type}
            },
            "Job Hash": {
                "rich_text": [{"text": {"content": job_hash}}]
            },
            "Notes": {
                "rich_text": [{"text": {"content": notes_content}}]
            },
            "Date Added": {
                "date": {
                    "start": datetime.now().strftime("%Y-%m-%d")
                }
            }
        }
    }
    
    try:
        response = requests.post(
            "https://api.notion.com/v1/pages",
            headers=HEADERS,
            json=payload,
            timeout=10
        )
        response.raise_for_status()
        print(f"✅ Created: {job_data['title']} [Priority: {priority}]")
        return True
    except requests.exceptions.HTTPError as e:
        error_body = e.response.json() if e.response else {}
        print(f"❌ Failed: {job_data['title']}")
        print(f"   Status: {e.response.status_code}")
        print(f"   Error: {error_body.get('message', 'Unknown error')}")
        return False
    except Exception as e:
        print(f"❌ Failed: {job_data['title']} | Error: {e}")
        return False

def main():
    """Main execution."""
    if not NOTION_TOKEN or not NOTION_DB_ID:
        print("❌ Missing NOTION_TOKEN or NOTION_DB_ID environment variables")
        sys.exit(1)
    
    # Load jobs from file
    jobs_file = "jobs_output.json"
    
    if not os.path.exists(jobs_file):
        print(f"ℹ️  No jobs file found: {jobs_file}")
        print("   This is normal if no jobs were found during scanning.")
        sys.exit(0)
    
    try:
        with open(jobs_file, 'r') as f:
            jobs = json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in {jobs_file}: {e}")
        sys.exit(1)
    
    if not jobs:
        print("ℹ️  No jobs to process")
        sys.exit(0)
    
    print(f"\n🔄 Processing {len(jobs)} opportunities...\n")
    
    created_count = 0
    skipped_count = 0
    failed_count = 0
    
    for job in jobs:
        # Validate required fields
        if not job.get("title"):
            print(f"⚠️  Skipped job with no title")
            failed_count += 1
            continue
        
        result = create_notion_page(job)
        if result:
            created_count += 1
        else:
            # Check if it was a duplicate or a failure
            job_hash = generate_job_hash(
                job.get("agency", "Unknown"),
                job["title"],
                job.get("location", "Remote")
            )
            if check_duplicate(job_hash):
                skipped_count += 1
            else:
                failed_count += 1
    
    print(f"\n📊 Summary:")
    print(f"   ✅ Created: {created_count}")
    print(f"   ⏭️  Skipped (duplicates): {skipped_count}")
    print(f"   ❌ Failed: {failed_count}")
    
    # Exit with error code if all jobs failed
    if failed_count > 0 and created_count == 0:
        sys.exit(1)

if __name__ == "__main__":
    main()
