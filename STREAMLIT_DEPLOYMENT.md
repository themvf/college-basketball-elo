# Deploy to Streamlit Cloud

## Quick Deployment Steps

### 1. Push Your Code to GitHub ✅
Your code is already pushed to GitHub on branch: `claude/plan-to-track-011CUycCoSJUTMAyG6q9gYMu`

### 2. Go to Streamlit Cloud
Visit: **https://share.streamlit.io**

### 3. Sign In
- Click "Sign in" or "Get started"
- Sign in with your GitHub account (the same one that has this repository)

### 4. Deploy New App
1. Click **"New app"** button
2. Fill in the deployment settings:
   - **Repository**: `themvf/college-basketball-elo`
   - **Branch**: `claude/plan-to-track-011CUycCoSJUTMAyG6q9gYMu` (or merge to main first)
   - **Main file path**: `app.py`
3. Click **"Deploy"**

### 5. Wait for Deployment
- Streamlit Cloud will install dependencies from `requirements.txt`
- Takes 2-5 minutes for first deployment
- You'll see build logs in real-time

### 6. Access Your App
Once deployed, you'll get a URL like:
- `https://your-app-name.streamlit.app`
- Share this URL with anyone!

## Important Notes

### Data Files
The following data files are included in the repository and will be available:
- `Data/predictions_database.csv` (your 168 predictions with results)
- `Data/performance_metrics.json` (calculated statistics)
- All ELO game data files

These were already committed, so they'll be deployed automatically.

### Automatic Updates
The GitHub Actions workflows will continue to run daily:
- Updates game data
- Makes new predictions
- Updates the predictions database
- Commits changes back to GitHub
- Streamlit Cloud will **auto-refresh** when changes are pushed!

### Branch Options

**Option A: Deploy from feature branch** (Quick)
- Deploy directly from `claude/plan-to-track-011CUycCoSJUTMAyG6q9gYMu`
- Fastest way to get online
- Can merge to main later

**Option B: Merge to main first** (Recommended)
```bash
git checkout main
git merge claude/plan-to-track-011CUycCoSJUTMAyG6q9gYMu
git push origin main
```
Then deploy from `main` branch

## Troubleshooting

### Build Fails
- Check requirements.txt has all dependencies
- Look at build logs for specific errors
- Most common: missing Python packages

### App Crashes on Startup
- Check Data/ directory exists with CSV files
- Verify predictions_database.csv is committed
- Check app.py runs locally first

### Data Not Showing
- Make sure you ran `python setup_tracking_database.py` locally first
- Ensure `Data/predictions_database.csv` was committed
- Check file is in the repository on GitHub

## Configuration

### .streamlit/config.toml (Optional)
Create this file for custom settings:
```toml
[theme]
primaryColor = "#FF6B6B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"

[server]
maxUploadSize = 200
enableXsrfProtection = true
```

### .streamlit/secrets.toml (Optional)
For API keys or secrets (never commit this file):
```toml
# Add any secrets here
# This file is NOT committed to GitHub
```

## Updating Your Deployed App

After deploying, any push to the selected branch will trigger auto-redeployment:

1. Make changes locally
2. Commit: `git commit -am "Update app"`
3. Push: `git push origin <branch-name>`
4. Streamlit Cloud detects the push
5. App automatically redeploys (takes 1-2 minutes)

## Managing Your App

From Streamlit Cloud dashboard:
- **View logs**: See runtime errors
- **Reboot app**: Force restart
- **Delete app**: Remove deployment
- **Settings**: Change branch, secrets, etc.

## Cost

Streamlit Community Cloud is **FREE** for public repositories!
- Unlimited apps
- Unlimited viewers
- Auto-deploys from GitHub
- 1GB storage per app
- Shared resources (good for most apps)

## Support

- Streamlit Docs: https://docs.streamlit.io/streamlit-community-cloud
- Community Forum: https://discuss.streamlit.io
- GitHub Issues: Report bugs in your repo

---

**Your app is ready to deploy!** Just visit https://share.streamlit.io and follow the steps above. 🚀
