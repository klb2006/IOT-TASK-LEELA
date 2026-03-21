# Render Deployment Instructions

## Step 1: Go to Render Dashboard
https://render.com/dashboard

## Step 2: Create New Web Service
1. Click **"New +"** → **"Web Service"**
2. Select your GitHub repo: `Satyanarayana53/Iot-Task`
3. Choose branch: `main`

## Step 3: Configure Settings

### Basic Settings
- **Name**: `cap-water-tank-api`
- **Environment**: `Python 3`
- **Region**: Select your closest region
- **Branch**: `main`

### Build & Start Commands
- **Build Command**: 
  ```
  cd backend && pip install -r requirements-prod.txt
  ```

- **Start Command**: 
  ```
  cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT
  ```

### Python Version
- Scroll to **"Environment"** section
- Add environment variable:
  - Key: `PYTHON_VERSION`
  - Value: `3.11.7`

## Step 4: Add Environment Variables

In Render dashboard, add these in **"Environment"** section:

```
DATABASE_URL=postgresql://user:password@host:5432/dbname
SECRET_KEY=your-secret-key-generate-one
API_KEY=your-api-key
THINGSPEAK_API_KEY=your-thingspeak-key
ALLOWED_ORIGINS=http://localhost:3000,https://your-frontend-url.onrender.com
ENVIRONMENT=production
```

## Step 5: Deploy
- Click **"Create Web Service"**
- Wait for deployment (3-5 minutes)
- Once deployed, you'll get a URL like: `https://cap-water-tank-api.onrender.com`

## Step 6: Test Your API
```bash
# Test if API is running
curl https://cap-water-tank-api.onrender.com/api/health

# Or in PowerShell
Invoke-WebRequest https://cap-water-tank-api.onrender.com/api/health
```

## Step 7: Update Frontend Config
Edit `frontend/src/config.js`:
```javascript
const config = {
  COLLEGE_NAME: 'IIIT',
  API_BASE_URL: 'https://cap-water-tank-api.onrender.com'
};

export default config;
```

Then push:
```bash
git add frontend/src/config.js
git commit -m "Update API URL to Render deployment"
git push
```

## Common Issues

### Build Fails: "No matching distribution for tensorflow"
✅ **Solution**: Use `requirements-prod.txt` instead (done!)

### 503 Service Unavailable
- Check database connection
- Verify DATABASE_URL environment variable
- Check Render logs for errors

### CORS Errors
- Update ALLOWED_ORIGINS with your frontend URL
- Restart service after updating

### Cold Start (First Request Slow)
- Normal on free tier
- API will sleep after 15 min of inactivity
- First request wakes it up (takes 30 seconds)

## Monitoring
- Go to Render dashboard
- Click your service name
- View **"Logs"** tab for real-time output
- Check **"Metrics"** for CPU/Memory usage

## Next Steps After Deployment
1. Deploy frontend on Render Static Site
2. Test full application
3. Set up database backups
4. Configure custom domain (optional)
