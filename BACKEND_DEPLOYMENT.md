# Backend Deployment Guide

Step-by-step guide for deploying the FastAPI backend to Render with PostgreSQL database.

## 📋 Prerequisites

- GitHub account with the code repository
- Render account (https://render.com)
- PostgreSQL database (will create on Render)
- Backend code in `backend/` directory

## 🎯 Step-by-Step Deployment

### Step 1: Create PostgreSQL Database

1. Log in to [Render Dashboard](https://dashboard.render.com)
2. Click **New +** button
3. Select **PostgreSQL**
4. Fill in:
   - **Name**: `iot-water-tank-db`
   - **Region**: Select closest to your location
   - **PostgreSQL Version**: Latest (15+)
5. Click **Create Database**
6. **Save your database credentials** (you'll need them):
   - Host
   - Port (usually 5432)
   - Database name
   - User
   - Password

### Step 2: Create Web Service

1. Click **New +** button again
2. Select **Web Service**
3. Click **Build and deploy from a Git repository**
4. Click **Connect a repository**
5. Select **GitHub** and authorize Render
6. Choose your repository: `klb2006/IOT-TASK-LEELA`
7. Click **Connect**

### Step 3: Configure Web Service

| Setting | Value |
|---------|-------|
| **Name** | `iot-water-tank-backend` |
| **Branch** | `main` |
| **Runtime** | `Python 3.11` |
| **Build Command** | `cd backend && pip install --no-cache-dir -r requirements.txt` |
| **Start Command** | `cd backend && python run.py` |
| **Region** | Same as database |

### Step 4: Configure Environment Variables

1. Go to **Environment** tab
2. Click **Add Environment Variable**
3. Add each variable (from database created earlier):

```
DATABASE_URL=postgresql://user:password@host:port/database_name
API_PORT=8000
FRONTEND_URL=https://your-frontend-url.onrender.com
DB_HOST=<database_host>
DB_PORT=5432
DB_NAME=<database_name>
DB_USER=<database_user>
DB_PASSWORD=<database_password>
```

**Replace placeholder values:**
- `user`, `password`, `host`, `port`, `database_name` from your PostgreSQL service
- `your-frontend-url` with your frontend Render URL (or set later)

### Step 5: Deploy

1. Click **Create Web Service**
2. Render will start building (watch the logs)
3. Wait for deployment to complete
4. Check if service is running (green "Live" indicator)

## 📍 Getting Your Backend URL

After deployment:
1. Go to Render Dashboard → Web Services
2. Click on your `iot-water-tank-backend` service
3. Copy the URL (e.g., `https://iot-water-tank-backend.onrender.com`)

**Use this URL in your frontend!**

## ✅ Testing Backend

### Check Service Health

```bash
curl https://your-backend-url.onrender.com/api/v1/status
```

Should return:
```json
{
  "status": "healthy",
  "database": "connected"
}
```

### View API Documentation

Visit: `https://your-backend-url.onrender.com/docs`

## 🔧 Important Configuration

### Start Command Details

```bash
cd backend && python run.py
```

This assumes `run.py` contains:
```python
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
```

If your setup is different, update the **Start Command**.

### Update Frontend CORS

After backend is deployed:
1. Update `main.py` CORS settings:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://your-frontend-url.onrender.com",
        "http://localhost:3000"  # Keep for local development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

2. Push changes to GitHub
3. Render will automatically rebuild and deploy

## 📊 Database Operations

### Connect to Database

Using `psql`:
```bash
psql postgresql://user:password@host:port/database_name
```

Using Python:
```python
import psycopg2

conn = psycopg2.connect(
    host="your-db-host",
    port=5432,
    database="your-db-name",
    user="your-db-user",
    password="your-db-password"
)
```

### Initialize Database Schema

If you need to run migrations:
```bash
# Add to requirements.txt if not present
alembic==1.12.0

# Create migrations in backend/alembic/
# Run migrations: alembic upgrade head
```

## 🔍 Monitoring & Debugging

### View Logs

1. Render Dashboard → Your Web Service
2. Click **Logs** tab
3. Scroll to see recent activity and errors

### Common Issues

**Port Already in Use:**
- Solution: Ensure `port=8000` in start command, not hardcoded elsewhere

**Database Connection Failed:**
- Check `DATABASE_URL` format: `postgresql://user:pass@host:port/dbname`
- Verify database is running (check Render PostgreSQL service)

**ModuleNotFoundError:**
- Rebuild command broken
- Solution: Check `build_command` paths and `requirements.txt`

**Timeout Errors:**
- Cold start - Render free tier takes longer
- Solution: Use paid tier or wait for free tier to warm up

### Clear Cache & Redeploy

1. Render Dashboard → Your Service
2. Click **Settings**
3. Scroll to **Deploy Hooks** or **Clear Build Cache**
4. Redeploy with fresh build

## 🚀 Optimization

### Reduce Build Time

Use `requirements-prod.txt` without ML libraries for faster builds:

Update **Build Command**:
```bash
cd backend && pip install --no-cache-dir -r requirements-prod.txt
```

### Free Tier Considerations

- Services sleep after 15 minutes of inactivity
- Data is persistent (won't lose database)
- First request after sleep takes longer (cold start)
- For production, upgrade to paid Render plan

## 📋 Deployment Checklist

- [ ] PostgreSQL database created on Render
- [ ] Database credentials saved securely
- [ ] Web Service created and connected to GitHub
- [ ] Build Command: `cd backend && pip install --no-cache-dir -r requirements.txt`
- [ ] Start Command: `cd backend && python run.py`
- [ ] DATABASE_URL environment variable set
- [ ] Frontend URL environment variable set
- [ ] Build completes successfully
- [ ] Service shows "Live" (green indicator)
- [ ] `/api/v1/status` endpoint returns healthy
- [ ] API docs accessible at `/docs`
- [ ] No errors in Render logs

## 🔄 Updating Backend

When you push changes to GitHub:

1. Render automatically detects changes
2. Starts new build (logs visible in Render Dashboard)
3. Deploys if build succeeds
4. Zero-downtime deployment

Manual redeploy:
1. Render Dashboard → Select your service
2. Click **Deploys** tab
3. Click **Deploy latest** on any commit

## 📞 Need Help?

- Check [Render Documentation](https://render.com/docs)
- View logs in Render Dashboard
- Verify locally: `python run.py` works
- Test API with Swagger at `/docs`

## ✨ Next Steps

1. **Update Frontend** - Set `VITE_API_URL` to your backend URL
2. **Update CORS** - Add your frontend URL to backend CORS settings
3. **Test End-to-End** - Verify frontend can reach backend
4. **Monitor Logs** - Watch Render logs for any errors
5. **Set Alerts** - Configure Render notifications (paid plans)

## 🎯 Expected Response Times

After deployment (first request may be slow):
- Subsequent requests: ~100-500ms
- Database queries: ~50-200ms
- Total API response: <1s

If consistently slow:
- Check database connection
- Monitor Render CPU/Memory usage
- Consider upgrading plan
