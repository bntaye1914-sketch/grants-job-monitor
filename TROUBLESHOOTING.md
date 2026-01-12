# Troubleshooting Guide

Common issues and solutions for the Grants Job Monitor.

---

## Email Issues

### Email not received

**Check these first:**
1. ✅ Check spam/junk folder
2. ✅ Wait 5 minutes (sometimes delayed)
3. ✅ Verify workflow completed (green checkmark in Actions)
4. ✅ Check if there were actually new jobs to report

**If still not working:**

1. **Verify Gmail App Password**
   ```
   - Must be 16 characters
   - Should include spaces: "abcd efgh ijkl mnop"
   - Not your regular Gmail password
   - Generated from: https://myaccount.google.com/apppasswords
   ```

2. **Check 2-Step Verification**
   - Must be enabled: https://myaccount.google.com/signinoptions/two-step-verification
   - App passwords won't work without it

3. **Verify Secrets**
   - Go to: Settings → Secrets → Actions
   - Confirm all 5 secrets exist
   - Secret names are case-sensitive
   - No extra spaces in secret names

4. **Test Locally**
   ```bash
   cd grants-job-monitor
   
   export GMAIL_USER="your@gmail.com"
   export GMAIL_APP_PASSWORD="your app password"
   export NOTIFY_EMAIL="your@gmail.com"
   export USAJOBS_API_KEY="your-key"
   export USAJOBS_EMAIL="your@gmail.com"
   
   python test_local.py
   ```

### "Authentication failed" error

**Cause:** Wrong password or 2-Step Verification not enabled

**Fix:**
1. Enable 2-Step Verification
2. Create new App Password
3. Update GMAIL_APP_PASSWORD secret
4. Test again

### Email goes to spam

**Fix:**
1. Mark as "Not Spam"
2. Add sender to contacts
3. Create filter in Gmail:
   - From: Your GMAIL_USER
   - Subject: contains "Grants Jobs"
   - Never send to spam

---

## USAJobs API Issues

### "API error: 401 Unauthorized"

**Cause:** Invalid or missing API key

**Fix:**
1. Verify USAJOBS_API_KEY secret exists
2. Check for typos in API key
3. Request new key: https://developer.usajobs.gov/APIRequest/Index
4. Update secret with new key

### "API error: 429 Too Many Requests"

**Cause:** Exceeded rate limit (rare - 250 requests/day)

**Fix:**
- Wait 1 hour
- Reduce workflow frequency if running very often
- This shouldn't happen with default twice-daily schedule

### No jobs returned from USAJobs

**This is normal if:**
- No new grants jobs posted recently
- Search terms don't match current openings
- All jobs already seen in previous scan

**To verify API works:**
1. Go to: https://www.usajobs.gov
2. Search manually for "grants management"
3. If you see jobs there, API should return them too

**To get more results:**
- Edit `scripts/scan_usajobs.py`
- Add more search terms
- Remove location restrictions

---

## Scraper Issues (Indeed/LinkedIn)

### Indeed returns no jobs

**Common causes:**
- Indeed changed their HTML structure
- Rate limiting (temporary)
- Network timeout

**Fix:**
1. Check if Indeed.com loads in your browser
2. Try again in a few hours
3. If persistent, Indeed may have changed their HTML

**Temporary workaround:**
Comment out Indeed in `scripts/main.py`:
```python
# all_jobs.extend(scan_indeed())
```

### LinkedIn returns no jobs

**Common causes:**
- LinkedIn changed their HTML structure
- Requires login (public jobs should work)
- Rate limiting

**Fix:**
1. Check if LinkedIn jobs load without login
2. Try again later
3. If broken, comment out in `scripts/main.py`

**Update scrapers:**
- Scrapers need updates when sites change HTML
- Check for updates in repository
- Or open an issue

---

## Workflow Issues

### Workflow not running automatically

**Check:**
1. Go to Actions → Grants Job Monitor
2. Look for scheduled runs
3. Should see runs at 8 AM and 8 PM EST

**If no scheduled runs:**

1. **Verify workflow file location**
   - Must be: `.github/workflows/job-scan.yml`
   - Exact path and filename matter

2. **Check cron syntax**
   ```yaml
   on:
     schedule:
       - cron: '0 13,1 * * *'  # Correct format
   ```

3. **Repository activity required**
   - GitHub disables workflows if repo inactive >60 days
   - Make a commit to re-enable

4. **Private repos**
   - Free tier: 2,000 minutes/month
   - Should be plenty for this workflow

### Workflow fails on "Commit updated job tracking data"

**Cause:** Git push permissions

**Fix:**
1. Repository Settings → Actions → General
2. Workflow permissions: Select "Read and write permissions"
3. Click Save
4. Re-run workflow

### Workflow fails immediately

1. Click on failed run
2. Click "scan-jobs"
3. Read error message
4. Common issues:
   - Missing secrets
   - Syntax error in YAML file
   - Python dependency issue

---

## File/Data Issues

### seen_jobs.json not updating

**Check:**
1. Workflow completed successfully?
2. Git push permissions enabled?
3. Look for error in "Commit updated job tracking data" step

**Fix:**
- Enable write permissions (see above)
- Manually trigger workflow to test

### Getting duplicate job notifications

**Cause:** seen_jobs.json not persisting

**Fix:**
1. Check git push step completes
2. Verify seen_jobs.json updates in repo
3. Clear and regenerate:
   ```json
   {
     "job_ids": [],
     "last_updated": "2025-01-12T00:00:00"
   }
   ```

---

## Local Testing Issues

### "Module not found" errors

**Fix:**
```bash
pip install -r requirements.txt
```

### Environment variables not working

**Bash/Linux/Mac:**
```bash
export VARIABLE_NAME="value"
```

**Windows PowerShell:**
```powershell
$env:VARIABLE_NAME="value"
```

**Windows CMD:**
```cmd
set VARIABLE_NAME=value
```

### Import errors

**Fix:**
```bash
cd grants-job-monitor
export PYTHONPATH="${PYTHONPATH}:$(pwd)/scripts"
python test_local.py
```

---

## Performance Issues

### Workflow takes too long (>5 min)

**Normal ranges:**
- USAJobs: 10-30 seconds
- Indeed: 30-60 seconds (due to delays)
- LinkedIn: 30-60 seconds (due to delays)
- Total: 2-4 minutes normal

**If >5 minutes:**
- Check for network timeouts
- Reduce number of searches
- Check GitHub Actions status page

### Too many jobs found

**To filter:**

1. **Edit search terms** - be more specific
2. **Add location filters** - target your area
3. **Add grade/salary filters** in USAJobs scanner

---

## Secret Management Issues

### Can't see secret values

**This is normal:**
- GitHub never shows secret values after creation
- You can only delete and recreate

**To update a secret:**
1. Delete old secret
2. Create new one with same name
3. Enter new value

### Secret names don't match

**Must be exact:**
- `USAJOBS_API_KEY` not `USAJobs_API_Key`
- Case-sensitive
- No spaces in names
- Underscores, not dashes

---

## Notification Frequency Issues

### Not getting enough alerts

**Increase frequency:**

Edit `.github/workflows/job-scan.yml`:
```yaml
on:
  schedule:
    - cron: '0 */4 * * *'  # Every 4 hours
```

### Getting too many alerts

**Decrease frequency:**
```yaml
on:
  schedule:
    - cron: '0 12 * * *'  # Once daily at noon
```

---

## Cost/Usage Issues

### Worried about GitHub Actions minutes

**Check usage:**
1. GitHub → Settings → Billing
2. See Actions minutes used
3. Free tier: 2,000 minutes/month

**This workflow:**
- ~3 minutes per run
- 2 runs/day = 6 min/day
- 30 days = ~180 min/month
- Well under limit

### Want to reduce usage

**Options:**
1. Run once daily instead of twice
2. Disable scrapers that timeout
3. Reduce search terms

---

## Discord Issues (Optional)

### Discord notifications not working

**Check:**
1. Webhook URL is valid
2. Added as `DISCORD_WEBHOOK` secret
3. Webhook still exists in Discord server

**Test webhook:**
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"content":"Test from Job Monitor"}' \
  YOUR_WEBHOOK_URL
```

### Discord message too long

**Automatic fix:**
- Script splits into multiple messages
- Discord limit: 2,000 characters

---

## Still Having Issues?

### Workflow logs

1. Actions → Failed workflow → scan-jobs
2. Expand each step
3. Read error messages
4. Look for:
   - Python tracebacks
   - API error codes
   - Network errors

### Manual test

```bash
cd grants-job-monitor
python test_local.py
```

### Check versions

```bash
python --version  # Should be 3.8+
pip --version
git --version
```

### Last resort

1. Delete repository
2. Start fresh with DEPLOYMENT.md
3. Triple-check all secrets
4. Test locally first

---

## Getting Help

### Before asking for help:

✅ Read this entire troubleshooting guide  
✅ Check workflow logs in Actions tab  
✅ Test locally with test_local.py  
✅ Verify all secrets are correct  
✅ Try manual workflow run  

### When asking for help:

Include:
1. What you're trying to do
2. What actually happens
3. Error messages (full text)
4. Workflow logs (if applicable)
5. What you've already tried

**Privacy note:**
- Never share your API keys
- Never share your App Password
- Redact sensitive info from logs

---

## Preventive Maintenance

### Monthly checks:

- [ ] Verify workflow still running
- [ ] Check email delivery
- [ ] Review Actions minutes usage
- [ ] Test if scrapers still work

### When to update:

- Indeed/LinkedIn return no results for >1 week
- USAJobs API changes (rare)
- GitHub Actions changes (very rare)

---

## Common Misconceptions

**❌ "I need to keep my computer running"**  
✅ No - runs on GitHub's servers

**❌ "I'll get charged if I use too much"**  
✅ Free tier is very generous, you won't hit limits

**❌ "I need to click Run workflow each time"**  
✅ No - runs automatically on schedule

**❌ "The API key will expire"**  
✅ USAJobs API keys don't expire

**❌ "I can't edit search terms after deployment"**  
✅ Yes you can - edit files and push changes

---

## Emergency Fixes

### Stop all notifications immediately

**Option 1: Disable workflow**
1. Actions → Grants Job Monitor
2. Click "..." (three dots)
3. Disable workflow

**Option 2: Delete secrets**
1. Settings → Secrets → Actions
2. Delete GMAIL_APP_PASSWORD
3. Workflow will fail but won't send email

**Option 3: Comment out notification**
Edit `scripts/main.py`:
```python
# send_email_notification(new_jobs)
```

### Clear all seen jobs (reset)

Replace `data/seen_jobs.json` with:
```json
{
  "job_ids": [],
  "last_updated": "2025-01-12T00:00:00"
}
```

Commit and push. Next run will treat all jobs as new.

---

Remember: Most issues are simple config mistakes. Take your time, check each step carefully, and you'll get it working! 🎯
