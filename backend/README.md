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

## 🐛 Troubleshooting

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
