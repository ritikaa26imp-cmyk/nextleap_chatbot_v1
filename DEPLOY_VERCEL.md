# Vercel Deployment Guide

## Prerequisites
1. Vercel account (sign up at https://vercel.com)
2. Vercel CLI installed: `npm i -g vercel`
3. Git repository pushed to GitHub/GitLab/Bitbucket

## Deployment Steps

### Step 1: Install Vercel CLI (if not already installed)
```bash
npm i -g vercel
```

### Step 2: Login to Vercel
```bash
vercel login
```

### Step 3: Navigate to project directory
```bash
cd /Users/ritikadey/nextleap_chatbot_v1
```

### Step 4: Link project to Vercel
```bash
vercel link
```
- Follow prompts to:
  - Link to existing project OR create new project
  - Set project name (e.g., `nextleap-chatbot`)
  - Confirm settings

### Step 5: Set Environment Variables
```bash
vercel env add GEMINI_API_KEY
```
- Enter your Gemini API key when prompted
- Select "Production", "Preview", and "Development" environments

### Step 6: Deploy
```bash
vercel --prod
```

Or deploy to preview:
```bash
vercel
```

### Step 7: Verify Deployment
1. Check deployment URL provided by Vercel
2. Visit: `https://your-project.vercel.app`
3. Test the chatbot

## Important Notes

### Knowledge Base
- The knowledge base will be built automatically on first query
- Models are cached in `/tmp` (ephemeral storage)
- First query may take longer (~30-60 seconds) to build KB

### Environment Variables
Required environment variable:
- `GEMINI_API_KEY`: Your Google Gemini API key

### File Structure
- Frontend files: `/frontend/`
- API serverless function: `/api/index.py`
- Configuration: `vercel.json`

### Troubleshooting

#### Build fails?
- Check that `mangum` is in `requirements.txt`
- Verify Python version (3.9+)
- Check build logs in Vercel dashboard

#### API not working?
- Verify `GEMINI_API_KEY` is set in Vercel environment variables
- Check function logs in Vercel dashboard
- Ensure routes are configured in `vercel.json`

#### Frontend not loading?
- Check that frontend files are in `/frontend/` directory
- Verify routes in `vercel.json`
- Check browser console for errors

## Alternative: Deploy via GitHub Integration

1. Go to https://vercel.com/dashboard
2. Click "Add New Project"
3. Import your Git repository
4. Configure:
   - Framework Preset: Other
   - Root Directory: ./
   - Build Command: (leave empty)
   - Output Directory: (leave empty)
5. Add environment variable: `GEMINI_API_KEY`
6. Click "Deploy"

## Post-Deployment

After successful deployment:
1. Your chatbot will be available at: `https://your-project.vercel.app`
2. First query will build the knowledge base (may take 30-60 seconds)
3. Subsequent queries will be fast

## Updating Deployment

To update after making changes:
```bash
git add .
git commit -m "Your changes"
git push
vercel --prod
```

Or if using GitHub integration, just push to your main branch.
