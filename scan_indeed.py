#!/usr/bin/env python3
"""
Indeed Job Scanner
Scrapes Indeed search results (public pages only)
Uses respectful delays and user agent
"""

import requests
from bs4 import BeautifulSoup
import time
import re

def scan_indeed():
    """
    Scan Indeed for grants management jobs
    Returns list of job dictionaries
    """
    
        queries = [ 
        'grants management',
        'grants consultant',
        'capital grants manager',
    'capital program manager',
    'federal grants specialist',
    'grant compliance'
    ]
    
    locations = [
        'Washington DC',
        'Remote'
    ]
    
    all_results = []
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
    }
    
    for query in queries:
        for location in locations:
            try:
                # Build Indeed URL
                query_encoded = query.replace(' ', '+')
                location_encoded = location.replace(' ', '+')
                url = f'https://www.indeed.com/jobs?q={query_encoded}&l={location_encoded}&sort=date&fromage=7'
                
                response = requests.get(url, headers=headers, timeout=15)
                
                if response.status_code != 200:
                    print(f"   ⚠ Indeed returned {response.status_code}")
                    continue
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find job cards - Indeed's structure as of 2024/2025
                # Note: This may need updates if Indeed changes their HTML
                job_cards = soup.find_all('div', class_='job_seen_beacon')
                
                if not job_cards:
                    # Try alternative structure
                    job_cards = soup.find_all('td', class_='resultContent')
                
                for card in job_cards[:15]:  # Limit per search
                    try:
                        # Extract job ID
                        job_id = card.get('data-jk', '')
                        if not job_id:
                            # Try alternative location
                            link = card.find('a', id=lambda x: x and x.startswith('job_'))
                            if link:
                                job_id = link.get('id', '').replace('job_', '')
                        
                        if not job_id:
                            continue
                        
                        # Extract title
                        title_elem = card.find('h2', class_='jobTitle')
                        if not title_elem:
                            title_elem = card.find('a', class_='jcs-JobTitle')
                        
                        if not title_elem:
                            continue
                        
                        title = title_elem.get_text(strip=True)
                        
                        # Remove "new" badge if present
                        title = re.sub(r'^(new|New)\s*', '', title)
                        
                        # Extract company
                        company_elem = card.find('span', class_='companyName')
                        if not company_elem:
                            company_elem = card.find('span', {'data-testid': 'company-name'})
                        
                        company = company_elem.get_text(strip=True) if company_elem else 'Company not listed'
                        
                        # Extract location
                        location_elem = card.find('div', class_='companyLocation')
                        job_location = location_elem.get_text(strip=True) if location_elem else location
                        
                        # Extract salary if available
                        salary_elem = card.find('div', class_='salary-snippet')
                        if not salary_elem:
                            salary_elem = card.find('span', class_='estimated-salary')
                        salary = salary_elem.get_text(strip=True) if salary_elem else 'See posting'
                        
                        result = {
                            'id': f'indeed_{job_id}',
                            'title': title,
                            'agency': company,
                            'location': job_location,
                            'url': f'https://www.indeed.com/viewjob?jk={job_id}',
                            'salary': salary,
                            'posted': 'Within 7 days',
                            'source': 'Indeed'
                        }
                        
                        all_results.append(result)
                        
                    except Exception as e:
                        continue
                
                # Be respectful - wait between requests
                time.sleep(3)
                
            except requests.exceptions.RequestException as e:
                print(f"   ⚠ Indeed network error: {e}")
                continue
            except Exception as e:
                print(f"   ⚠ Indeed parsing error: {e}")
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
    jobs = scan_indeed()
    print(f"Found {len(jobs)} Indeed positions")
    for job in jobs[:3]:
        print(f"  {job['title']} - {job['agency']}")
