# Render.com Deployment Configuration

## Prerequisites
- GitHub account with repository: https://github.com/Satyanarayana53/Iot-Task
- Render account (https://render.com)

## Step 1: Prepare Environment Variables
1. Go to Render Dashboard
2. Create a new Web Service
3. Add these environment variables:
   - DATABASE_URL: Your PostgreSQL connection string
   - SECRET_KEY: Generate a random secret key
   - API_KEY: Your API key
   - THINGSPEAK_API_KEY: Your ThingSpeak API key
   - ALLOWED_ORIGINS: http://localhost:3000,https://yourdomain.com

## Step 2: Create Web Service
1. Click "New +"
2. Select "Web Service"
3. Connect your GitHub repository
4. Select branch: main

## Step 3: Configure Build Settings
- **Name**: cap-water-tank-api
- **Environment**: Python 3
- **Region**: Choose your region
- **Build Command**: 
  ```
  pip install -r backend/requirements.txt
  ```
- **Start Command**: 
  ```
  cd backend && bash render-start.sh
  ```

## Step 4: Deploy
- Click Create Web Service
- Monitor deployment logs
- Once deployed, note your URL: https://cap-water-tank-api.onrender.com

## Step 5: Update Frontend
Update `frontend/src/config.js`:
```javascript
const API_BASE_URL = 'https://cap-water-tank-api.onrender.com';
```

## Step 6: Test Deployment
```bash
curl https://cap-water-tank-api.onrender.com/api/health
```

## Troubleshooting
- Check logs in Render dashboard
- Ensure all environment variables are set
- Verify database URL is correct
- Free tier auto-sleeps after 15 minutes of inactivity
