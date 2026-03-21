# Frontend Activity Predictions - Setup Complete ✅

## 🔄 Complete Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│                                                              │
│  THINGSPEAK → DATABASE → BACKEND API → FRONTEND DISPLAY    │
│                                                              │
└─────────────────────────────────────────────────────────────┘

Step 1: IoT Device (ESP32)
├── Reads ultrasonic sensor (distance cm)
├── Reads temperature sensor (°C)
└── Sends to backend: POST /api/v1/predict-activity

Step 2: Backend Processing
├── Receives: {distance, temperature, node_id}
├── Loads GRU model (model32.h5)
├── Predicts activity: filling, flush, washing_machine, geyser, no_activity
├── Stores prediction in PostgreSQL database
└── Returns: {activity, confidence, probabilities, ...}

Step 3: Frontend Display
├── Calls: GET /api/v1/activity-model-info (model details)
├── Calls: GET /api/v1/predictions/history (past predictions)
├── User enters: distance + temperature
├── Calls: POST /api/v1/predict-activity (real-time prediction)
└── Displays: Activity name, confidence, probability breakdown
```

---

## 📱 What Changed in Frontend

### Updated Files:

1. **src/utils/api.js**
   - Added: `predictActivity()` endpoint for GRU model
   - Added: `getActivityModelInfo()` to fetch model metadata
   - Updated: Correct endpoint paths

2. **src/config.js**
   - Updated: `PREDICTION_CLASSES` → ['no_activity', 'filling', 'flush', 'washing_machine', 'geyser']
   - Added: `ACTIVITY_DESCRIPTIONS` for each activity type

3. **src/pages/Prediction.js**
   - **NEW**: `getActivityColor()` function to color-code activities
   - **Updated**: Form now only needs distance + temperature (not water_percent)
   - **Updated**: `handlePredict()` calls `/api/v1/predict-activity` endpoint
   - **Updated**: Results display activity description + breakdown
   - **NEW**: Probability bars showing confidence for each activity
   - **Updated**: Model info shows GRU details + 5 activity types
   - **NEW**: Auto-refreshes prediction history every 10 seconds

4. **src/styles/Prediction.css**
   - **NEW**: `.activity-description` - styled description text
   - **NEW**: `.probabilities-section` - probability breakdown display
   - **NEW**: `.probability-bars` - visual confidence bars
   - **NEW**: `.activity-tag` - colored activity badges
   - **NEW**: `.activities-list` - list of supported activities

---

## 🎯 Prediction Page Features

### Input Section
```
Distance (cm): [___] ← From ultrasonic sensor
Temperature (°C): [___] ← From temperature sensor
Node ID: [node-1] ← Device identifier

[MAKE PREDICTION] Button
```

### Results Section (After Prediction)
```
📊 Prediction Results

Detected Activity: [FILLING] (Blue badge)
"Water is being added to tank (pump running)"

Confidence: [████████░░] 85%
Distance Reading: 50.00 cm
Temperature: 28.5 °C
Confidence Score: 85.0%
Time: 14:30:45

Activity Probabilities:
├── no_activity: [░░░░░░░░░░] 5%
├── filling: [████████████████████] 85%
├── flush: [███░░░░░░░] 3%
├── washing_machine: [██░░░░░░░░] 2%
└── geyser: [█░░░░░░░░░] 1%
```

### Model Info Card
```
🤖 Activity Model Info

Model Type: GRU Neural Network (model32.h5)
Accuracy: 85.95%
F1-Score: 0.6881
Activities: 5 classes

Detected Activities:
[no_activity] [filling] [flush] [washing_machine] [geyser]
```

---

## 🔄 Real-Time Updates

The Prediction page now:
1. ✅ Auto-fetches model info on load
2. ✅ Auto-refreshes prediction history every 10 seconds
3. ✅ Stores all predictions in PostgreSQL
4. ✅ Displays real predictions from backend API
5. ✅ Shows confidence breakdown for each activity

---

## 🎨 Activity Colors

Each activity has a unique color for easy identification:

| Activity | Color | Meaning |
|----------|-------|---------|
| **no_activity** | Gray (#6B7280) | Tank is idle |
| **filling** | Blue (#3B82F6) | Water being added |
| **flush** | Red (#EF4444) | Rapid water removal |
| **washing_machine** | Amber (#F59E0B) | Extended usage |
| **geyser** | Pink (#EC4899) | Hot water system |

---

## 📊 Activity Descriptions

Users see helpful descriptions for each predicted activity:

- **no_activity**: "Tank is idle - no water usage detected"
- **filling**: "Water is being added to tank (pump running)"
- **flush**: "Rapid water removal detected (toilet flush)"
- **washing_machine**: "Extended water usage pattern detected"
- **geyser**: "Hot water system usage detected"

---

## 🧪 How to Test

### 1. Backend Must be Running
```bash
python backend/main.py
# Should show: "[OK] API Server ready!"
```

### 2. Frontend Must Know Backend URL
In `src/config.js`:
```javascript
API_BASE_URL: process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000'
```

### 3. Test in Frontend
1. Go to Prediction page
2. Model info should load automatically
3. Enter sample values:
   - Distance: 50
   - Temperature: 28.5
4. Click "MAKE PREDICTION"
5. See activity result with confidence bars

### 4. Verify Database Storage
```bash
# Connect to PostgreSQL
psql -h localhost -U your_user -d your_db

# Check predictions table
SELECT * FROM predictions 
ORDER BY created_at DESC 
LIMIT 5;
```

---

## 🚀 Frontend to Backend Endpoints

### Get Model Information
```
GET /api/v1/activity-model-info

Response:
{
  "status": "success",
  "model": {
    "model": "GRU (model32.h5)",
    "accuracy": "85.95%",
    "f1_score": "0.6881",
    "activities": ["no_activity", "filling", "flush", "washing_machine", "geyser"],
    "num_classes": 5
  }
}
```

### Make Prediction
```
POST /api/v1/predict-activity

Request:
{
  "distance": 50.0,
  "temperature": 28.5,
  "node_id": "node-1"
}

Response:
{
  "status": "success",
  "activity": "filling",
  "confidence": 0.89,
  "distance": 50.0,
  "temperature": 28.5,
  "probabilities": {
    "no_activity": 0.05,
    "filling": 0.89,
    "flush": 0.03,
    "washing_machine": 0.02,
    "geyser": 0.01
  },
  "node_id": "node-1",
  "timestamp": "2024-03-21T14:30:00"
}
```

### Get Prediction History
```
GET /api/v1/predictions/history?limit=100

Response:
{
  "status": "success",
  "count": 50,
  "data": [
    {
      "id": 1,
      "node_id": "node-1",
      "distance": 50.0,
      "temperature": 28.5,
      "prediction": "filling",
      "confidence": 0.89,
      "created_at": "2024-03-21T14:30:00"
    },
    ...
  ]
}
```

---

## 📈 Database Schema

### predictions Table
```sql
CREATE TABLE predictions (
  id SERIAL PRIMARY KEY,
  node_id VARCHAR(255),
  distance FLOAT,
  temperature FLOAT,
  water_percent FLOAT,
  prediction VARCHAR(255),     ← Activity name
  confidence FLOAT,            ← Confidence 0-1
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 🔍 Frontend Component Flow

```
Prediction.js
├── useEffect (on mount)
│   ├── fetchModelInfo() → GET /api/v1/activity-model-info
│   ├── fetchPredictionHistory() → GET /api/v1/predictions/history
│   └── setInterval(fetchPredictionHistory, 10000)
│
├── Input Form
│   ├── distance input
│   ├── temperature input
│   └── node_id input
│
├── handlePredict() (on form submit)
│   ├── validateInputs()
│   ├── POST /api/v1/predict-activity
│   ├── setPrediction(response.data)
│   └── fetchPredictionHistory()
│
└── Render Results
    ├── Activity Badge (colored)
    ├── Activity Description
    ├── Confidence Gauge
    └── Probability Bars
```

---

## ✨ Key Features Added

### 1. Real Activity Classification
- Uses actual GRU model (model32.h5) from Colab
- 5 different water activities
- 85.95% accuracy

### 2. Confidence Breakdown
- Shows probability for each activity
- Visual bars for easy comparison
- High confidence = more reliable prediction

### 3. Activity Descriptions
- User-friendly explanations
- Tells what each activity means
- Helps understand predictions

### 4. Auto-Refresh History
- Prediction history updates every 10 seconds
- Always shows latest data
- No manual refresh needed

### 5. Real Database Storage
- Every prediction saved to PostgreSQL
- Query history anytime
- Track patterns over time

---

## 🎓 How Frontend Gets Real Predictions

1. **User enters sensor data** (distance, temperature)
2. **Frontend sends to backend**: POST /api/v1/predict-activity
3. **Backend loads model32.h5** and extracts features
4. **GRU model predicts** activity class + confidence
5. **Backend returns** prediction data
6. **Frontend displays** with color, description, and probability breakdown
7. **Prediction is saved** to database automatically
8. **History is updated** and displayed in page

---

## 📝 Configuration

All activity settings are in `src/config.js`:

```javascript
// Activity classes
PREDICTION_CLASSES: [
  'no_activity',
  'filling',
  'flush',
  'washing_machine',
  'geyser'
]

// Activity descriptions
ACTIVITY_DESCRIPTIONS: {
  'no_activity': 'Tank is idle - no water usage detected',
  'filling': 'Water is being added to tank (pump running)',
  // ... etc
}
```

---

## ✅ Frontend Is Ready!

Your Prediction page now:
- ✅ Calls real activity classification endpoint
- ✅ Shows GRU model metadata
- ✅ Displays predictions with confidence
- ✅ Shows probability breakdown
- ✅ Auto-updates history
- ✅ Stores to database
- ✅ Uses color-coded activities
- ✅ Shows activity descriptions

**Status**: Ready for production! 🚀

Just ensure:
1. `model32.h5` is in `backend/saved_models/`
2. Backend is running: `python backend/main.py`
3. Frontend points to correct API URL

---

Generated: 2024-03-21
