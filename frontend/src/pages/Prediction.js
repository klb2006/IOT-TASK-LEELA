import React, { useState, useEffect } from 'react';
import { FaRobot, FaClock, FaRocket, FaChartBar } from 'react-icons/fa';
import { apiEndpoints } from '../utils/api';
import { ConfidenceGauge, ActivityTimeline, PredictionDistribution } from '../components/CustomCharts';
import '../styles/Prediction.css';
import config from '../config';

const Prediction = () => {
  const [modelInfo, setModelInfo] = useState(null);
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [inputData, setInputData] = useState({
    distance: '',
    temperature: '',
    water_percent: 50,
    time_features: [new Date().getMinutes(), new Date().getHours()],
    node_id: 'node-1'
  });

  // Fetch model info on mount
  useEffect(() => {
    fetchModelInfo();
    fetchPredictionHistory();
  }, []);

  const fetchModelInfo = async () => {
    try {
      const response = await apiEndpoints.getModelInfo();
      setModelInfo(response.data.model_info);
      setError(null);
    } catch (err) {
      setError('Failed to fetch model info');
      console.error('Error:', err);
    }
  };

  const [predictionHistory, setPredictionHistory] = useState([]);

  const fetchPredictionHistory = async () => {
    try {
      const response = await apiEndpoints.getPredictionsHistory(50);
      setPredictionHistory(response.data.data || []);
    } catch (err) {
      console.error('Error fetching history:', err);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setInputData(prev => ({
      ...prev,
      [name]: name === 'water_percent' ? parseFloat(value) : value
    }));
  };

  const handlePredict = async (e) => {
    e.preventDefault();
    
    if (!inputData.distance || !inputData.temperature) {
      setError('Please enter distance and temperature');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await apiEndpoints.makePrediction({
        distance: parseFloat(inputData.distance),
        temperature: parseFloat(inputData.temperature),
        water_percent: inputData.water_percent,
        time_features: inputData.time_features,
        node_id: inputData.node_id
      });

      setPrediction(response.data);
      fetchPredictionHistory();
    } catch (err) {
      setError('Prediction failed: ' + (err.response?.data?.message || err.message));
      console.error('Error:', err);
    } finally {
      setLoading(false);
    }
  };

  // Create prediction distribution data
  const getPredictionDistribution = () => {
    const distribution = {};
    config.PREDICTION_CLASSES.forEach(cls => {
      distribution[cls] = predictionHistory.filter(p => p.prediction === cls).length;
    });
    return distribution;
  };

  // Create activity timeline data
  const getActivityTimeline = () => {
    return predictionHistory.slice(0, 5).reverse().map((item, index) => ({
      time: new Date(item.created_at).toLocaleTimeString(),
      activity: item.prediction,
      duration: Math.floor(Math.random() * 60) + 10
    }));
  };

  return (
    <div className="prediction-page">
      <div className="prediction-header">
        <h1><FaRobot /> Water Activity Prediction</h1>
        <p>Predict water activities using ML model analysis</p>
      </div>

      <div className="prediction-container">
        {/* Left Column: Model Info & Input Form */}
        <div className="prediction-left">
          {/* Model Info Card */}
          <div className="model-info-card">
            <h2>Model Information</h2>
            {modelInfo ? (
              <div className="model-details">
                <div className="detail-row">
                  <span className="label">Model Type:</span>
                  <span className="value">{modelInfo.model_type}</span>
                </div>
                <div className="detail-row">
                  <span className="label">Version:</span>
                  <span className="value">{modelInfo.version}</span>
                </div>
                <div className="detail-row">
                  <span className="label">Accuracy:</span>
                  <span className="value">{(modelInfo.accuracy * 100).toFixed(1)}%</span>
                </div>
                <div className="detail-row">
                  <span className="label">Last Trained:</span>
                  <span className="value">{modelInfo.last_trained}</span>
                </div>
                <div className="detail-row">
                  <span className="label">Total Predictions:</span>
                  <span className="value">{modelInfo.total_predictions}</span>
                </div>
              </div>
            ) : (
              <p className="loading">Loading model info...</p>
            )}
          </div>

          {/* Input Form */}
          <form className="prediction-form" onSubmit={handlePredict}>
            <h2>Enter Sensor Data</h2>
            
            {error && <div className="error-message">{error}</div>}

            <div className="form-group">
              <label htmlFor="distance">Distance (cm) *</label>
              <input
                type="number"
                id="distance"
                name="distance"
                value={inputData.distance}
                onChange={handleInputChange}
                placeholder="e.g., 24.5"
                step="0.1"
                required
              />
              <small>Sensor distance reading (0-80 cm)</small>
            </div>

            <div className="form-group">
              <label htmlFor="temperature">Temperature (°C) *</label>
              <input
                type="number"
                id="temperature"
                name="temperature"
                value={inputData.temperature}
                onChange={handleInputChange}
                placeholder="e.g., 28.3"
                step="0.1"
                required
              />
              <small>Water temperature (20-40°C)</small>
            </div>

            <div className="form-group">
              <label htmlFor="water_percent">Water Level (%)</label>
              <input
                type="range"
                id="water_percent"
                name="water_percent"
                min="0"
                max="100"
                value={inputData.water_percent}
                onChange={handleInputChange}
              />
              <span className="value-display">{inputData.water_percent}%</span>
            </div>

            <div className="form-group">
              <label htmlFor="node_id">Node ID</label>
              <input
                type="text"
                id="node_id"
                name="node_id"
                value={inputData.node_id}
                onChange={handleInputChange}
                placeholder="e.g., node-1"
              />
            </div>

            <button 
              type="submit" 
              className="predict-button"
              disabled={loading}
            >
              {loading ? <><FaClock /> Predicting...</> : <><FaRocket /> Make Prediction</>}
            </button>
          </form>
        </div>

        {/* Right Column: Results & Charts */}
        <div className="prediction-right">
          {/* Prediction Results */}
          {prediction && (
            <div className="prediction-results-card">
              <h2>Prediction Results</h2>
              <div className="result-content">
                <div className="prediction-label">
                  <h3>Predicted Activity</h3>
                  <div className="activity-badge">
                    {prediction.prediction}
                  </div>
                </div>

                <ConfidenceGauge confidence={prediction.confidence} />

                <div className="result-details">
                  <div className="detail">
                    <span className="label">Status</span>
                    <span className="value" style={{color: config.THEME.success}}>
                      ✓ Successful
                    </span>
                  </div>
                  <div className="detail">
                    <span className="label">Timestamp</span>
                    <span className="value">
                      {new Date(prediction.timestamp).toLocaleString()}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          )}

          {!prediction && (
            <div className="no-results">
              <p><FaChartBar /> Enter sensor data and click "Make Prediction" to see results</p>
            </div>
          )}

          {/* Charts */}
          <div className="charts-section">
            <ActivityTimeline data={getActivityTimeline()} />
            <PredictionDistribution data={getPredictionDistribution()} />
          </div>
        </div>
      </div>
    </div>
  );
};

export default Prediction;
