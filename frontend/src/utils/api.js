import axios from 'axios';
import config from '../config';

const API = axios.create({
  baseURL: config.API_BASE_URL,
  timeout: config.API_TIMEOUT,
  headers: {
    'Content-Type': 'application/json'
  }
});

// API Endpoints
export const apiEndpoints = {
  // Model endpoints
  getModelInfo: () => API.get('/api/v1/model-info'),
  
  // Prediction endpoints
  makePrediction: (data) => API.post('/api/v1/predict', data),
  getPredictionsHistory: (limit = 100) => 
    API.get('/api/v1/predictions-history', { params: { limit } }),
  
  // Sensor data endpoints
  getLatestSensorData: () => API.get('/api/v1/sensor/latest'),
  getSensorHistory: (limit = 100) => 
    API.get('/api/v1/sensor/history', { params: { limit } }),
  
  // System status
  getStatus: () => API.get('/api/v1/status')
};

export default API;
