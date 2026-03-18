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

# Load environment variables from .env
load_dotenv()

# ===== LAZY TENSORFLOW LOADING =====
# We use lazy loading to defer TensorFlow import errors until actually needed
# This prevents import errors from stopping the entire server startup
ml_model = None
TENSORFLOW_AVAILABLE = False

def try_load_tensorflow():
    """Lazy load TensorFlow/Keras - only called when actually needed"""
    global TENSORFLOW_AVAILABLE
    try:
        # Suppress TensorFlow warnings
        import os
        os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
        
        from tensorflow.keras.models import load_model
        TENSORFLOW_AVAILABLE = True
        return load_model
    except Exception as tf_error:
        print(f"[WARNING] TensorFlow import failed: {tf_error}")
        import traceback
        traceback.print_exc()
        try:
            from keras.models import load_model
            TENSORFLOW_AVAILABLE = True
            return load_model
        except Exception as keras_error:
            print(f"[WARNING] Keras import also failed: {keras_error}")
            import traceback
            traceback.print_exc()
            print("[INFO] Will run without ML model support")
            TENSORFLOW_AVAILABLE = False
            return None

def rebuild_model_from_weights(model_path):
    """
    Extract weights from Keras 3.x model and rebuild with TF 2.15 compatible architecture
    """
    try:
        import h5py
        import numpy as np
        print("[INFO] Attempting to extract weights from model...")
        
        with h5py.File(model_path, 'r') as f:
            weights_dict = {}
            
            # Helper to recursively find weight datasets
            def get_weight_arrays(group_path):
                """Get all weight arrays from a group, handling nested structure"""
                arrays = []
                if isinstance(f[group_path], h5py.Dataset):
                    return [np.array(f[group_path])]
                
                for key in f[group_path].keys():
                    item_path = f"{group_path}/{key}"
                    if isinstance(f[item_path], h5py.Dataset):
                        arrays.append(np.array(f[item_path]))
                    elif isinstance(f[item_path], h5py.Group):
                        arrays.extend(get_weight_arrays(item_path))
                return arrays
            
            # Extract GRU weights
            print("[INFO] Extracting GRU layer weights...")
            gru_path = 'model_weights/gru'
            if gru_path in f:
                gru_weights = get_weight_arrays(gru_path)
                weights_dict['gru'] = gru_weights
                print(f"  [OK] GRU: {len(gru_weights)} weight arrays extracted")
                for i, w in enumerate(gru_weights):
                    print(f"      Weight {i}: {w.shape}")
            
            # Extract GRU_1 weights
            print("[INFO] Extracting GRU_1 layer weights...")
            gru1_path = 'model_weights/gru_1'
            if gru1_path in f:
                gru1_weights = get_weight_arrays(gru1_path)
                weights_dict['gru1'] = gru1_weights
                print(f"  [OK] GRU_1: {len(gru1_weights)} weight arrays extracted")
                for i, w in enumerate(gru1_weights):
                    print(f"      Weight {i}: {w.shape}")
            
            # Extract Dense_4 weights
            print("[INFO] Extracting Dense_4 layer weights...")
            dense4_path = 'model_weights/dense_4'
            if dense4_path in f:
                dense4_weights = get_weight_arrays(dense4_path)
                weights_dict['dense4'] = dense4_weights
                print(f"  [OK] Dense_4: {len(dense4_weights)} weight arrays extracted")
                for i, w in enumerate(dense4_weights):
                    print(f"      Weight {i}: {w.shape}")
            
            # Extract Dense_5 weights
            print("[INFO] Extracting Dense_5 layer weights...")
            dense5_path = 'model_weights/dense_5'
            if dense5_path in f:
                dense5_weights = get_weight_arrays(dense5_path)
                weights_dict['dense5'] = dense5_weights
                print(f"  [OK] Dense_5: {len(dense5_weights)} weight arrays extracted")
                for i, w in enumerate(dense5_weights):
                    print(f"      Weight {i}: {w.shape}")
            
            return weights_dict if weights_dict else None
        
    except Exception as e:
        print(f"[ERROR] Weight extraction failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def load_model_with_fallback_weights(model_path):
    """
    Rebuild the model with the correct GRU + Dense architecture and load extracted weights
    """
    from tensorflow.keras.models import Sequential
    from tensorflow.keras.layers import GRU, Dense, Dropout
    
    try:
        weights_dict = rebuild_model_from_weights(model_path)
        if not weights_dict:
            print("[WARNING] No weights extracted")
            return None
        
        print("[INFO] Building model with GRU layers...")
        
        # Build model: GRU -> GRU -> Dense -> Dense (based on file structure)
        model = Sequential([
            GRU(64, return_sequences=True, input_shape=(1, 5), name='gru'),
            GRU(32, name='gru_1'),
            Dropout(0.2, name='dropout'),
            Dense(16, activation='relu', name='dense_4'),
            Dense(4, activation='softmax', name='dense_5')
        ])
        
        model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
        print("[INFO] Model architecture created, loading weights...")
        
        # Load weights into each layer
        try:
            if 'gru' in weights_dict and weights_dict['gru']:
                print(f"[INFO] Setting GRU weights ({len(weights_dict['gru'])} arrays)...")
                model.layers[0].set_weights(weights_dict['gru'])
                print("[OK] GRU layer weights loaded")
            
            if 'gru1' in weights_dict and weights_dict['gru1']:
                print(f"[INFO] Setting GRU_1 weights ({len(weights_dict['gru1'])} arrays)...")
                model.layers[1].set_weights(weights_dict['gru1'])
                print("[OK] GRU_1 layer weights loaded")
            
            if 'dense4' in weights_dict and weights_dict['dense4']:
                print(f"[INFO] Setting Dense_4 weights ({len(weights_dict['dense4'])} arrays)...")
                model.layers[3].set_weights(weights_dict['dense4'])
                print("[OK] Dense_4 layer weights loaded")
            
            if 'dense5' in weights_dict and weights_dict['dense5']:
                print(f"[INFO] Setting Dense_5 weights ({len(weights_dict['dense5'])} arrays)...")
                model.layers[4].set_weights(weights_dict['dense5'])
                print("[OK] Dense_5 layer weights loaded")
            
            print("[OK] Model successfully rebuilt with all weights!")
            return model
            
        except Exception as weight_error:
            print(f"[WARNING] Error loading some weights: {weight_error}")
            print("[INFO] Returning model with partially loaded weights")
            import traceback
            traceback.print_exc()
            return model
        
    except Exception as e:
        print(f"[ERROR] Model rebuilding failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def load_ml_model():
    """
    Lazy load the ML model - only attempts to load once
    """
    global ml_model, TENSORFLOW_AVAILABLE
    
    if ml_model is not None:
        return ml_model  # Already loaded
    
    print("\n" + "="*60)
    print("Loading ML model...")
    print("="*60)
    
    load_model_fn = try_load_tensorflow()
    if not load_model_fn:
        print("[INFO] Skipping model loading - TensorFlow not available")
        return None
    
    try:
        # Get the directory of this script
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Try multiple possible paths (prioritize local directory)
        possible_paths = [
            os.path.join(current_dir, "best_model.h5"),
            os.path.join(current_dir, "saved_models", "best_model.h5"),
            os.path.join(os.path.dirname(current_dir), "best_model.h5"),
            "best_model.h5",
            "/opt/render/project/src/backend/best_model.h5"
        ]
        
        model_path = None
        for path in possible_paths:
            if os.path.exists(path):
                model_path = path
                print(f"[INFO] Found model at: {path}")
                break
        
        if model_path:
            try:
                # Try with safe_mode=False first
                try:
                    ml_model = load_model_fn(model_path, safe_mode=False)
                    print(f"[OK] ML model loaded successfully (safe_mode=False) from {model_path}")
                    TENSORFLOW_AVAILABLE = True
                    print("="*60 + "\n")
                    return ml_model
                except TypeError:
                    # Try without safe_mode parameter
                    ml_model = load_model_fn(model_path)
                    print(f"[OK] ML model loaded successfully from {model_path}")
                    TENSORFLOW_AVAILABLE = True
                    print("="*60 + "\n")
                    return ml_model
            except Exception as e:
                print(f"[WARNING] Direct loading failed: {e}")
                print(f"[INFO] Attempting to extract weights and rebuild model...")
                
                # Try extracting weights and rebuilding
                ml_model = load_model_with_fallback_weights(model_path)
                if ml_model is not None:
                    print(f"[OK] Model successfully rebuilt with extracted weights")
                    TENSORFLOW_AVAILABLE = True
                    print("="*60 + "\n")
                    return ml_model
                
                print(f"[ERROR] Model loading and weight extraction both failed:")
                print(f"  Error type: {type(e).__name__}")
                print(f"  Error message: {e}")
                import traceback
                traceback.print_exc()
                print("[INFO] Will use fallback predictions")
                print("="*60 + "\n")
                return None
        else:
            print(f"[WARNING] Model not found. Checked paths:")
            for p in possible_paths:
                exists = "EXISTS" if os.path.exists(p) else "NOT FOUND"
                print(f"  - {p} [{exists}]")
            print("[INFO] Will use fallback predictions")
            return None
            
    except Exception as e:
        print(f"[WARNING] Error during model loading: {e}")
        print("[INFO] Will use fallback predictions")
        return None

# ThingSpeak import
from thingspeak import get_thingspeak_client

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
        "model_loaded": load_ml_model() is not None,
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
    model = load_ml_model()
    if model is None:
        return {"status": "error", "message": "ML model not loaded"}
    
    try:
        # Prepare input data [distance, temperature, water_percent, minute, hour]
        x = np.array([[request.distance, request.temperature, request.water_percent, request.minute, request.hour]])
        
        # Reshape to model input shape (1, 1, 5)
        x = x.reshape((1, 1, 5))
        
        # Make prediction
        prediction = model.predict(x, verbose=0)
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
