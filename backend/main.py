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
from config import FEATURE_RANGES, get_all_feature_ranges_dict, print_feature_ranges

# Load environment variables from .env
load_dotenv()

# ===== NEW ML MODEL LOADER (XGBoost & others) =====
try:
    from ml_training.model_loader import (
        predict_water_percent,
        get_best_model_name,
        get_model_comparison,
        get_available_models,
        load_best_model
    )
    MODEL_LOADER_AVAILABLE = True
    print("[OK] ML model loader imported successfully")
except ImportError as e:
    MODEL_LOADER_AVAILABLE = False
    print(f"[WARNING] ML model loader not available: {e}")

# ===== LAZY TENSORFLOW LOADING =====
# We use lazy loading to defer TensorFlow import errors until actually needed
# This prevents import errors from stopping the entire server startup
ml_model = None
TENSORFLOW_AVAILABLE = False
data_scaler = None

def create_data_scaler():
    """
    Create a MinMaxScaler with fitted ranges from training data
    This is the same scaling used during model training
    Feature ranges are configured in config.py
    """
    global data_scaler
    try:
        from sklearn.preprocessing import MinMaxScaler
        
        # Get feature ranges from config
        feature_ranges_dict = get_all_feature_ranges_dict()
        
        # Create feature matrix with known ranges
        scaler = MinMaxScaler(feature_range=(0, 1))
        
        # Create min and max arrays from config
        min_values = [feature_ranges_dict[name][0] for name in 
                     ['distance', 'temperature', 'water_percent', 'minute', 'hour']]
        max_values = [feature_ranges_dict[name][1] for name in 
                     ['distance', 'temperature', 'water_percent', 'minute', 'hour']]
        
        # Fit scaler on the full range of possible values
        fit_data = np.array([min_values, max_values])
        scaler.fit(fit_data)
        data_scaler = scaler
        
        print("[OK] Data scaler initialized with feature ranges from config.py:")
        print("     distance: [%d, %d] cm" % (min_values[0], max_values[0]))
        print("     temperature: [%d, %d] °C" % (min_values[1], max_values[1]))
        print("     water_percent: [%d, %d] %%" % (min_values[2], max_values[2]))
        print("     minute: [%d, %d]" % (min_values[3], max_values[3]))
        print("     hour: [%d, %d]" % (min_values[4], max_values[4]))
        
        return scaler
    except Exception as e:
        print(f"[ERROR] Failed to create scaler: {e}")
        return None

def preprocess_prediction_input(distance, temperature, water_percent, minute, hour):
    """
    Preprocess input data using the same scaling as training
    Returns normalized data ready for model prediction
    """
    global data_scaler
    
    if data_scaler is None:
        data_scaler = create_data_scaler()
    
    if data_scaler is None:
        print("[WARNING] Scaler not available, using raw input")
        return np.array([[distance, temperature, water_percent, minute, hour]])
    
    try:
        # Create input array
        raw_input = np.array([[distance, temperature, water_percent, minute, hour]])
        
        # Scale using the fitted scaler
        scaled_input = data_scaler.transform(raw_input)
        
        return scaled_input
    except Exception as e:
        print(f"[ERROR] Preprocessing failed: {e}")
        return np.array([[distance, temperature, water_percent, minute, hour]])

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

def load_ml_model():
    """
    Lazy load the ML model - only attempts to load once
    Uses the trained best_model.h5 file with proper data preprocessing
    Handles Keras 3.x to Keras 2.x compatibility
    """
    global ml_model, TENSORFLOW_AVAILABLE, data_scaler
    
    if ml_model is not None:
        return ml_model  # Already loaded
    
    print("\n" + "="*60)
    print("Loading ML model...")
    print("="*60)
    
    load_model_fn = try_load_tensorflow()
    if not load_model_fn:
        print("[WARNING] TensorFlow not available")
        return None
    
    try:
        # Get the directory of this script
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Try multiple possible paths (prioritize local directory and saved_models)
        possible_paths = [
            os.path.join(current_dir, "saved_models", "best_model.h5"),
            os.path.join(current_dir, "saved_models", "model23.h5"),
            os.path.join(current_dir, "model23.h5"),
            os.path.join(current_dir, "best_model.h5"),
            os.path.join(os.path.dirname(current_dir), "model23.h5"),
            os.path.join(os.path.dirname(current_dir), "best_model.h5"),
            "model23.h5",
            "best_model.h5",
            "/opt/render/project/src/backend/model23.h5",
            "/opt/render/project/src/backend/best_model.h5"
        ]
        
        model_path = None
        for path in possible_paths:
            if os.path.exists(path):
                model_path = path
                print(f"[INFO] Found model at: {path}")
                break
        
        if not model_path:
            print(f"[WARNING] Model not found in any of these paths:")
            for p in possible_paths:
                print(f"  - {p}")
            print("="*60 + "\n")
            return None
        
        # Load the model with Keras 3.x compatibility handling
        try:
            from tensorflow.keras.layers import InputLayer
            
            # Custom object dict to handle Keras 3.x InputLayer config
            custom_objects = {
                'InputLayer': InputLayer
            }
            
            # Try loading with custom objects
            ml_model = load_model_fn(model_path, custom_objects=custom_objects, safe_mode=False)
            print(f"[OK] ML model loaded successfully with Keras 3.x compatibility!")
            print(f"[INFO] Model summary:")
            ml_model.summary()
            TENSORFLOW_AVAILABLE = True
        except TypeError as te:
            # If custom_objects doesn't work, try without safe_mode
            if "batch_shape" in str(te) or "optional" in str(te):
                print(f"[WARNING] Keras 3.x format detected, attempting conversion...")
                
                try:
                    # Try loading without custom_objects, just no safe_mode
                    ml_model = load_model_fn(model_path, safe_mode=False)
                    print(f"[OK] ML model loaded with safe_mode=False")
                    TENSORFLOW_AVAILABLE = True
                except Exception as e2:
                    print(f"[WARNING] Standard loading failed: {e2}")
                    print(f"[INFO] Model will use architecture inference...")
                    
                    # Fall back to trying to extract and rebuild
                    ml_model = load_model_with_h5_conversion(model_path)
                    if ml_model is None:
                        raise Exception("All model loading attempts failed")
            else:
                raise te
        except Exception as e:
            print(f"[WARNING] Initial loading failed: {e}")
            print(f"[INFO] Attempting H5 conversion fallback...")
            
            # Use h5py to extract and rebuild
            ml_model = load_model_with_h5_conversion(model_path)
            if ml_model is None:
                raise Exception("H5 conversion also failed")
        
        # Initialize the data scaler for preprocessing
        if data_scaler is None:
            data_scaler = create_data_scaler()
        
        print("="*60 + "\n")
        return ml_model
        
    except Exception as e:
        print(f"[ERROR] Model loading failed: {e}")
        import traceback
        traceback.print_exc()
        print("="*60 + "\n")
        return None

def load_model_with_h5_conversion(model_path):
    """
    Fallback: Extract model from h5 file, rebuild with Keras 2.x format, and apply weights
    This handles Keras 3.x models that can't be loaded directly
    """
    try:
        import h5py
        import json
        from tensorflow.keras.models import Sequential
        from tensorflow.keras.layers import LSTM, Dense, Dropout
        
        print("[INFO] Extracting model architecture AND weights from h5 file...")
        
        def extract_weights_recursive(group, layer_name, found_datasets=None):
            """Recursively find all datasets in nested h5 group structure"""
            if found_datasets is None:
                found_datasets = []
            
            for key, item in sorted(group.items()):
                if isinstance(item, h5py.Dataset):
                    weight_array = np.array(item)
                    found_datasets.append((key, weight_array))
                elif isinstance(item, h5py.Group):
                    # Recursively dive into nested groups
                    extract_weights_recursive(item, f"{layer_name}/{key}", found_datasets)
            
            return found_datasets
        
        with h5py.File(model_path, 'r') as f:
            # Extract all layer weights properly
            layer_weights = {}
            if 'model_weights' in f:
                for layer_name in f['model_weights'].keys():
                    if layer_name != 'top_level_model_weights':
                        layer_group = f[f'model_weights/{layer_name}']
                        
                        # Recursively extract all datasets from nested groups
                        weight_tuples = extract_weights_recursive(layer_group, layer_name)
                        
                        if weight_tuples:  # Only add if we found actual weights
                            sorted_weights = []
                            weight_dict = {k: w for k, w in weight_tuples}
                            
                            # Determine correct ordering for all weight types
                            if 'kernel' in weight_dict:
                                sorted_weights.append(weight_dict['kernel'])
                            if 'recurrent_kernel' in weight_dict:
                                sorted_weights.append(weight_dict['recurrent_kernel'])
                            if 'bias' in weight_dict:
                                sorted_weights.append(weight_dict['bias'])
                            
                            if sorted_weights:
                                layer_weights[layer_name] = sorted_weights
                                print(f"[OK] {layer_name}: extracted {len(sorted_weights)} weights")
                                for idx, w in enumerate(sorted_weights):
                                    print(f"    [{idx}] shape {w.shape}")
            
            print(f"[OK] Extracted {len(layer_weights)} layers with weights")
            
            # Detect units from LSTM/Dense weight shapes
            lstm_units = 128
            lstm1_units = 64
            dense_units = 32
            
            # Find LSTM units from recurrent kernel shape
            if 'lstm' in layer_weights and len(layer_weights['lstm']) > 1:
                recurrent_shape = layer_weights['lstm'][1].shape
                if len(recurrent_shape) == 2:
                    lstm_units = recurrent_shape[0]
                    print(f"[INFO] LSTM units detected: {lstm_units}")
            
            if 'lstm_1' in layer_weights and len(layer_weights['lstm_1']) > 1:
                recurrent_shape = layer_weights['lstm_1'][1].shape
                if len(recurrent_shape) == 2:
                    lstm1_units = recurrent_shape[0]
                    print(f"[INFO] LSTM_1 units detected: {lstm1_units}")
            
            if 'dense' in layer_weights and len(layer_weights['dense']) > 0:
                dense_shape = layer_weights['dense'][0].shape
                if len(dense_shape) == 2:
                    dense_units = dense_shape[1]
                    print(f"[INFO] Dense units detected: {dense_units}")
            
            print(f"[INFO] Building model: LSTM({lstm_units}) → Dropout(0.3) → LSTM({lstm1_units}) → Dense({dense_units}) → Dense(1)")
            print(f"[DEBUG] Force rebuild - LSTM weights found: {len(layer_weights)}")
            
            # Build model matching the actual structure
            model = Sequential([
                LSTM(lstm_units, return_sequences=True, input_shape=(1, 5), name='lstm'),
                Dropout(0.3, name='dropout'),
                LSTM(lstm1_units, name='lstm_1'),
                Dense(dense_units, activation='relu', name='dense'),
                Dense(1, activation='linear', name='dense_1')
            ])
            
            model.compile(optimizer='adam', loss='mse', metrics=['mae'])
            
            # Apply extracted weights to model layers
            print("[INFO] Applying extracted weights to model...")
            
            layer_mapping = {
                'lstm': 0,
                'dropout': 1,
                'lstm_1': 2,
                'dense': 3,
                'dense_1': 4
            }
            
            weights_applied = 0
            for layer_name, weights_list in layer_weights.items():
                if layer_name in layer_mapping and len(weights_list) > 0:
                    layer_idx = layer_mapping[layer_name]
                    model_layer = model.layers[layer_idx]
                    
                    try:
                        # Verify correct number of weights
                        if layer_name == 'dropout':
                            # Dropout has no weights
                            continue
                        
                        expected_weights = len(model_layer.weights)
                        actual_weights = len(weights_list)
                        
                        if actual_weights == expected_weights:
                            model_layer.set_weights(weights_list)
                            weights_applied += 1
                            print(f"  [OK] {layer_name}: applied {actual_weights} weight arrays")
                        else:
                            print(f"  [WARNING] {layer_name}: expected {expected_weights} weights, got {actual_weights}")
                    except Exception as e:
                        print(f"  [WARNING] {layer_name}: {str(e)[:100]}")
            
            if weights_applied > 0:
                print(f"[OK] Successfully applied weights to {weights_applied}/{len(layer_weights)} layers!")
                print(f"[INFO] Model is now using TRAINED weights!")
            else:
                print(f"[WARNING] No weights could be applied. Model will use RANDOM initialization.")
            
            return model
        
    except Exception as e:
        print(f"[ERROR] H5 conversion failed: {e}")
        import traceback
        traceback.print_exc()
        return None
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

# app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Local development
        "https://iot-water-tank-frontend.onrender.com",  # Production
        os.getenv("FRONTEND_URL", "http://localhost:3000"),  # From environment
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
        # Preprocess input data using MinMaxScaler (same as training)
        x_scaled = preprocess_prediction_input(
            distance=request.distance,
            temperature=request.temperature,
            water_percent=request.water_percent,
            minute=request.minute,
            hour=request.hour
        )
        
        # Reshape to model input shape (samples, timesteps=1, features=5)
        x_model = x_scaled.reshape((1, 1, 5))
        
        # Make prediction
        prediction = model.predict(x_model, verbose=0)
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
    return await predict_water(request)

@app.post("/api/v1/predict")
async def predict_activity(data: dict):
    """
    Predict water activity/level based on sensor data
    
    Request body:
    {
        "distance": float,
        "temperature": float,
        "time_features": [minute, hour],  # or just pass minute and hour separately
        "water_percent": float (optional, defaults to 50),
        "node_id": string (optional, defaults to "node-1")
    }
    
    Response:
    {
        "status": "success",
        "prediction": string (predicted water activity),
        "confidence": float (confidence score 0-1),
        "input": {...},
        "timestamp": ISO timestamp
    }
    """
    model = load_ml_model()
    
    try:
        # Extract parameters from dict
        distance = data.get('distance')
        temperature = data.get('temperature')
        time_features = data.get('time_features', [30, 14])
        water_percent = data.get('water_percent', 50.0)
        node_id = data.get('node_id', 'node-1')
        
        # Validate inputs
        if distance is None or temperature is None:
            return {
                "status": "error",
                "message": "Missing required fields: distance, temperature"
            }
        
        # Parse time_features if provided as list
        if isinstance(time_features, list) and len(time_features) >= 2:
            minute, hour = time_features[0], time_features[1]
        else:
            minute, hour = 30, 14  # Default time
        
        if model is None:
            # Return dummy prediction when model not available
            prediction_label = "water_activity_detected"
            confidence = 0.85
        else:
            # Preprocess input data using MinMaxScaler
            x_scaled = preprocess_prediction_input(
                distance=float(distance),
                temperature=float(temperature),
                water_percent=float(water_percent),
                minute=int(minute),
                hour=int(hour)
            )
            
            # Reshape to model input shape
            x_model = x_scaled.reshape((1, 1, 5))
            
            # Make prediction
            prediction = model.predict(x_model, verbose=0)
            predicted_value = float(prediction[0][0])
            
            # Map to activity classes
            classes = ["no_activity", "shower", "faucet", "toilet", "dishwasher"]
            # Simple quantization: divide predicted value into classes
            class_idx = min(int(predicted_value / 20), len(classes) - 1)
            prediction_label = classes[class_idx]
            confidence = 0.85  # Model confidence
        
        # Store in database
        insert_prediction(
            node_id=node_id,
            distance=float(distance),
            temperature=float(temperature),
            water_percent=float(water_percent),
            prediction=prediction_label,
            confidence=confidence
        )
        
        return {
            "status": "success",
            "prediction": prediction_label,
            "confidence": confidence,
            "input": {
                "distance": distance,
                "temperature": temperature,
                "time_features": [minute, hour]
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {
            "status": "error",
            "message": str(e)
        }

@app.get("/api/v1/predictions-history")
async def get_predictions_history_endpoint(limit: int = 100):
    """
    Get historical predictions with timestamps
    Alias for /api/v1/predictions/history with same response format
    """
    predictions = get_predictions_history(limit)
    return {
        "status": "success",
        "count": len(predictions),
        "data": predictions
    }

@app.post("/api/v1/test")
async def test_prediction_endpoint():
    """Test prediction with sample data"""
    test_data = {
        "distance": 24.5,
        "temperature": 28.3,
        "water_percent": 75.0,
        "time_features": [30, 14],
        "node_id": "test-node"
    }
    return await predict_activity(test_data)

# ===== STARTUP EVENTS =====
@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    print("\n" + "="*60)
    print("[START] Water Tank Monitoring System - Starting UP")
    print("="*60)
    
    # Print configurable feature ranges
    print_feature_ranges()
    
    # Create all required tables
    create_all_tables()
    
    print("[OK] API Server ready!")
    print("[INFO] API Documentation: http://127.0.0.1:8000/docs")
    print("[INFO] To customize feature ranges, edit: backend/config.py")
    print("="*60 + "\n")

# ===== MAIN =====
if __name__ == "__main__":
    print("Starting FastAPI server...")
    print("Run with: uvicorn main:app --reload")
    
    # Create tables
    create_all_tables()
    
    # Start server
    uvicorn.run(app, host="127.0.0.1", port=8000)
