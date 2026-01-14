#!/usr/bin/env python3
"""
Grants Job Monitor - Main Orchestrator
Scans USAJobs, Indeed, and LinkedIn for grants management opportunities
"""

import json
import os
from datetime import datetime
from scan_usajobs import scan_usajobs
# from scan_indeed import scan_indeed
from scan_linkedin import scan_linkedin
from notify import send_email_notification, send_discord_notification

def load_seen_jobs():
    """Load previously seen job IDs from storage"""
    try:
        with open('data/seen_jobs.json', 'r') as f:
            data = json.load(f)
            return set(data.get('job_ids', []))
    except FileNotFoundError:
        return set()
    except Exception as e:
        print(f"Error loading seen jobs: {e}")
        return set()

def save_seen_jobs(seen_ids):
    """Save job IDs to prevent duplicate notifications"""
    try:
        os.makedirs('data', exist_ok=True)
        with open('data/seen_jobs.json', 'w') as f:
            json.dump({
                'job_ids': list(seen_ids),
                'last_updated': datetime.now().isoformat()
            }, f, indent=2)
    except Exception as e:
        print(f"Error saving seen jobs: {e}")

def save_job_archive(all_jobs):
    """Archive all found jobs for reference"""
    try:
        os.makedirs('data', exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        with open(f'data/jobs_archive_{timestamp}.json', 'w') as f:
            json.dump(all_jobs, f, indent=2)
    except Exception as e:
        print(f"Error archiving jobs: {e}")

def main():
    print("=" * 60)
    print("🔍 GRANTS JOB MONITOR - Starting Scan")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Scan all platforms
    all_jobs = []
    
    print("\n📋 Scanning USAJobs.gov...")
    try:
        usajobs_results = scan_usajobs()
        all_jobs.extend(usajobs_results)
        print(f"   Found: {len(usajobs_results)} jobs")
    except Exception as e:
        print(f"   ❌ USAJobs error: {e}")
    
#     print("\n🔎 Scanning Indeed...")
#     try:
#         indeed_results = scan_indeed()
#         all_jobs.extend(indeed_results)
#         print(f"   Found: {len(indeed_results)} jobs")
#     except Exception as e:
#         print(f"   ❌ Indeed error: {e}")
    
    print("\n💼 Scanning LinkedIn...")
    try:
        linkedin_results = scan_linkedin()
        all_jobs.extend(linkedin_results)
        print(f"   Found: {len(linkedin_results)} jobs")
    except Exception as e:
        print(f"   ❌ LinkedIn error: {e}")
    
    print(f"\n📊 Total jobs found: {len(all_jobs)}")
    
    # Filter for new jobs
    seen_ids = load_seen_jobs()
    new_jobs = [j for j in all_jobs if j['id'] not in seen_ids]
    
    if new_jobs:
        print(f"✨ NEW JOBS: {len(new_jobs)}")
        print("\nNew opportunities:")
        for job in new_jobs[:5]:  # Show first 5
            print(f"  • {job['title']} at {job['agency']}")
        if len(new_jobs) > 5:
            print(f"  ... and {len(new_jobs) - 5} more")
        
        # Send notifications
        print("\n📧 Sending notifications...")
        try:
            send_email_notification(new_jobs)
            print("   ✓ Email sent")
        except Exception as e:
            print(f"   ⚠ Email failed: {e}")
        
        try:
            send_discord_notification(new_jobs)
            print("   ✓ Discord sent")
        except Exception as e:
            print(f"   ⚠ Discord skipped (webhook not configured)")
        
        # Update seen jobs
        new_ids = {j['id'] for j in new_jobs}
        seen_ids.update(new_ids)
        save_seen_jobs(seen_ids)
        
        # Archive results
        save_job_archive(new_jobs)

        # Save for Notion integration
        with open('jobs_output.json', 'w') as f:
            json.dump(new_jobs, f, indent=2)

    else:
                print("✓ No new jobs this scan (all previously seen)")
    
    print("\n" + "=" * 60)
    print("✅ Scan complete")
    print("=" * 60)

if __name__ == '__main__':
    main()
