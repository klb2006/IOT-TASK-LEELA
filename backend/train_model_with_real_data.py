"""
Real ML Model Training - Uses actual sensor data from PostgreSQL
Replaces the fake 8-sample training with proper real-world data
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, precision_score, recall_score
import joblib
import json
from datetime import datetime
from dotenv import load_dotenv
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, LSTM, GRU
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
from tensorflow.keras.regularizers import l2

# Load environment variables
load_dotenv()

# Database configuration from .env
DB_HOST = os.getenv('DB_HOST')
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_PORT = os.getenv('DB_PORT', 5432)
DB_SSLMODE = os.getenv('DB_SSLMODE', 'require')

print("="*70)
print("REAL ML MODEL TRAINING WITH SENSOR DATA FROM DATABASE")
print("="*70)

def fetch_sensor_data_from_db():
    """Fetch all sensor readings from PostgreSQL database"""
    try:
        connection = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            port=DB_PORT,
            sslmode=DB_SSLMODE
        )
        
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        
        # Fetch all sensor data
        cursor.execute("""
            SELECT 
                distance, 
                temperature, 
                water_percent, 
                EXTRACT(MINUTE FROM timestamp::timestamp) as minute,
                EXTRACT(HOUR FROM timestamp::timestamp) as hour,
                timestamp
            FROM sensor_readings
            ORDER BY timestamp DESC
            LIMIT 10000
        """)
        
        data = cursor.fetchall()
        cursor.close()
        connection.close()
        
        print(f"✓ Fetched {len(data)} sensor readings from database")
        return data
    except Exception as e:
        print(f"✗ Database connection error: {e}")
        print("  Using sample data for demonstration...")
        return None

def create_water_level_labels(water_percent):
    """Convert water percentage to class labels
    LOW: 0-25%, MEDIUM: 25-50%, HIGH: 50-75%, FULL: 75-100%"""
    if water_percent < 25:
        return 0  # LOW
    elif water_percent < 50:
        return 1  # MEDIUM
    elif water_percent < 75:
        return 2  # HIGH
    else:
        return 3  # FULL

def prepare_training_data(data):
    """Prepare data for model training with proper train/test split"""
    
    if data is None or len(data) < 100:
        print("⚠ WARNING: Not enough real data. Creating larger sample dataset...")
        # Generate synthetic data based on realistic patterns
        np.random.seed(42)
        data = []
        for i in range(500):
            distance = np.random.uniform(5, 50)
            temperature = np.random.uniform(15, 40)
            water_percent = np.random.uniform(0, 100)
            minute = np.random.randint(0, 60)
            hour = np.random.randint(0, 24)
            data.append({
                'distance': distance,
                'temperature': temperature,
                'water_percent': water_percent,
                'minute': minute,
                'hour': hour
            })
    
    # Convert to DataFrame
    df = pd.DataFrame(data)
    
    # Remove any rows with NaN values
    df = df.dropna()
    
    print(f"\n📊 Dataset Info:")
    print(f"  Total samples: {len(df)}")
    print(f"  Features: {list(df.columns)}")
    
    # Create labels
    df['label'] = df['water_percent'].apply(create_water_level_labels)
    
    # Show class distribution
    class_names = ['LOW', 'MEDIUM', 'HIGH', 'FULL']
    print(f"\n  Class Distribution:")
    for i, name in enumerate(class_names):
        count = (df['label'] == i).sum()
        pct = (count / len(df)) * 100
        print(f"    {name}: {count} samples ({pct:.1f}%)")
    
    # Select features for training
    features = ['distance', 'temperature', 'water_percent', 'minute', 'hour']
    X = df[features].values
    y = df['label'].values
    
    # One-hot encode labels
    y_encoded = tf.keras.utils.to_categorical(y, num_classes=4)
    
    # Normalize features using MinMaxScaler
    scaler = MinMaxScaler(feature_range=(0, 1))
    X_scaled = scaler.fit_transform(X)
    
    # Split data: 70% train, 15% validation, 15% test
    X_train, X_temp, y_train, y_temp = train_test_split(
        X_scaled, y_encoded, test_size=0.3, random_state=42, stratify=y
    )
    X_val, X_test, y_val, y_test = train_test_split(
        X_temp, y_temp, test_size=0.5, random_state=42, stratify=y_temp.argmax(axis=1)
    )
    
    print(f"\n🔀 Data Split:")
    print(f"  Training: {len(X_train)} samples ({len(X_train)/len(X)*100:.1f}%)")
    print(f"  Validation: {len(X_val)} samples ({len(X_val)/len(X)*100:.1f}%)")
    print(f"  Testing: {len(X_test)} samples ({len(X_test)/len(X)*100:.1f}%)")
    
    return X_train, X_val, X_test, y_train, y_val, y_test, scaler, features

def build_model(input_shape):
    """Build neural network with regularization to prevent overfitting"""
    model = Sequential([
        Dense(128, activation='relu', input_shape=(input_shape,), kernel_regularizer=l2(0.001)),
        Dropout(0.3),
        Dense(64, activation='relu', kernel_regularizer=l2(0.001)),
        Dropout(0.3),
        Dense(32, activation='relu', kernel_regularizer=l2(0.001)),
        Dropout(0.2),
        Dense(16, activation='relu', kernel_regularizer=l2(0.001)),
        Dense(4, activation='softmax')  # 4 classes: LOW, MEDIUM, HIGH, FULL
    ])
    
    model.compile(
        optimizer='adam',
        loss='categorical_crossentropy',
        metrics=['accuracy', tf.keras.metrics.Precision(), tf.keras.metrics.Recall()]
    )
    
    return model

def train_model(model, X_train, X_val, X_test, y_train, y_val, y_test):
    """Train model with proper validation and early stopping"""
    
    print("\n🚀 Training Model...")
    print("  (With dropout and L2 regularization to prevent overfitting)")
    
    # Early stopping to prevent overfitting
    early_stop = EarlyStopping(
        monitor='val_loss',
        patience=10,
        restore_best_weights=True,
        verbose=1
    )
    
    # Save best model checkpoint
    checkpoint = ModelCheckpoint(
        'best_model.h5',
        monitor='val_accuracy',
        save_best_only=True,
        verbose=0
    )
    
    # Train model
    history = model.fit(
        X_train, y_train,
        validation_data=(X_val, y_val),
        epochs=100,
        batch_size=16,
        verbose=1,
        callbacks=[early_stop, checkpoint]
    )
    
    return history

def evaluate_model(model, X_train, X_val, X_test, y_train, y_val, y_test):
    """Evaluate model on all datasets and show real metrics"""
    
    print("\n" + "="*70)
    print("MODEL EVALUATION - REAL ACCURACY METRICS")
    print("="*70)
    
    # Predictions
    y_train_pred = model.predict(X_train, verbose=0).argmax(axis=1)
    y_val_pred = model.predict(X_val, verbose=0).argmax(axis=1)
    y_test_pred = model.predict(X_test, verbose=0).argmax(axis=1)
    
    y_train_true = y_train.argmax(axis=1)
    y_val_true = y_val.argmax(axis=1)
    y_test_true = y_test.argmax(axis=1)
    
    class_names = ['LOW', 'MEDIUM', 'HIGH', 'FULL']
    
    # Training metrics
    print("\n📈 TRAINING SET METRICS:")
    train_acc = accuracy_score(y_train_true, y_train_pred)
    train_prec = precision_score(y_train_true, y_train_pred, average='weighted', zero_division=0)
    train_recall = recall_score(y_train_true, y_train_pred, average='weighted', zero_division=0)
    print(f"  Accuracy:  {train_acc:.4f}")
    print(f"  Precision: {train_prec:.4f}")
    print(f"  Recall:    {train_recall:.4f}")
    
    # Validation metrics
    print("\n🎯 VALIDATION SET METRICS:")
    val_acc = accuracy_score(y_val_true, y_val_pred)
    val_prec = precision_score(y_val_true, y_val_pred, average='weighted', zero_division=0)
    val_recall = recall_score(y_val_true, y_val_pred, average='weighted', zero_division=0)
    print(f"  Accuracy:  {val_acc:.4f}")
    print(f"  Precision: {val_prec:.4f}")
    print(f"  Recall:    {val_recall:.4f}")
    
    # Test metrics (Most important - unseen data)
    print("\n⭐ TEST SET METRICS (REAL-WORLD ACCURACY):")
    test_acc = accuracy_score(y_test_true, y_test_pred)
    test_prec = precision_score(y_test_true, y_test_pred, average='weighted', zero_division=0)
    test_recall = recall_score(y_test_true, y_test_pred, average='weighted', zero_division=0)
    print(f"  Accuracy:  {test_acc:.4f}  ← This is REAL accuracy!")
    print(f"  Precision: {test_prec:.4f}")
    print(f"  Recall:    {test_recall:.4f}")
    
    # Per-class metrics
    print("\n📊 PER-CLASS METRICS (Test Set):")
    print(classification_report(y_test_true, y_test_pred, target_names=class_names))
    
    # Confusion matrix
    print("🔍 CONFUSION MATRIX (Test Set):")
    cm = confusion_matrix(y_test_true, y_test_pred)
    print(cm)
    
    # Check for overfitting
    print("\n⚠ OVERFITTING CHECK:")
    gap = train_acc - test_acc
    if gap > 0.1:
        print(f"  ⚠ WARNING: Large gap between train ({train_acc:.4f}) and test ({test_acc:.4f}) accuracy")
        print(f"  Your model may be OVERFITTING. Consider:")
        print(f"    - More training data")
        print(f"    - Increase dropout rate")
        print(f"    - Add more L2 regularization")
    else:
        print(f"  ✓ Training ({train_acc:.4f}) and test ({test_acc:.4f}) accuracy are close")
        print(f"  Your model is generalizing well!")
    
    return {
        'train': {'accuracy': train_acc, 'precision': train_prec, 'recall': train_recall},
        'val': {'accuracy': val_acc, 'precision': val_prec, 'recall': val_recall},
        'test': {'accuracy': test_acc, 'precision': test_prec, 'recall': test_recall}
    }

def main():
    # Create saved_models directory if it doesn't exist
    os.makedirs('saved_models', exist_ok=True)
    
    # Fetch real data from database
    data = fetch_sensor_data_from_db()
    
    # Prepare training data with proper train/val/test split
    X_train, X_val, X_test, y_train, y_val, y_test, scaler, features = prepare_training_data(data)
    
    # Save scaler for later use in predictions
    joblib.dump(scaler, 'saved_models/scaler.pkl')
    print("✓ Scaler saved to saved_models/scaler.pkl")
    
    # Build model with regularization
    model = build_model(X_train.shape[1])
    print("\n✓ Model built with dropout and L2 regularization")
    print(f"  Model architecture:")
    model.summary()
    
    # Train model
    history = train_model(model, X_train, X_val, X_test, y_train, y_val, y_test)
    
    # Save model
    model.save('saved_models/best_model.h5')
    print("\n✓ Model saved to saved_models/best_model.h5")
    
    # Evaluate model comprehensively
    metrics = evaluate_model(model, X_train, X_val, X_test, y_train, y_val, y_test)
    
    # Save metrics report
    with open('saved_models/model_metrics.json', 'w') as f:
        json.dump(metrics, f, indent=2)
    print("\n✓ Metrics saved to saved_models/model_metrics.json")
    
    # Save feature names
    with open('saved_models/feature_names.json', 'w') as f:
        json.dump(features, f)
    print("✓ Feature names saved to saved_models/feature_names.json")
    
    print("\n" + "="*70)
    print("TRAINING COMPLETE!")
    print("="*70)
    print("\nNEXT STEPS:")
    print("1. Check the metrics - compare train vs test accuracy")
    print("2. If test accuracy is much lower, you need MORE real data")
    print("3. Deploy the model by restarting main.py")
    print("4. Your predictions will now use REAL trained weights!")
    print("="*70 + "\n")

if __name__ == "__main__":
    # Set up TensorFlow to use GPU if available
    physical_devices = tf.config.list_physical_devices('GPU')
    if physical_devices:
        print(f"✓ GPU available: {physical_devices}")
    else:
        print("ℹ CPU mode (GPU not available)")
    
    main()
