"""
Script to create a sample ML model for water tank level prediction
Run this once to create the model file
"""
import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
import os

print("Creating sample ML model...")

# Create a simple neural network
model = Sequential([
    Dense(64, activation='relu', input_shape=(3,)),  # 3 inputs: distance, temperature, water_percent
    Dense(32, activation='relu'),
    Dense(16, activation='relu'),
    Dense(4, activation='softmax')  # 4 classes: LOW, MEDIUM, HIGH, FULL
])

model.compile(
    optimizer='adam',
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

# Create sample training data
X_train = np.array([
    [25, 28, 80],  # LOW water
    [20, 30, 60],  # MEDIUM water
    [15, 32, 40],  # HIGH water
    [10, 35, 20],  # FULL water
    [26, 27, 85],  # LOW water
    [18, 31, 55],  # MEDIUM water
    [14, 33, 35],  # HIGH water
    [9, 36, 15],   # FULL water
])

# One-hot encoded labels: [LOW, MEDIUM, HIGH, FULL]
y_train = np.array([
    [1, 0, 0, 0],  # LOW
    [0, 1, 0, 0],  # MEDIUM
    [0, 0, 1, 0],  # HIGH
    [0, 0, 0, 1],  # FULL
    [1, 0, 0, 0],  # LOW
    [0, 1, 0, 0],  # MEDIUM
    [0, 0, 1, 0],  # HIGH
    [0, 0, 0, 1],  # FULL
])

# Train model
print("Training model...")
model.fit(X_train, y_train, epochs=10, verbose=0)

# Save model
model_path = "saved_models/best_model.h5"
model.save(model_path)
print(f"✓ Model saved to {model_path}")
print(f"✓ Model expects 3 inputs: [distance, temperature, water_percent]")
print(f"✓ Model outputs 4 classes: [LOW, MEDIUM, HIGH, FULL]")
