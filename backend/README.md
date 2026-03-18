# Water Level Monitoring System - Setup Guide

## 📁 3 Files Explained (Simple)

```
Your Project
├── main.py          → DATABASE (saves water sensor data)
├── thingspeak.py    → API CLIENT (gets data from ThingSpeak)
└── sync.py          → SERVER (connects them + auto-uploads)
```

### Why 3 Files?
- **Separation = Easy to Fix & Update**
- If database breaks → fix main.py only
- If ThingSpeak API changes → fix thingspeak.py only
- Server logic stays in sync.py

---

## 🚀 How to Run

### **Option 1: Auto-Upload Server (RECOMMENDED)**
Automatically fetches & stores data every 60 seconds:

```powershell
cd "C:\Users\kurra\vs code\abhishek\IIIT PROJECT\backend"
& ".\.venv\Scripts\python.exe" sync.py
```

What happens:
- ✅ Connects to ThingSpeak
- ✅ Gets latest sensor data
- ✅ Saves to database
- ✅ Waits 60 seconds
- ✅ Repeats

Press `Ctrl+C` to stop.

### **Option 2: One-Time Fetch**
```powershell
cd "C:\Users\kurra\vs code\abhishek\IIIT PROJECT\backend"
& ".\.venv\Scripts\python.exe" -c "from sync import fetch_and_store_latest; fetch_and_store_latest()"
```

---

## 🔄 Data Flow

```
ThingSpeak (Cloud)
      ↓
thingspeak.py (fetch)
      ↓
sync.py (organize)
      ↓
main.py (store)
      ↓
PostgreSQL Database
```

---

## 📊 Check Your Data

**See latest data in database:**
```powershell
cd "C:\Users\kurra\vs code\abhishek\IIIT PROJECT\backend"
& ".\.venv\Scripts\python.exe" -c "
from main import get_latest_sensor_data
data = get_latest_sensor_data()
print(f'Temperature: {data[\"temperature\"]}°C')
print(f'Water Level: {data[\"water_percentage\"]}%')
print(f'Distance: {data[\"distance\"]}')
print(f'Water Liters: {data[\"water_liters\"]}L')
"
```

---

## 📋 What's in Each File

| File | Purpose | Key Functions |
|------|---------|---|
| **main.py** | Database Connection & Storage | `get_connection()`, `insert_sensor_data()`, `get_latest_sensor_data()` |
| **thingspeak.py** | ThingSpeak API Client | `ThingSpeakClient.get_latest_data()`, `get_multiple_data()` |
| **sync.py** | Integration & Auto-Upload | `fetch_and_store_latest()`, `continuous_sync()` |

---

## ✅ What's Working

- ✅ ThingSpeak API connection
- ✅ Database storage
- ✅ Auto-upload every 60 seconds
- ✅ Data persistence

---

## 🎯 Next Steps

Choose one:

1. **REST API** - Access data via HTTP `GET /sensor/latest`
2. **Dashboard** - Visual charts & graphs
3. **Alerts** - Notify when water level is low
4. **Change sync interval** - Edit `sync.py` line at bottom: `continuous_sync(interval=30)  # 30 seconds`

---

## � Deploy to Render

### **Prerequisites**
- GitHub account with repository pushed
- Render.com account (free tier available)
- PostgreSQL database URL (from Aiven or similar)
- ThingSpeak API key

### **Step 1: Prepare for Deployment**

Ensure your repository has these files:
- `main.py` - FastAPI application
- `requirements.txt` - All dependencies
- `Procfile` - Process file for Render (example: `web: uvicorn main:app --host 0.0.0.0 --port $PORT`)
- `render.yaml` - Render deployment config
- `.env` - Environment variables (NOT pushed to GitHub, set on Render instead)

### **Step 2: Create Render Web Service**

1. Go to [render.com](https://render.com)
2. Click **New +** → **Web Service**
3. Connect your GitHub repository
4. Fill in details:
   - **Name:** `cap-iiit-backend` (or your preferred name)
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`

### **Step 3: Add Environment Variables**

In Render dashboard under **Environment**:
```
DATABASE_URL=postgresql://user:password@host/dbname
THINGSPEAK_API_KEY=AWP8F08WA7SLO5EQ
THINGSPEAK_CHANNEL_ID=3290444
```

Get `DATABASE_URL` from your PostgreSQL provider (Aiven, AWS RDS, etc.)

### **Step 4: Deploy**

1. Click **Create Web Service**
2. Render will automatically build and deploy
3. Wait for deployment to complete (2-5 minutes)
4. Your backend will be live at: `https://your-app-name.onrender.com`

### **Step 5: Verify Deployment**

Check if backend is running:
```
GET https://your-app-name.onrender.com/status
```

Expected response:
```json
{
  "status": "ok",
  "database": "connected",
  "model_loaded": true
}
```

### **Step 6: Access API Documentation**

Once deployed, view interactive API docs:
```
https://your-app-name.onrender.com/docs
```

### **Common Issues & Solutions**

**Deployment fails with "Build command failed"**
- Check `requirements.txt` is correct
- Run locally: `pip install -r requirements.txt`
- Push fix to GitHub and redeploy

**"Database connection refused"**
- Verify `DATABASE_URL` in Render environment variables
- Add your Render IP to database whitelist (if using external DB)
- Check database is running and accessible

**API returns 502 Bad Gateway**
- Check Render logs: Dashboard → Service → Logs
- Ensure `main.py` starts correctly
- Verify `uvicorn` is specified in `requirements.txt`

**Environment variables not working**
- Restart the service after adding variables
- Use `Ctrl+C` and redeploy from Render dashboard

### **Auto-Deploy on GitHub Push**

Render automatically redeploys when you:
1. Push changes to GitHub (default branch)
2. Changes are detected automatically
3. New build starts and deploys

To disable auto-deploy:
- Dashboard → **Settings** → Toggle **Auto-Deploy** OFF

---

## �🐛 Troubleshooting

**"ModuleNotFoundError: requests"**
```powershell
pip install requests
```

**"Can't connect to database"**
- Check `.env` file has correct credentials
- Verify PostgreSQL server is running

**"No data from ThingSpeak"**
- Check API key in `thingspeak.py` is correct
- Check internet connection

---

## 📝 Credentials

- **ThingSpeak Channel:** 3290444
- **ThingSpeak API Key:** AWP8F08WA7SLO5EQ
- **Database:** PostgreSQL on Aiven Cloud
- **Table:** `sensor_data`

---

That's it! Your system is ready to go! 🎉
