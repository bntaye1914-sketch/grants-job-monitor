#!/usr/bin/env python3
"""
USAJobs.gov Scanner
Uses official USAJobs API (free registration required)
API docs: https://developer.usajobs.gov/
"""

import requests
import os
from datetime import datetime

def scan_usajobs():
    """
    Scan USAJobs.gov for grants management and consultant roles
    Returns list of job dictionaries
    """
    
    # Get credentials from environment
    api_key = os.getenv('USAJOBS_API_KEY')
    email = os.getenv('USAJOBS_EMAIL')
    
    if not api_key or not email:
        print("   ⚠ USAJobs API credentials not configured")
        return []
    
    headers = {
        'Authorization-Key': api_key,
        'User-Agent': email
    }
    
    # Search parameters
    search_terms = [
        'grants management',
        'grants consultant',
        'capital grants',
    'capital program manager',
    'federal grants specialist',
    'grant compliance'
    ]
    
    all_results = []
    
    for term in search_terms:
        params = {
            'Keyword': term,
            'ResultsPerPage': 50,
            'SortField': 'PostingDate',
            'SortOrder': 'Descending'
        }
        
        try:
            response = requests.get(
                'https://data.usajobs.gov/api/search',
                params=params,
                headers=headers,
                timeout=15
            )
            
            if response.status_code != 200:
                print(f"   ⚠ API returned {response.status_code} for '{term}'")
                continue
            
            data = response.json()
            
            if 'SearchResult' not in data or not data['SearchResult']:
                continue
            
            items = data['SearchResult'].get('SearchResultItems', [])
            
            for item in items:
                try:
                    job = item['MatchedObjectDescriptor']
                    
                    # Extract salary info
                    salary_min = 'Not listed'
                    salary_max = 'Not listed'
                    if 'PositionRemuneration' in job and job['PositionRemuneration']:
                        salary_min = job['PositionRemuneration'][0].get('MinimumRange', 'Not listed')
                        salary_max = job['PositionRemuneration'][0].get('MaximumRange', 'Not listed')
                    
                    salary_display = f"${salary_min:,} - ${salary_max:,}" if isinstance(salary_min, (int, float)) else salary_min
                    
                    result = {
                        'id': item['MatchedObjectId'],
                        'title': job.get('PositionTitle', 'Unknown Position'),
                        'agency': job.get('OrganizationName', 'Unknown Agency'),
                        'location': job.get('PositionLocationDisplay', 'Location not specified'),
                        'url': job.get('PositionURI', ''),
                        'salary': salary_display,
                        'posted': job.get('PublicationStartDate', ''),
                        'closes': job.get('ApplicationCloseDate', ''),
                        'grade': job.get('JobGrade', [{}])[0].get('Code', 'N/A') if job.get('JobGrade') else 'N/A',
                        'source': 'USAJobs'
                    }
                    
                    all_results.append(result)
                    
                except (KeyError, IndexError, TypeError) as e:
                    continue
            
        except requests.exceptions.RequestException as e:
            print(f"   ⚠ Network error for '{term}': {e}")
            continue
    
    # Remove duplicates by ID
    seen = set()
    unique_results = []
    for job in all_results:
        if job['id'] not in seen:
            seen.add(job['id'])
            unique_results.append(job)
    
    return unique_results

if __name__ == '__main__':
    # Test the scanner
    jobs = scan_usajobs()
    print(f"Found {len(jobs)} USAJobs positions")
    for job in jobs[:3]:
        print(f"  {job['title']} - {job['agency']}")
