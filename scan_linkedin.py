#!/usr/bin/env python3
"""
LinkedIn Job Scanner
Scrapes LinkedIn public job search results
No authentication required for public listings
"""

import requests
from bs4 import BeautifulSoup
import urllib.parse
import time
import re

def scan_linkedin():
    """
    Scan LinkedIn for grants management jobs
    Returns list of job dictionaries
    """
    
    queries = [
        'grants management',
        'grants consultant',
        'capital grants',
    'capital program manager',
    'federal grants specialist',
    'grant compliance'
    ]
    
    locations = [
        'District of Columbia, United States',
        'United States'  # Remote
    ]
    
    all_results = []
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
    }
    
    for query in queries:
        for location in locations:
            try:
                # Build LinkedIn job search URL
                params = {
                    'keywords': query,
                    'location': location,
                    'f_TPR': 'r604800',  # Past week
                    'sortBy': 'DD'  # Date descending
                }
                
                url = 'https://www.linkedin.com/jobs/search?' + urllib.parse.urlencode(params)
                
                response = requests.get(url, headers=headers, timeout=15)
                
                if response.status_code != 200:
                    print(f"   ⚠ LinkedIn returned {response.status_code}")
                    continue
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find job cards
                job_cards = soup.find_all('div', class_='base-card')
                
                if not job_cards:
                    # Try alternative selector
                    job_cards = soup.find_all('li', class_=lambda x: x and 'jobs-search-results__list-item' in x)
                
                for card in job_cards[:15]:  # Limit per search
                    try:
                        # Extract title
                        title_elem = card.find('h3', class_='base-search-card__title')
                        if not title_elem:
                            title_elem = card.find('a', class_=lambda x: x and 'job-card-list__title' in x)
                        
                        if not title_elem:
                            continue
                        
                        title = title_elem.get_text(strip=True)
                        
                        # Extract company
                        company_elem = card.find('h4', class_='base-search-card__subtitle')
                        if not company_elem:
                            company_elem = card.find('a', class_=lambda x: x and 'job-card-container__company-name' in x)
                        
                        company = company_elem.get_text(strip=True) if company_elem else 'Company not listed'
                        
                        # Extract location
                        location_elem = card.find('span', class_='job-search-card__location')
                        job_location = location_elem.get_text(strip=True) if location_elem else location
                        
                        # Extract job URL and ID
                        link_elem = card.find('a', class_='base-card__full-link')
                        if not link_elem:
                            link_elem = card.find('a', href=lambda x: x and '/jobs/view/' in x)
                        
                        if not link_elem:
                            continue
                        
                        job_url = link_elem.get('href', '')
                        
                        # Extract job ID from URL
                        job_id_match = re.search(r'/jobs/view/(\d+)', job_url)
                        if job_id_match:
                            job_id = job_id_match.group(1)
                        else:
                            # Fallback: use last part of URL
                            job_id = job_url.split('/')[-1].split('?')[0]
                        
                        # Clean URL
                        if not job_url.startswith('http'):
                            job_url = 'https://www.linkedin.com' + job_url
                        
                        # Extract posted date if available
                        time_elem = card.find('time', class_='job-search-card__listdate')
                        if not time_elem:
                            time_elem = card.find('time')
                        posted = time_elem.get('datetime', 'Recent') if time_elem else 'Recent'
                        
                        result = {
                            'id': f'linkedin_{job_id}',
                            'title': title,
                            'agency': company,
                            'location': job_location,
                            'url': job_url,
                            'salary': 'See posting',
                            'posted': posted,
                            'source': 'LinkedIn'
                        }
                        
                        all_results.append(result)
                        
                    except Exception as e:
                        continue
                
                # Be respectful - wait between requests
                time.sleep(3)
                
            except requests.exceptions.RequestException as e:
                print(f"   ⚠ LinkedIn network error: {e}")
                continue
            except Exception as e:
                print(f"   ⚠ LinkedIn parsing error: {e}")
                continue
    
    # Remove duplicates
    seen = set()
    unique_results = []
    for job in all_results:
        if job['id'] not in seen:
            seen.add(job['id'])
            unique_results.append(job)
    
    return unique_results

if __name__ == '__main__':
    # Test the scanner
    jobs = scan_linkedin()
    print(f"Found {len(jobs)} LinkedIn positions")
    for job in jobs[:3]:
        print(f"  {job['title']} - {job['agency']}")
