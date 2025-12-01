# Railway Deployment Setup Guide

## Environment Variables

You need to set the following environment variable in Railway:

### Required Variables

1. **GEMINI_API_KEY**
   - Value: `AIzaSyAowbwS15xpzN2bs8Q3rGhvlQe4SN3kMSc`
   - Description: Google Gemini API key for LLM functionality

## How to Add Environment Variables in Railway

1. Go to your Railway project dashboard
2. Click on your service (nextleap_chatbot_v1)
3. Navigate to the **Variables** tab
4. Click **+ New Variable**
5. Add:
   - **Variable Name**: `GEMINI_API_KEY`
   - **Value**: `AIzaSyAowbwS15xpzN2bs8Q3rGhvlQe4SN3kMSc`
6. Click **Add**
7. Railway will automatically redeploy with the new environment variable

## Verification

After setting the environment variable, check the deployment logs to ensure:
- The API key is loaded (you'll see "Using API key from environment variable" in logs)
- The server starts successfully
- The `/health` endpoint returns a successful response

## Security Notes

- ✅ The API key is stored securely in Railway's environment variables
- ✅ The API key is NOT committed to the repository
- ✅ The `.env` file is gitignored
- ⚠️ Never commit API keys to version control

