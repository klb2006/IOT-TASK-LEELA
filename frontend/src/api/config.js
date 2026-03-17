// API Configuration
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const API_ENDPOINTS = {
  STATUS: `${API_BASE_URL}/api/v1/status`,
  SENSOR_LATEST: `${API_BASE_URL}/api/v1/sensor/latest`,
  SENSOR_HISTORY: `${API_BASE_URL}/api/v1/sensor/history`,
  PREDICT: `${API_BASE_URL}/api/v1/predict`,
  MODEL_INFO: `${API_BASE_URL}/api/v1/model-info`,
  PREDICTIONS_HISTORY: `${API_BASE_URL}/api/v1/predictions/history`,
  TEST: `${API_BASE_URL}/api/v1/test`,
};

// Fetch with error handling
export const fetchAPI = async (url, options = {}) => {
  try {
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    });

    if (!response.ok) {
      throw new Error(`API Error: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error('API Fetch Error:', error);
    throw error;
  }
};

export default API_BASE_URL;
