# GitHub Push Guide

This document contains the step-by-step instructions to push your code to GitHub.

## Step 1: Get Your GitHub Token
1. Go to https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Select these scopes:
   - `repo` (full control of private repositories)
   - `workflow` (update GitHub Action workflows)
4. Copy your token (you won't see it again!)

## Step 2: Configure Remote
```powershell
cd "c:\Users\Abhishek\Downloads\CAP--IIIT-master\CAP--IIIT-master"

# Add remote if not already done
git remote add origin https://github.com/Satyanarayana53/Iot-Task.git
```

## Step 3: Add and Commit Files
```powershell
# Add all files (respects .gitignore)
git add .

# Check what will be committed
git status

# Commit
git commit -m "Initial commit: Water Tank Monitoring System with ML Model"
```

## Step 4: Push to GitHub
```powershell
# Set main branch
git branch -M main

# Push to repository
git push -u origin main
```

When prompted:
- **Username**: Your GitHub username (e.g., Satyanarayana53)
- **Password**: Your Personal Access Token (from Step 1)

## Step 5: Verify
Visit: https://github.com/Satyanarayana53/Iot-Task
Check if all files are there!

---

**⚠️ IMPORTANT**: 
- Never commit .env file (it's in .gitignore)
- Use .env.example as template
- Keep tokens and passwords secret
