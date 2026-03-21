# 🎯 QUICK START - Activity Classification Integration

## ✅ What's Been Set Up

Your water tank monitoring system now has **real ML-based activity classification**!

### Files Created
1. ✅ **activity_classifier.py** - GRU model loader & predictor
2. ✅ **main.py updated** - New `/api/v1/predict-activity` endpoint  
3. ✅ **verify_setup.py** - Check if everything is configured
4. ✅ **Documentation**:
   - ACTIVITY_CLASSIFICATION_SETUP.md
   - SYSTEM_ARCHITECTURE.md
   - COLAB_INTEGRATION_GUIDE.md
   - MODEL_PRECISION_GUIDE.md

---

## 🚀 3-STEP SETUP

### Step 1: Copy Your Model (2 minutes)
```bash
# Copy model32.h5 from your downloads to:
backend/saved_models/model32.h5
```

### Step 2: Verify Installation (1 minute)
```bash
# In Windows PowerShell:
python verify_setup.py
```

Expected output:
```
✓ Model file found: backend/saved_models/model32.h5
✓ Classifier module found: backend/ml_training/activity_classifier.py
✓ Backend has /api/v1/predict-activity endpoint
✓ Activity classifier module loaded successfully
```

### Step 3: Start & Test (2 minutes)
```bash
# Terminal 1: Start backend
python backend/main.py

# Terminal 2: Test the endpoint
curl -X POST "http://127.0.0.1:8000/api/v1/predict-activity" \
  -H "Content-Type: application/json" \
  -d '{"distance": 50.0, "temperature": 28.0}'
```

Expected response:
```json
{
  "status": "success",
  "activity": "no_activity",
  "confidence": 0.85,
  "distance": 50.0,
  "temperature": 28.0,
  "timestamp": "2024-03-21T14:30:00"
}
```

---

## 📱 IoT Device Setup

Your ESP32 code **already has the correct endpoint**!

Just update the backend IP:

```cpp
// Line ~12 in your .ino file
#define BACKEND_SERVER "192.168.29.128"  // ← YOUR COMPUTER'S IP
#define BACKEND_PORT 8001
```

Then upload to ESP32 and check serial monitor:
```
Distance: 50 cm | Temp: 28 C | ...
Sending to backend API...
Backend API call complete
```

---

## 🤖 What the Model Does

Shows detected water activity every 20 seconds:

| Activity | What It Means |
|----------|--------------|
| **no_activity** | Tank idle, no water usage |
| **filling** | Pump adding water to tank |
| **flush** | Rapid water drain (toilet) |
| **washing_machine** | Extended usage pattern |
| **geyser** | Hot water system usage |

---

## 📊 Model Specifications

- **Type**: GRU (Gated Recurrent Unit) Neural Network
- **Trained on**: 42,028 labeled samples
- **Accuracy**: 85.95%
- **F1-Score**: 0.6881
- **Classes**: 5 water activities

---

## 📁 Where Files Are

```
backend/
├── saved_models/
│   └── model32.h5                    ← PLACE YOUR MODEL HERE
├── ml_training/
│   └── activity_classifier.py        ← CREATED FOR YOU
└── main.py                           ← UPDATED WITH NEW ENDPOINT
```

---

## 🧪 Testing Checklist

- [ ] model32.h5 placed in backend/saved_models/
- [ ] Run: `python verify_setup.py` (all checks pass)
- [ ] Run: `python backend/main.py` (shows "API Server ready!")
- [ ] Test API with curl command above
- [ ] Upload ESP32 code with correct IP
- [ ] Check serial monitor shows activity predictions

---

## 🔗 API Endpoints

### Activity Prediction (NEW)
```
POST /api/v1/predict-activity
Input: {"distance": 50.0, "temperature": 28.0}
Output: {"activity": "filling", "confidence": 0.89, ...}
```

### Model Info
```
GET /api/v1/activity-model-info
Output: {"model": "GRU", "accuracy": "85.95%", "activities": [...]}
```

### Prediction History
```
GET /api/v1/predictions/history?limit=100
Output: List of all predictions from database
```

---

## 🐛 Troubleshooting

**Problem**: Model not found
```
→ Check: ls backend/saved_models/model32.h5
→ Copy file if missing
```

**Problem**: Backend won't start
```
→ Check: python backend/main.py
→ Install missing packages: pip install -r backend/requirements.txt
```

**Problem**: ESP32 can't connect
```
→ Update: #define BACKEND_SERVER "YOUR_COMPUTER_IP"
→ Find IP: ipconfig (Windows) or ifconfig (Mac)
```

**Problem**: Low confidence predictions
```
→ Verify sensor is working: read distances change
→ Check: Collected data matches training data range
```

---

## 📖 Full Documentation

For detailed information, see:
- **Setup Guide**: [ACTIVITY_CLASSIFICATION_SETUP.md](ACTIVITY_CLASSIFICATION_SETUP.md)
- **System Architecture**: [SYSTEM_ARCHITECTURE.md](SYSTEM_ARCHITECTURE.md)
- **API Documentation**: `http://127.0.0.1:8000/docs` (when backend running)

---

## ✨ What You Can Do Now

1. **Monitor water activity** - See what water is being used for
2. **Detect patterns** - Identify peak usage times
3. **Spot anomalies** - Detect potential leaks
4. **Track trends** - Analyze usage over time
5. **Set alerts** - Notify when unusual patterns occur

---

## 🎓 How It Works (Simple Version)

```
ESP32 Sensor
    ↓
Reads distance (cm) & temperature (°C)
    ↓
Sends to Backend API
    ↓
Backend extracts features from sensor data
    ↓
GRU Model (trained in Colab) predicts activity
    ↓
Returns activity name & confidence
    ↓
Displayed in dashboard + saved to database
```

---

## 📞 Need Help?

Check these files in order:
1. **Setup issues**: ACTIVITY_CLASSIFICATION_SETUP.md
2. **System design**: SYSTEM_ARCHITECTURE.md
3. **Model metrics**: MODEL_PRECISION_GUIDE.md
4. **API errors**: Run `python backend/main.py` for verbose logs

---

**Status**: ✅ Ready to use!

Run: `python verify_setup.py` to check everything is configured correctly.

Then: Start backend with `python backend/main.py` and test the API!

---

Generated: 2024-03-21
Version: 1.0
