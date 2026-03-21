# 📖 Swagger UI Documentation - Complete Guide

## 🎯 What is This Page?

```
http://127.0.0.1:8000/docs
```

This is **Swagger UI** - an **interactive API documentation** tool that comes built-in with FastAPI. It's like a **browser-based API testing tool** (similar to Postman, but built-in).

---

## 🔗 URL Breakdown

```
http://127.0.0.1:8000/docs#/default/predict_water_level_api_v1_predict_post
│        │         │    │      │                                          │
│        │         │    │      └──────────────── Endpoint ID #hash
│        │         │    └────────────────────── /docs page
│        │         └─────────────────────────── Port 8000
│        └──────────────────────────────────── localhost
└────────────────────────────────────────────── HTTP protocol
```

**Meaning:**
- `127.0.0.1:8000` = Your API server running locally
- `/docs` = Swagger UI documentation page
- `#/default/predict_water_level_...` = Direct link to the `/api/v1/predict` endpoint

---

## 🚀 How to Access the Swagger UI

### Step 1: Start API Server

```powershell
cd "C:\Users\kurra\vs code\abhishek\IIIT PROJECT\backend"
& ".\.venv\Scripts\python.exe" -m uvicorn main:app --reload
```

Wait for the output:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### Step 2: Open in Browser

Visit: **`http://127.0.0.1:8000/docs`**

You should see the **Swagger UI page** with all your endpoints listed. ✅

---

## 📋 What You See on the Page

The Swagger UI page shows:

```
┌─────────────────────────────────────────────────────────┐
│  Water Tank Monitoring System v1.0                      │
├─────────────────────────────────────────────────────────┤
│ BASE URL: http://127.0.0.1:8000                        │
├─────────────────────────────────────────────────────────┤
│ [GET]  /api/v1/status                                 │
│ [GET]  /api/v1/sensor/latest                          │
│ [GET]  /api/v1/sensor/history                         │
│ [POST] /api/v1/predict                      ← YOU'RE HERE
│ [GET]  /api/v1/model-info                             │
│ [GET]  /api/v1/predictions/history                    │
│ [POST] /api/v1/test                                   │
└─────────────────────────────────────────────────────────┘
```

---

## 🧪 Testing the Prediction Endpoint

### What You Can Do:

The Swagger UI allows you to **test API endpoints directly from the browser** without needing Postman or writing code.

### Step-by-Step Instructions:

#### 1️⃣ Find the Endpoint
On the Swagger UI page, look for:
```
POST /api/v1/predict
  Predict water tank level using ML model
```

Click on it to expand:
```
▼ POST /api/v1/predict
  Predict water tank level using ML model
  
  Parameters: (none)
  Request body: 
    {
      "distance": 24.0,
      "temperature": 30.25,
      "water_percent": 85.0,
      "node_id": "node-1"
    }
```

#### 2️⃣ Click "Try it out" Button
- You'll see a blue button labeled **"Try it out"**
- Click it to enable the request editor

#### 3️⃣ Enter Request Data
A form will appear. Enter this data:

```json
{
  "distance": 24,
  "temperature": 30,
  "water_percent": 85,
  "node_id": "node-1"
}
```

#### 4️⃣ Click "Execute" Button
- The request will be sent to your API
- You'll see the response immediately

#### 5️⃣ See the Response
You'll see:
```json
{
  "status": "success",
  "prediction": "LOW",
  "confidence": 0.6112,
  "input": {
    "distance": 24,
    "temperature": 30,
    "water_percent": 85
  },
  "timestamp": "2026-03-16T12:03:41.266761"
}
```

---

## 📊 Example: Testing Different Endpoints

### Test 1: Get Model Info

**Endpoint:** `GET /api/v1/model-info`

Steps:
1. Find the endpoint in the list
2. Click "Try it out"
3. Click "Execute"
4. See response with model details

**Response:**
```json
{
  "status": "success",
  "model_info": {
    "model_type": "Water Tank Level Prediction Model",
    "version": "1.0",
    "input_features": ["distance", "temperature", "water_percent"],
    "output_classes": ["LOW", "MEDIUM", "HIGH", "FULL"],
    "accuracy": 0.85,
    "last_trained": "2026-03-10"
  }
}
```

---

### Test 2: Get Prediction History

**Endpoint:** `GET /api/v1/predictions/history`

Steps:
1. Find the endpoint
2. Click "Try it out"
3. (Optional) Set `limit=100`
4. Click "Execute"
5. See all past predictions

**Response:**
```json
{
  "status": "success",
  "count": 3,
  "data": [
    {
      "id": 1,
      "node_id": "node-1",
      "distance": 24.0,
      "temperature": 30,
      "water_percent": 85,
      "prediction": "LOW",
      "confidence": 0.6112,
      "created_at": "2026-03-16T06:33:40.632194"
    },
    ...
  ]
}
```

---

### Test 3: Get API Status

**Endpoint:** `GET /api/v1/status`

Steps:
1. Find the endpoint
2. Click "Try it out"
3. Click "Execute"
4. See if everything is connected

**Response:**
```json
{
  "status": "running",
  "model_loaded": true,
  "database": "connected",
  "timestamp": "2026-03-16T12:04:42.862877"
}
```

---

## ✅ Benefits of Swagger UI

| Feature | Benefit |
|---------|---------|
| **Interactive Testing** | Test endpoints without Postman or code |
| **Auto Documentation** | Always shows current API endpoint specs |
| **Request Builder** | Form-based request creation |
| **Response Viewer** | Shows responses with syntax highlighting |
| **Parameter Validation** | Shows required fields and data types |
| **Schema Display** | Shows request/response JSON structure |
| **HTTP Status Codes** | Shows what each response code means |
| **No Setup Needed** | Works out-of-the-box with FastAPI |

---

## 📝 Understanding the Request/Response Section

### Request Section Shows:
```
Method:    POST (or GET, etc.)
Path:      /api/v1/predict
Parameters:  (any URL parameters)
Request Body: (JSON structure expected)
  - distance (float, required)
  - temperature (float, required)
  - water_percent (float, required)
  - node_id (string, optional)
```

### Response Section Shows:
```
Success Response (200):
  {
    "status": "success",
    "prediction": "LOW",
    "confidence": 0.6112,
    "timestamp": "..."
  }

Error Response (400):
  {
    "detail": "Invalid input"
  }
```

---

## 🎯 Alternative: Other Documentation Pages

FastAPI provides two auto-generated docs pages:

### 1. Swagger UI (Interactive)
```
http://127.0.0.1:8000/docs
```
- **Better for:** Testing endpoints, visual interface
- **Features:** Try it out, request builder, response viewer

### 2. ReDoc (API Reference)
```
http://127.0.0.1:8000/redoc
```
- **Better for:** Reading documentation, static reference
- **Features:** Clean, organized, read-only

---

## 📸 Screenshots for Assignment

### Screenshot 1: Swagger UI Main Page
Visit `http://127.0.0.1:8000/docs`

Take screenshot showing:
- List of all endpoints
- API title and version
- Base URL

### Screenshot 2: Expanded Prediction Endpoint
On the same page:
- Click on `POST /api/v1/predict`
- Expand it
- Show the request body schema

Take screenshot showing:
- Endpoint description
- Required parameters
- Request/Response schema

### Screenshot 3: Test Response
After clicking "Execute":

Take screenshot showing:
- Request sent
- Response received
- Prediction result
- Confidence score

---

## 💡 Tips & Tricks

### ✅ DO:
- Use Swagger UI to test during development
- Check response status codes
- Verify exact request/response formats
- Test different input values
- Check error messages

### ❌ DON'T:
- Rely only on Swagger UI for documentation (use comments in code too)
- Use Swagger for load testing (it's single-threaded)
- Expose `/docs` on public APIs (for security)

---

## 🔒 Production Note

In production, you might **disable** Swagger UI:

```python
# In main.py
app = FastAPI(
    docs_url=None,  # Disable /docs
    redoc_url=None  # Disable /redoc
)
```

But for development and testing, it's **extremely useful**! ✅

---

## 📚 Quick Reference

| URL | Purpose |
|-----|---------|
| `http://127.0.0.1:8000/` | API root (welcome page) |
| `http://127.0.0.1:8000/docs` | **Swagger UI (interactive testing)** ← USE THIS |
| `http://127.0.0.1:8000/redoc` | ReDoc (static documentation) |
| `http://127.0.0.1:8000/api/v1/predict` | Actual API endpoint (POST request) |
| `http://127.0.0.1:8000/api/v1/model-info` | Model info endpoint (GET request) |

---

## 🎉 Summary

The `/docs` page is your **personal Postman** that comes with FastAPI!

**To test your APIs:**
1. Start server: `uvicorn main:app --reload`
2. Open: `http://127.0.0.1:8000/docs`
3. Find endpoint
4. Click "Try it out"
5. Enter test data
6. Click "Execute"
7. See response instantly ✓

**No additional tools needed!** 🚀

---

## 🎯 For Your Assignment:

**Take these 3 screenshots:**

1. **Swagger UI home page** - Shows all endpoints list
2. **Expanded `/api/v1/predict` endpoint** - Shows request/response schema
3. **Test result** - Shows "Try it out" with response data

**This proves:**
✅ Task 2.1 - Prediction API endpoint works
✅ Task 2.2 - Model Info API endpoint works  
✅ Task 2.3 - Predictions stored in database

All in one place! 🎉
