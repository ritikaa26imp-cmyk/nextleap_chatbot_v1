#!/bin/bash
# Vercel Deployment Script

echo "🚀 Vercel Deployment Script"
echo ""

# Step 1: Login
echo "Step 1: Login to Vercel"
echo "Please complete authentication in your browser..."
vercel login

# Step 2: Link project
echo ""
echo "Step 2: Linking project to Vercel"
vercel link

# Step 3: Add environment variable
echo ""
echo "Step 3: Adding GEMINI_API_KEY environment variable"
vercel env add GEMINI_API_KEY

# Step 4: Deploy
echo ""
echo "Step 4: Deploying to production..."
vercel --prod

echo ""
echo "✅ Deployment complete!"
