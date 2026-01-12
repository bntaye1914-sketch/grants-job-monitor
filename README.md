# 🎯 Grants Job Monitor

Automated job scanner that monitors **USAJobs.gov**, **Indeed**, and **LinkedIn** for grants management and consultant positions.

**100% free** • Runs on GitHub Actions • No servers required

---

## Features

- ✅ Scans 3 major job platforms twice daily
- ✅ Email notifications for new jobs (HTML formatted)
- ✅ Optional Discord webhook alerts
- ✅ Duplicate detection (never get alerted twice)
- ✅ Job archiving for historical tracking
- ✅ Zero cost (GitHub Actions free tier: 2,000 min/month)

---

## Quick Setup (15 minutes)

### 1. Fork/Clone This Repo

```bash
# Create new repo on GitHub, then:
git clone https://github.com/YOUR-USERNAME/grants-job-monitor.git
cd grants-job-monitor
git add .
git commit -m "Initial setup"
git push origin main
```

### 2. Get USAJobs API Key (FREE)

1. Go to: https://developer.usajobs.gov/APIRequest/Index
2. Fill out form (takes 2 minutes)
3. Receive API key via email instantly
4. Save your API key and email address

### 3. Set Up Gmail App Password

**Note:** You need a Gmail account. App passwords are different from your regular password.

1. Go to: https://myaccount.google.com/apppasswords
2. Sign in to your Google account
3. Enter app name: "Grants Job Monitor"
4. Click "Create"
5. Copy the 16-character password
6. Save it (you won't see it again)

**Can't find App Passwords?**
- You need 2-Step Verification enabled first: https://myaccount.google.com/signinoptions/two-step-verification

### 4. Add Secrets to GitHub

Go to your repo: **Settings → Secrets and variables → Actions → New repository secret**

Add these secrets (one at a time):

| Secret Name | Value | Example |
|-------------|-------|---------|
| `USAJOBS_API_KEY` | Your USAJobs API key | `abc123def456...` |
| `USAJOBS_EMAIL` | Your email (for API) | `your.email@gmail.com` |
| `GMAIL_USER` | Your Gmail address | `your.email@gmail.com` |
| `GMAIL_APP_PASSWORD` | Gmail app password | `abcd efgh ijkl mnop` |
| `NOTIFY_EMAIL` | Where to send alerts | `your.email@gmail.com` |

**Optional (Discord):**
| Secret Name | Value |
|-------------|-------|
| `DISCORD_WEBHOOK` | Discord webhook URL |

---

## Test It Manually

Go to: **Actions → Grants Job Monitor → Run workflow**

Click "Run workflow" button

Wait 2-3 minutes, then check:
- ✅ Workflow completes successfully
- ✅ Email arrives in your inbox
- ✅ `data/seen_jobs.json` updates in repo

---

## Customization

### Change Search Terms

Edit `scripts/scan_usajobs.py`, `scripts/scan_indeed.py`, and `scripts/scan_linkedin.py`:

```python
search_terms = [
    'grants management',
    'grants consultant',
    'capital grants',
    'your custom term here'  # Add more
]
```

### Change Locations

Edit the scanner files:

```python
locations = [
    'Maryland',
    'Virginia',
    'Washington DC',
    'Remote'
]
```

### Change Schedule

Edit `.github/workflows/job-scan.yml`:

```yaml
on:
  schedule:
    - cron: '0 13,1 * * *'  # Current: 8 AM and 8 PM EST
    # Examples:
    # - cron: '0 */6 * * *'   # Every 6 hours
    # - cron: '0 9 * * *'     # Once daily at 9 AM UTC
```

**Cron syntax:** `minute hour day month weekday`

Use https://crontab.guru to build your schedule

---

## Troubleshooting

### Email not working?

**Check:**
1. ✅ Gmail App Password (not regular password)
2. ✅ 2-Step Verification enabled on Google account
3. ✅ All secrets spelled exactly as shown (case-sensitive)
4. ✅ Check spam folder

**Test locally:**
```bash
export GMAIL_USER="your@gmail.com"
export GMAIL_APP_PASSWORD="your-app-password"
export NOTIFY_EMAIL="your@gmail.com"
export USAJOBS_API_KEY="your-key"
export USAJOBS_EMAIL="your@gmail.com"

cd scripts
python notify.py  # Test email only
```

### USAJobs not returning results?

- Check API key is valid
- Make sure `USAJOBS_EMAIL` matches what you registered
- API has rate limits (250 requests/day - should never hit this)

### Indeed/LinkedIn not working?

These sites change their HTML frequently. If scrapers break:

1. Open an issue in this repo
2. Or disable by commenting out in `scripts/main.py`:
   ```python
   # all_jobs.extend(scan_indeed())
   # all_jobs.extend(scan_linkedin())
   ```

### Workflow not running?

- Make sure workflow file is in `.github/workflows/` directory
- Check Actions tab for error messages
- Verify all secrets are set correctly

---

## File Structure

```
grants-job-monitor/
├── .github/
│   └── workflows/
│       └── job-scan.yml          # GitHub Actions automation
├── scripts/
│   ├── main.py                   # Orchestrator
│   ├── scan_usajobs.py          # USAJobs scanner
│   ├── scan_indeed.py           # Indeed scanner
│   ├── scan_linkedin.py         # LinkedIn scanner
│   └── notify.py                # Email/Discord alerts
├── data/
│   ├── seen_jobs.json           # Tracks seen jobs
│   └── jobs_archive_*.json      # Historical data
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

---

## Optional: Discord Setup

**Why Discord?**
- Faster setup than email
- Mobile push notifications
- No Gmail restrictions

**Setup:**
1. Create Discord server (or use existing)
2. Server Settings → Integrations → Webhooks
3. Click "New Webhook"
4. Name it "Job Monitor"
5. Copy webhook URL
6. Add as `DISCORD_WEBHOOK` secret in GitHub

---

## Cost Analysis

| Resource | Usage | Cost |
|----------|-------|------|
| GitHub Actions | ~180 min/month | $0 (free tier: 2,000 min) |
| USAJobs API | ~60 calls/month | $0 (free, unlimited) |
| Gmail SMTP | ~60 emails/month | $0 (unlimited) |
| Repository | <1 MB storage | $0 |
| **Total** | | **$0/month** |

---

## Monitoring

**Check workflow runs:**
- Go to: Actions tab in GitHub
- View logs for each run
- Download job archives as artifacts

**Job archives:**
- Located in `data/jobs_archive_TIMESTAMP.json`
- Contains full details of all jobs found
- Kept in repo for historical reference

---

## Advanced: Local Testing

```bash
# Clone repo
git clone https://github.com/YOUR-USERNAME/grants-job-monitor.git
cd grants-job-monitor

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export USAJOBS_API_KEY="your-key"
export USAJOBS_EMAIL="your@email.com"
export GMAIL_USER="your@gmail.com"
export GMAIL_APP_PASSWORD="your-app-password"
export NOTIFY_EMAIL="your@email.com"

# Run
cd scripts
python main.py
```

---

## FAQ

**Q: Can I run this more frequently than twice daily?**  
A: Yes, but be respectful. GitHub Actions gives you 2,000 free minutes/month. Each run takes ~3 minutes, so you could run up to ~20 times per day.

**Q: Will this get my IP banned from job sites?**  
A: No. The scrapers use polite delays, proper user agents, and only access public pages. USAJobs uses their official API.

**Q: Can I add more job sites?**  
A: Yes. Create a new scanner in `scripts/` following the same pattern, then add it to `main.py`.

**Q: What if I don't want email notifications?**  
A: Comment out `send_email_notification()` in `main.py` and use Discord instead, or just check the logs in GitHub Actions.

**Q: Can I search for non-grants jobs?**  
A: Yes. Just change the search terms in the scanner files.

---

## Support

- **Issues:** Open a GitHub issue
- **Updates:** Watch this repo for improvements
- **Contributions:** PRs welcome

---

## License

MIT License - Use freely for personal or commercial purposes.

Built for grants professionals who want to stay ahead of opportunities without manual searching.
