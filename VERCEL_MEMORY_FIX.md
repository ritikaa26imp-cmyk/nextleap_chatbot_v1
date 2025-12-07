# Fixing Vercel Memory Limit Error

## Problem
Build fails with "exceeded the amount of memory available" because:
- Large packages (sentence-transformers, chromadb, numpy, pandas)
- Models being downloaded during build
- Memory-intensive compilation

## Solutions Applied

### 1. Optimized Install Command
Added `--no-cache-dir` to reduce memory usage:
```json
"installCommand": "pip install --no-cache-dir -r requirements.txt"
```

### 2. Excluded Large Files
Created `.vercelignore` to exclude:
- Knowledge base data
- Cache files
- Log files
- Virtual environments

### 3. Alternative Solutions (if still failing)

#### Option A: Upgrade Vercel Plan
- Hobby plan: 1024 MB memory limit
- Pro plan: 2048 MB memory limit
- Upgrade in Vercel Dashboard → Settings → Plan

#### Option B: Split Dependencies
Install heavy packages at runtime instead of build time:
- Move model downloads to first request
- Use lighter alternatives where possible

#### Option C: Use Vercel CLI with Larger Memory
Deploy via CLI with increased memory allocation (if available)

#### Option D: Optimize Package Versions
Use pre-built wheels instead of compiling from source:
- Ensure all packages have wheels available
- Avoid packages that need compilation

## Current Optimizations
✅ `--no-cache-dir` flag added
✅ `.vercelignore` created
✅ Large files excluded from build

## Next Steps
1. Try deploying again
2. If still failing, consider upgrading Vercel plan
3. Or optimize further by lazy-loading heavy dependencies
