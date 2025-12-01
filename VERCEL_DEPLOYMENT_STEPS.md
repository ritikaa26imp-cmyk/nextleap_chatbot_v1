# 🚀 Vercel Deployment Steps

## ✅ Pre-Deployment Checklist

- [x] Railway files removed
- [x] Vercel configuration files added
- [x] Changes committed and pushed to main branch
- [ ] Vercel CLI installed
- [ ] Vercel account created
- [ ] GEMINI_API_KEY ready

---

## 📋 Step-by-Step Deployment Guide

### Option 1: Deploy via Vercel CLI (Recommended)

#### Step 1: Install Vercel CLI (if not already installed)
```bash
npm install -g vercel
```

#### Step 2: Login to Vercel
```bash
vercel login
```
- This will open a browser for authentication
- Follow the prompts to complete login

#### Step 3: Navigate to Project Directory
```bash
cd /Users/ritikadey/nextleap_chatbot_v1
```

#### Step 4: Link Project to Vercel (First Time Only)
```bash
vercel link
```
- Choose: **Create a new project** (or link to existing)
- Project name: `nextleap-chatbot` (or your preferred name)
- Directory: `./` (current directory)
- Override settings: **No**

#### Step 5: Set Environment Variable
```bash
vercel env add GEMINI_API_KEY
```
- When prompted, enter your Google Gemini API key
- Select environments: **Production, Preview, and Development** (all three)

#### Step 6: Deploy to Production
```bash
vercel --prod
```

#### Step 7: Verify Deployment
1. Vercel will provide a deployment URL (e.g., `https://nextleap-chatbot.vercel.app`)
2. Visit the URL in your browser
3. Test the chatbot with a sample query
4. **Note**: First query may take 30-60 seconds to build the knowledge base

---

### Option 2: Deploy via Vercel Dashboard (GitHub Integration)

#### Step 1: Push Code to GitHub
```bash
# Already done - code is on main branch
git remote -v  # Verify GitHub remote is set
```

#### Step 2: Go to Vercel Dashboard
1. Visit: https://vercel.com/dashboard
2. Click **"Add New Project"** or **"Import Project"**

#### Step 3: Import Git Repository
1. Select your Git provider (GitHub/GitLab/Bitbucket)
2. Authorize Vercel to access your repositories
3. Find and select: `nextleap_chatbot_v1`
4. Click **"Import"**

#### Step 4: Configure Project
- **Framework Preset**: Other
- **Root Directory**: `./` (leave as default)
- **Build Command**: (leave empty)
- **Output Directory**: (leave empty)
- **Install Command**: (leave empty)

#### Step 5: Add Environment Variable
- Click **"Environment Variables"**
- Add variable:
  - **Name**: `GEMINI_API_KEY`
  - **Value**: (your Gemini API key)
  - **Environments**: Select all (Production, Preview, Development)

#### Step 6: Deploy
1. Click **"Deploy"**
2. Wait for build to complete (2-5 minutes)
3. Visit the provided URL

---

## 🔍 Post-Deployment Verification

### 1. Check Health Endpoint
```bash
curl https://your-project.vercel.app/api/health
```
Expected response:
```json
{
  "status": "healthy",
  "message": "Nextleap FAQ Chatbot API is running",
  "knowledge_base_chunks": 0
}
```
(Chunks will be 0 initially, will build on first query)

### 2. Test API Endpoint
```bash
curl -X POST https://your-project.vercel.app/api/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the cost of data analyst course?"}'
```

### 3. Test Frontend
- Visit: `https://your-project.vercel.app`
- Try a sample query
- Verify source URLs are displayed

---

## ⚠️ Important Notes

### Knowledge Base Building
- **First Query**: Will take 30-60 seconds (building KB)
- **Subsequent Queries**: Fast (< 5 seconds)
- KB is built automatically on first query if missing
- Models are cached in `/tmp` (ephemeral storage)

### Environment Variables
- **Required**: `GEMINI_API_KEY`
- Set in Vercel dashboard: Settings → Environment Variables
- Available in: Production, Preview, Development

### Function Timeout
- Default timeout: 10 seconds (Hobby plan)
- Extended timeout: 60 seconds (configured in `vercel.json`)
- For Pro plan: Up to 300 seconds available

### Cold Starts
- First request after inactivity: ~5-10 seconds
- Subsequent requests: < 1 second
- This is normal for serverless functions

---

## 🔧 Troubleshooting

### Build Fails?
1. Check build logs in Vercel dashboard
2. Verify `mangum` is in `requirements.txt`
3. Check Python version (3.9+)
4. Review error messages in logs

### API Returns 500 Error?
1. Check function logs in Vercel dashboard
2. Verify `GEMINI_API_KEY` is set correctly
3. Check if KB build is failing
4. Review server logs for errors

### Frontend Not Loading?
1. Check browser console for errors
2. Verify routes in `vercel.json`
3. Ensure frontend files are in `/frontend/` directory
4. Check network tab for failed requests

### Knowledge Base Not Building?
1. Check function logs for errors
2. Verify `data/processed/nextleap_courses.json` exists
3. Check if scripts are accessible
4. Review timeout settings (may need Pro plan for long builds)

---

## 📝 Updating Deployment

### After Making Changes:
```bash
git add .
git commit -m "Your changes"
git push origin main
```

### If Using CLI:
```bash
vercel --prod
```

### If Using GitHub Integration:
- Just push to main branch
- Vercel will auto-deploy

---

## 🎯 Quick Reference

**Deployment URL**: `https://your-project.vercel.app`  
**API Endpoint**: `https://your-project.vercel.app/api/query`  
**Health Check**: `https://your-project.vercel.app/api/health`  
**Frontend**: `https://your-project.vercel.app/`

**Environment Variable**: `GEMINI_API_KEY`

---

## ✅ Success Criteria

- [ ] Deployment completes without errors
- [ ] Health endpoint returns 200 OK
- [ ] Frontend loads correctly
- [ ] First query builds KB successfully
- [ ] Subsequent queries return answers quickly
- [ ] Source URLs are displayed correctly

---

**Need Help?** Check Vercel documentation: https://vercel.com/docs
