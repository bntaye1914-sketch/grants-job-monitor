# Quick Setup Checklist

Complete this checklist to get your job monitor running:

## ☐ 1. Repository Setup (5 min)

- [ ] Create new GitHub repository named `grants-job-monitor`
- [ ] Clone this code to your computer
- [ ] Push to your new repository

## ☐ 2. Get USAJobs API Key (2 min)

- [ ] Go to: https://developer.usajobs.gov/APIRequest/Index
- [ ] Fill out registration form
- [ ] Check email for API key
- [ ] Save API key somewhere safe

## ☐ 3. Gmail App Password (5 min)

- [ ] Enable 2-Step Verification: https://myaccount.google.com/signinoptions/two-step-verification
- [ ] Go to: https://myaccount.google.com/apppasswords
- [ ] Create app password named "Grants Job Monitor"
- [ ] Save the 16-character password

## ☐ 4. Add GitHub Secrets (3 min)

Go to: `Your Repo → Settings → Secrets and variables → Actions`

Click "New repository secret" for each:

- [ ] `USAJOBS_API_KEY` = Your USAJobs API key
- [ ] `USAJOBS_EMAIL` = Your email address
- [ ] `GMAIL_USER` = Your Gmail address
- [ ] `GMAIL_APP_PASSWORD` = Your Gmail app password (16 chars)
- [ ] `NOTIFY_EMAIL` = Where to send alerts (probably same Gmail)

## ☐ 5. Test Run (2 min)

- [ ] Go to: `Actions → Grants Job Monitor → Run workflow`
- [ ] Click "Run workflow" button
- [ ] Wait 2-3 minutes
- [ ] Check your email for job alerts

## ☐ 6. Verify (1 min)

- [ ] Workflow completed successfully (green checkmark)
- [ ] Email received with job listings
- [ ] `data/seen_jobs.json` updated in repository

---

## Optional: Discord Setup

- [ ] Create Discord server
- [ ] Server Settings → Integrations → Webhooks → New Webhook
- [ ] Copy webhook URL
- [ ] Add as `DISCORD_WEBHOOK` secret in GitHub
- [ ] Test run to verify Discord notification

---

## Customization (Optional)

- [ ] Edit search terms in scanner files
- [ ] Adjust target locations
- [ ] Change schedule in workflow file
- [ ] Test changes with manual workflow run

---

## Total Time: ~15 minutes

Once complete, your monitor will:
- ✅ Run automatically twice daily (8 AM & 8 PM)
- ✅ Scan USAJobs, Indeed, and LinkedIn
- ✅ Email you only new jobs (no duplicates)
- ✅ Cost you $0/month forever

---

## Having Issues?

1. Check the troubleshooting section in README.md
2. Review workflow logs in Actions tab
3. Verify all secrets are spelled exactly right (case-sensitive)
4. Make sure Gmail 2-Step Verification is enabled
5. Check spam folder for emails

## Success?

🎉 You now have a free, automated job monitoring system that runs 24/7 without any servers or maintenance!
