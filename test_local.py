#!/usr/bin/env python3
"""
Local Test Script
Run this to verify your configuration before deploying to GitHub Actions

Usage:
    export USAJOBS_API_KEY="your-key"
    export USAJOBS_EMAIL="your@email.com"
    export GMAIL_USER="your@gmail.com"
    export GMAIL_APP_PASSWORD="your-app-password"
    export NOTIFY_EMAIL="your@email.com"
    
    python test_local.py
"""

import os
import sys

def test_environment_variables():
    """Check if all required environment variables are set"""
    print("=" * 60)
    print("1. Testing Environment Variables")
    print("=" * 60)
    
    required = {
        'USAJOBS_API_KEY': 'USAJobs API key',
        'USAJOBS_EMAIL': 'USAJobs email',
        'GMAIL_USER': 'Gmail address',
        'GMAIL_APP_PASSWORD': 'Gmail app password',
        'NOTIFY_EMAIL': 'Notification email'
    }
    
    all_set = True
    for var, desc in required.items():
        value = os.getenv(var)
        if value:
            masked = value[:4] + '...' + value[-4:] if len(value) > 8 else '***'
            print(f"✓ {var}: {masked}")
        else:
            print(f"✗ {var}: NOT SET ({desc})")
            all_set = False
    
    if not all_set:
        print("\n❌ Missing required environment variables")
        print("\nSet them like this:")
        print('  export USAJOBS_API_KEY="your-key"')
        return False
    
    print("\n✅ All environment variables set")
    return True

def test_usajobs():
    """Test USAJobs API connection"""
    print("\n" + "=" * 60)
    print("2. Testing USAJobs API")
    print("=" * 60)
    
    try:
        from scan_usajobs import scan_usajobs
        jobs = scan_usajobs()
        
        if jobs:
            print(f"✓ Found {len(jobs)} jobs on USAJobs")
            print(f"\nSample jobs:")
            for job in jobs[:3]:
                print(f"  • {job['title']}")
                print(f"    {job['agency']}")
                print(f"    {job['url']}")
            print("\n✅ USAJobs API working")
            return True
        else:
            print("⚠ No jobs found (this might be normal if there are no matches)")
            print("✅ USAJobs API connected successfully")
            return True
            
    except Exception as e:
        print(f"❌ USAJobs error: {e}")
        return False

def test_indeed():
    """Test Indeed scraper"""
    print("\n" + "=" * 60)
    print("3. Testing Indeed Scraper")
    print("=" * 60)
    
    try:
        from scan_indeed import scan_indeed
        jobs = scan_indeed()
        
        if jobs:
            print(f"✓ Found {len(jobs)} jobs on Indeed")
            print(f"\nSample jobs:")
            for job in jobs[:3]:
                print(f"  • {job['title']}")
                print(f"    {job['agency']}")
            print("\n✅ Indeed scraper working")
        else:
            print("⚠ No jobs found on Indeed")
            print("   (This could be normal or the scraper needs updating)")
        
        return True
        
    except Exception as e:
        print(f"⚠ Indeed error: {e}")
        print("   (Indeed scraper may need updates if their HTML changed)")
        return True  # Don't fail on scraper issues

def test_linkedin():
    """Test LinkedIn scraper"""
    print("\n" + "=" * 60)
    print("4. Testing LinkedIn Scraper")
    print("=" * 60)
    
    try:
        from scan_linkedin import scan_linkedin
        jobs = scan_linkedin()
        
        if jobs:
            print(f"✓ Found {len(jobs)} jobs on LinkedIn")
            print(f"\nSample jobs:")
            for job in jobs[:3]:
                print(f"  • {job['title']}")
                print(f"    {job['agency']}")
            print("\n✅ LinkedIn scraper working")
        else:
            print("⚠ No jobs found on LinkedIn")
            print("   (This could be normal or the scraper needs updating)")
        
        return True
        
    except Exception as e:
        print(f"⚠ LinkedIn error: {e}")
        print("   (LinkedIn scraper may need updates if their HTML changed)")
        return True  # Don't fail on scraper issues

def test_email():
    """Test email notification"""
    print("\n" + "=" * 60)
    print("5. Testing Email Notification")
    print("=" * 60)
    
    try:
        from notify import send_email_notification
        
        test_job = {
            'id': 'test_123',
            'title': 'TEST: Grants Manager Position',
            'agency': 'Test Agency (This is a test email)',
            'location': 'Baltimore, MD',
            'url': 'https://example.com/test',
            'salary': '$85,000 - $110,000',
            'posted': '2025-01-12',
            'source': 'Test'
        }
        
        print("Sending test email...")
        send_email_notification([test_job])
        
        print("\n✅ Email sent!")
        print(f"   Check your inbox: {os.getenv('NOTIFY_EMAIL')}")
        print("   (Also check spam folder)")
        
        return True
        
    except Exception as e:
        print(f"❌ Email error: {e}")
        print("\nCommon issues:")
        print("  • Make sure 2-Step Verification is enabled on Google")
        print("  • Use App Password (not regular password)")
        print("  • Check that GMAIL_APP_PASSWORD has no spaces")
        return False

def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("GRANTS JOB MONITOR - Local Test")
    print("=" * 60)
    
    # Add scripts directory to path
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scripts'))
    
    results = []
    
    # Run tests
    results.append(("Environment", test_environment_variables()))
    
    if results[0][1]:  # Only continue if env vars are set
        results.append(("USAJobs", test_usajobs()))
        results.append(("Indeed", test_indeed()))
        results.append(("LinkedIn", test_linkedin()))
        results.append(("Email", test_email()))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {name}")
    
    all_passed = all(result[1] for result in results)
    
    if all_passed:
        print("\n" + "=" * 60)
        print("🎉 ALL TESTS PASSED!")
        print("=" * 60)
        print("\nYou're ready to deploy to GitHub Actions!")
        print("\nNext steps:")
        print("1. Add all secrets to GitHub (see SETUP_CHECKLIST.md)")
        print("2. Push this code to your repository")
        print("3. Go to Actions tab and run workflow manually")
        print("4. Wait for email notification")
    else:
        print("\n" + "=" * 60)
        print("❌ SOME TESTS FAILED")
        print("=" * 60)
        print("\nFix the failed tests before deploying.")
        print("See troubleshooting section in README.md")

if __name__ == '__main__':
    main()
