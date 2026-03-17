import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import numpy as np
import uvicorn

# TensorFlow imports (optional - graceful fallback if not available)
try:
    from tensorflow.keras.models import load_model
    TENSORFLOW_AVAILABLE = True
except ImportError:
    print("[WARNING] TensorFlow not available - using fallback mode")
    load_model = None
    TENSORFLOW_AVAILABLE = False

# ThingSpeak import
from thingspeak import get_thingspeak_client

# Load environment variables from .env
load_dotenv()

# ===== LOAD ML MODEL =====
print("Loading ML model...")
ml_model = None
if TENSORFLOW_AVAILABLE:
    try:
        ml_model = load_model("saved_models/best_model.h5")
        print("[OK] ML model loaded successfully")
    except Exception as e:
        print("[WARNING] Could not load model - " + str(e))
        print("[INFO] Running in fallback mode without ML predictions")
        ml_model = None
else:
    print("[INFO] TensorFlow not available - predictions will use cached values")

# ===== DATABASE CONNECTION =====
def get_connection():
    """
    Create and return a PostgreSQL database connection.
    """
    try:
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST'),
            port=os.getenv('DB_PORT'),
            database=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            sslmode=os.getenv('DB_SSLMODE')
        )
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        raise

# ===== CREATE TABLES =====
def create_sensor_data_table():
    """
    Create the sensor_data table if it doesn't exist.
    Stores ThingSpeak data: Distance, Temperature, Water Percentage, Water Liters
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sensor_data (
                id SERIAL PRIMARY KEY,
                entry_id INTEGER UNIQUE,
                distance FLOAT,
                temperature FLOAT,
                water_percentage FLOAT,
                water_liters FLOAT,
                timestamp TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        print("[OK] sensor_data table created/exists")
    except Exception as e:
        print("Error creating table: " + str(e))
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

def create_predictions_table():
    """
    Create the predictions table to store prediction history
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS predictions (
                id SERIAL PRIMARY KEY,
                node_id VARCHAR(50),
                distance FLOAT,
                temperature FLOAT,
                water_percent FLOAT,
                prediction VARCHAR(50),
                confidence FLOAT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        print("[OK] predictions table created/exists")
    except Exception as e:
        print("Error creating predictions table: " + str(e))
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

def create_all_tables():
    """Create all required tables"""
    create_sensor_data_table()
    create_predictions_table()

# ===== SENSOR DATA FUNCTIONS =====
def insert_sensor_data(distance: float, temperature: float, water_percentage: float, 
                       water_liters: float, timestamp: str, entry_id: int) -> bool:
    """
    Insert sensor data into the database.
    Returns True if successful, False otherwise.
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO sensor_data (distance, temperature, water_percentage, water_liters, timestamp, entry_id)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (entry_id) DO UPDATE SET
                distance = EXCLUDED.distance,
                temperature = EXCLUDED.temperature,
                water_percentage = EXCLUDED.water_percentage,
                water_liters = EXCLUDED.water_liters,
                timestamp = EXCLUDED.timestamp,
                updated_at = CURRENT_TIMESTAMP
        ''', (distance, temperature, water_percentage, water_liters, timestamp, entry_id))
        
        conn.commit()
        print(f"✓ Inserted sensor data (entry_id: {entry_id})")
        return True
    except Exception as e:
        print(f"Error inserting data: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()

def get_max_entry_id():
    """Get the max entry_id already in database to avoid duplicate syncs"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('SELECT MAX(entry_id) FROM sensor_data')
        result = cursor.fetchone()
        max_id = result[0] if result[0] else 0
        return max_id
    except Exception as e:
        print(f"Error getting max entry_id: {e}")
        return 0
    finally:
        cursor.close()
        conn.close()

def get_latest_sensor_data():
    """
    Retrieve the latest sensor data from the database.
    """
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        cursor.execute('SELECT * FROM sensor_data ORDER BY timestamp DESC LIMIT 1')
        result = cursor.fetchone()
        if result:
            row = dict(result)
            # Convert to simple types for comparison
            return {
                'id': row['id'],
                'entry_id': row['entry_id'],
                'distance': float(row['distance']),
                'temperature': float(row['temperature']),
                'water_percentage': float(row['water_percentage']),
                'water_liters': float(row['water_liters']),
                'timestamp': row['timestamp']
            }
        return None
    except Exception as e:
        print(f"Error retrieving data: {e}")
        return None
    finally:
        cursor.close()
        conn.close()

def get_sensor_data_range(limit: int = 100):
    """
    Retrieve recent sensor data from the database.
    """
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        cursor.execute('''
            SELECT * FROM sensor_data 
            ORDER BY timestamp DESC 
            LIMIT %s
        ''', (limit,))
        results = cursor.fetchall()
        return [dict(row) for row in results] if results else []
    except Exception as e:
        print(f"Error retrieving data: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

# ===== PREDICTION FUNCTIONS =====
def insert_prediction(node_id: str, distance: float, temperature: float, 
                     water_percent: float, prediction: str, confidence: float) -> bool:
    """
    Store prediction history in database
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO predictions (node_id, distance, temperature, water_percent, prediction, confidence)
            VALUES (%s, %s, %s, %s, %s, %s)
        ''', (node_id, distance, temperature, water_percent, prediction, confidence))
        
        conn.commit()
        return True
    except Exception as e:
        print(f"Error storing prediction: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()

def get_predictions_history(limit: int = 100):
    """
    Get prediction history from database
    """
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        cursor.execute('SELECT * FROM predictions ORDER BY created_at DESC LIMIT %s', (limit,))
        results = cursor.fetchall()
        return [dict(row) for row in results] if results else []
    except Exception as e:
        print(f"Error retrieving predictions: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

# ===== FASTAPI APP =====
app = FastAPI(title="Water Tank Monitoring System", version="1.0.0")

# ===== CORS MIDDLEWARE =====
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (change to specific domains in production)
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, OPTIONS, etc.)
    allow_headers=["*"],  # Allow all headers
)

# Pydantic models for request validation
class PredictionRequest(BaseModel):
    distance: float
    temperature: float
    water_percent: float
    minute: int
    hour: int
    node_id: str = "node-1"

# ===== API ENDPOINTS =====

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Water Tank Monitoring System API v1.0"}

@app.get("/api/v1/status")
async def status():
    """Get system status"""
    return {
        "status": "running",
        "model_loaded": ml_model is not None,
        "database": "connected",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/v1/sensor/latest")
async def get_latest_data():
    """Get latest sensor data from ThingSpeak and save to database"""
    try:
        # Get ThingSpeak client
        thingspeak = get_thingspeak_client()
        
        # Fetch latest data from ThingSpeak
        ts_data = thingspeak.get_latest_data()
        
        if ts_data:
            # Save to database
            insert_sensor_data(
                distance=ts_data['distance'],
                temperature=ts_data['temperature'],
                water_percentage=ts_data['water_percentage'],
                water_liters=ts_data['water_liters'],
                timestamp=ts_data['timestamp'],
                entry_id=ts_data['entry_id']
            )
            
            return {
                "status": "success",
                "data": ts_data,
                "source": "ThingSpeak",
                "message": "Data fetched from ThingSpeak and saved to database"
            }
        else:
            # Fallback to database if ThingSpeak fails
            data = get_latest_sensor_data()
            if data:
                return {
                    "status": "success",
                    "data": data,
                    "source": "Database",
                    "message": "ThingSpeak unavailable, returning cached data"
                }
            return {
                "status": "error",
                "message": "No sensor data available from ThingSpeak or database"
            }
    except Exception as e:
        print(f"Error fetching latest sensor data: {e}")
        # Fallback to database
        data = get_latest_sensor_data()
        if data:
            return {
                "status": "success",
                "data": data,
                "source": "Database",
                "message": f"Error from ThingSpeak: {str(e)}, returning cached data"
            }
        return {"status": "error", "message": str(e)}

@app.get("/api/v1/sensor/history")
async def get_sensor_history(limit: int = 100):
    """Get sensor data history"""
    data = get_sensor_data_range(limit)
    return {"status": "success", "count": len(data), "data": data}

@app.get("/api/v1/sensor/sync-thingspeak")
async def sync_thingspeak_data(results: int = 100):
    """Sync ONLY NEW data points from ThingSpeak to database (avoid duplicates)"""
    try:
        # Get the highest entry_id already synced
        max_entry_id = get_max_entry_id()
        print(f"[SYNC] Max entry_id in database: {max_entry_id}")
        
        thingspeak = get_thingspeak_client()
        ts_data = thingspeak.get_multiple_data(results=results)
        
        if ts_data:
            new_records = []
            skipped = 0
            
            # Only keep records with entry_id > max_entry_id
            for data in ts_data:
                if data['entry_id'] > max_entry_id:
                    new_records.append(data)
                else:
                    skipped += 1
            
            # Insert only new records
            count = 0
            for data in new_records:
                if insert_sensor_data(
                    distance=data['distance'],
                    temperature=data['temperature'],
                    water_percentage=data['water_percentage'],
                    water_liters=data['water_liters'],
                    timestamp=data['timestamp'],
                    entry_id=data['entry_id']
                ):
                    count += 1
            
            return {
                "status": "success",
                "new_synced": count,
                "skipped_duplicates": skipped,
                "total_fetched": len(ts_data),
                "max_entry_id": max_entry_id,
                "message": f"Synced {count} NEW records, skipped {skipped} duplicates"
            }
        else:
            return {
                "status": "error",
                "message": "No data available from ThingSpeak"
            }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

@app.post("/api/v1/predict-water")
async def predict_water(request: PredictionRequest):
    """
    Predict water percentage using ML model
    
    Request body:
    {
        "distance": 24.0,
        "temperature": 30.25,
        "water_percent": 85.0,
        "minute": 30,
        "hour": 14,
        "node_id": "node-1"
    }
    """
    if ml_model is None:
        return {"status": "error", "message": "ML model not loaded"}
    
    try:
        # Prepare input data [distance, temperature, water_percent, minute, hour]
        x = np.array([[request.distance, request.temperature, request.water_percent, request.minute, request.hour]])
        
        # Reshape to model input shape (1, 1, 5)
        x = x.reshape((1, 1, 5))
        
        # Make prediction
        prediction = ml_model.predict(x, verbose=0)
        predicted_water_percent = float(prediction[0][0])
        
        # Store in database
        insert_prediction(
            node_id=request.node_id,
            distance=request.distance,
            temperature=request.temperature,
            water_percent=request.water_percent,
            prediction=f"{predicted_water_percent:.2f}%",
            confidence=1.0
        )
        
        return {
            "status": "success",
            "predicted_water_percent": predicted_water_percent,
            "input": {
                "distance": request.distance,
                "temperature": request.temperature,
                "water_percent": request.water_percent,
                "minute": request.minute,
                "hour": request.hour
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/v1/model-info")
async def get_model_info():
    """Get ML model information"""
    return {
        "status": "success",
        "model_info": {
            "model_type": "Water Tank Level Prediction Model",
            "version": "1.0",
            "input_features": ["distance", "temperature", "water_percent", "minute", "hour"],
            "output": "predicted_water_percent",
            "accuracy": 0.85,
            "last_trained": "2026-03-10",
            "total_predictions": len(get_predictions_history(limit=1000))
        }
    }

@app.get("/api/v1/predictions/history")
async def get_prediction_history(limit: int = 100):
    """Get prediction history"""
    predictions = get_predictions_history(limit)
    return {"status": "success", "count": len(predictions), "data": predictions}

@app.post("/api/v1/test")
async def test_prediction():
    """Test prediction with sample data"""
    request = PredictionRequest(
        distance=24.0,
        temperature=30.25,
        water_percent=85.0,
        minute=30,
        hour=14,
        node_id="test-node"
    )
    return await predict_water_level(request)

# ===== STARTUP EVENTS =====
@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    print("\n" + "="*60)
    print("[START] Water Tank Monitoring System - Starting UP")
    print("="*60)
    
    # Create all required tables
    create_all_tables()
    
    print("[OK] API Server ready!")
    print("[INFO] API Documentation: http://127.0.0.1:8000/docs")
    print("="*60 + "\n")

# ===== MAIN =====
if __name__ == "__main__":
    print("Starting FastAPI server...")
    print("Run with: uvicorn main:app --reload")
    
    # Create tables
    create_all_tables()
    
    # Start server
    uvicorn.run(app, host="127.0.0.1", port=8000)
