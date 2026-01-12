# Deployment Guide

Step-by-step instructions to deploy your Grants Job Monitor to GitHub.

---

## Prerequisites

- [x] GitHub account (free)
- [x] Gmail account (for notifications)
- [x] Git installed on your computer

---

## Step 1: Create GitHub Repository

1. Go to: https://github.com/new
2. Repository name: `grants-job-monitor`
3. Description: "Automated grants job monitoring system"
4. Set to **Private** (recommended) or Public
5. **Do NOT** initialize with README, .gitignore, or license
6. Click "Create repository"

---

## Step 2: Upload Your Code

### Option A: Using Git Command Line

```bash
# Navigate to the grants-job-monitor folder
cd grants-job-monitor

# Initialize git repository
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit: Grants Job Monitor"

# Link to your GitHub repository (replace YOUR-USERNAME)
git remote add origin https://github.com/YOUR-USERNAME/grants-job-monitor.git

# Push to GitHub
git branch -M main
git push -u origin main
```

### Option B: Using GitHub Desktop

1. Open GitHub Desktop
2. File → Add Local Repository
3. Choose the `grants-job-monitor` folder
4. Click "Publish repository"
5. Choose repository name: `grants-job-monitor`
6. Set visibility (Private recommended)
7. Click "Publish repository"

### Option C: Upload via Web

1. On your new repo page, click "uploading an existing file"
2. Drag the entire `grants-job-monitor` folder
3. Commit changes

---

## Step 3: Get USAJobs API Key

1. Go to: https://developer.usajobs.gov/APIRequest/Index
2. Fill out the form:
   - **Email**: Your email address
   - **First Name**: Your first name
   - **Last Name**: Your last name
   - **Purpose**: Job search automation
3. Click "Submit"
4. Check your email for API key (arrives instantly)
5. **Save the API key** - you'll need it in Step 5

---

## Step 4: Set Up Gmail App Password

### Enable 2-Step Verification (if not already enabled)

1. Go to: https://myaccount.google.com/signinoptions/two-step-verification
2. Follow prompts to enable 2-Step Verification
3. Use your phone for verification codes

### Create App Password

1. Go to: https://myaccount.google.com/apppasswords
2. You may need to sign in again
3. App name: `Grants Job Monitor`
4. Click "Create"
5. **Copy the 16-character password** (shown like: `abcd efgh ijkl mnop`)
6. Save it - you won't see it again

**Note:** This is NOT your regular Gmail password. It's a special password just for this app.

---

## Step 5: Add Secrets to GitHub

1. Go to your repository on GitHub
2. Click **Settings** (top menu)
3. Click **Secrets and variables** (left sidebar)
4. Click **Actions**
5. Click **New repository secret** button

Add these secrets **one at a time**:

### Secret 1: USAJOBS_API_KEY
- Name: `USAJOBS_API_KEY`
- Value: Your USAJobs API key from Step 3
- Click "Add secret"

### Secret 2: USAJOBS_EMAIL
- Name: `USAJOBS_EMAIL`
- Value: Your email address (same as registration)
- Click "Add secret"

### Secret 3: GMAIL_USER
- Name: `GMAIL_USER`
- Value: Your Gmail address (e.g., `yourname@gmail.com`)
- Click "Add secret"

### Secret 4: GMAIL_APP_PASSWORD
- Name: `GMAIL_APP_PASSWORD`
- Value: The 16-character app password from Step 4
- **Important:** Include the spaces (e.g., `abcd efgh ijkl mnop`)
- Click "Add secret"

### Secret 5: NOTIFY_EMAIL
- Name: `NOTIFY_EMAIL`
- Value: Where to send alerts (usually same as GMAIL_USER)
- Click "Add secret"

**Verify:** You should now see 5 secrets listed.

---

## Step 6: Test Your Setup

1. Go to **Actions** tab in your repository
2. You should see "Grants Job Monitor" workflow
3. Click on "Grants Job Monitor"
4. Click **Run workflow** button (right side)
5. Click green **Run workflow** button in popup
6. Wait 2-3 minutes

### Watch the workflow run:

- Click on the running workflow
- Click on "scan-jobs"
- Watch the logs in real-time
- Look for green checkmarks

### What should happen:

- ✅ Checkout code
- ✅ Install Python
- ✅ Install dependencies
- ✅ Run job scan (this takes ~2 min)
- ✅ Commit updates
- ✅ Upload results

---

## Step 7: Verify Success

### Check Email

- Go to your inbox (the NOTIFY_EMAIL address)
- Look for email: "🎯 X New Grants Jobs Found"
- **Check spam folder** if not in inbox

### Check Repository

- Go to your repository
- Look at `data/seen_jobs.json`
- Should show recent update time
- Should have job IDs listed

### Check Workflow Status

- Go to Actions tab
- Latest run should have green checkmark ✓
- If red X, click to see error logs

---

## Step 8: Schedule Verification

Your workflow is now set to run automatically twice daily:
- 8:00 AM EST
- 8:00 PM EST

To verify automatic runs:
1. Wait for the next scheduled time
2. Check Actions tab - you'll see new runs appear
3. Check your email for notifications

---

## Troubleshooting

### "Email sent" but no email received

1. Check spam folder
2. Verify NOTIFY_EMAIL is correct
3. Try sending test email from Gmail web interface to verify account works
4. Check GMAIL_APP_PASSWORD has spaces included
5. Verify 2-Step Verification is enabled

### "USAJobs API error: 401"

- Your API key is incorrect or not set properly
- Double-check USAJOBS_API_KEY secret
- Make sure USAJOBS_EMAIL matches registration

### Workflow failing on "Run job scan"

1. Click on failed workflow
2. Click "scan-jobs"
3. Expand "Run job scan" step
4. Read error message
5. Usually a missing or incorrect secret

### No jobs found

This is normal if:
- No new grants jobs posted recently
- All jobs were found in previous scan
- Search terms don't match current listings

Try customizing search terms in scanner files.

---

## Success Indicators

✅ Workflow runs with green checkmark  
✅ Email received with job listings  
✅ `data/seen_jobs.json` updates automatically  
✅ No duplicate alerts for same jobs  
✅ Runs automatically on schedule  

---

## Next Steps

1. **Customize searches**: Edit scanner files to add more search terms
2. **Adjust schedule**: Modify `.github/workflows/job-scan.yml` cron schedule
3. **Add Discord** (optional): Set up webhook for instant mobile alerts
4. **Monitor results**: Check Actions tab periodically for workflow status

---

## Need Help?

1. Check README.md troubleshooting section
2. Review workflow logs in Actions tab
3. Verify all secrets are spelled exactly right
4. Test locally using `test_local.py` script

---

## Maintenance

**No regular maintenance needed!**

The system runs automatically. Only act if:
- Scrapers break (Indeed/LinkedIn change their HTML)
- You want to change search terms
- You need to update email address
- API keys expire (USAJobs keys don't expire)

**Update scrapers:**
- If Indeed/LinkedIn stop returning results
- Open issue on GitHub or fix locally
- Usually just HTML selector changes

---

## You're Done! 🎉

Your automated grants job monitor is now:
- ✅ Running 24/7
- ✅ Monitoring 3 job platforms
- ✅ Sending email alerts
- ✅ Costing you $0/month

Check your email at 8 AM and 8 PM daily for new opportunities!
