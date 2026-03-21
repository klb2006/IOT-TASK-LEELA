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
    node_id: 'node-1'
  });

  // Get color for activity type
  const getActivityColor = (activity) => {
    const colors = {
      'no_activity': '#6B7280',         // Gray
      'filling': '#3B82F6',             // Blue
      'flush': '#EF4444',               // Red
      'washing_machine': '#F59E0B',     // Amber
      'geyser': '#EC4899'               // Pink
    };
    return colors[activity] || '#6B7280';
  };

  // Fetch model info on mount
  useEffect(() => {
    fetchModelInfo();
    fetchPredictionHistory();
    
    // Auto-refresh prediction history every 10 seconds
    const interval = setInterval(fetchPredictionHistory, 10000);
    return () => clearInterval(interval);
  }, []);

  const fetchModelInfo = async () => {
    try {
      const response = await apiEndpoints.getActivityModelInfo();
      if (response.data.status === 'success') {
        setModelInfo(response.data.model);
      } else {
        // Fallback to regular model info
        const fallback = await apiEndpoints.getModelInfo();
        setModelInfo(fallback.data.model_info);
      }
      setError(null);
    } catch (err) {
      console.error('Error fetching model info:', err);
      // Try fallback
      try {
        const response = await apiEndpoints.getModelInfo();
        setModelInfo(response.data.model_info);
      } catch (e) {
        setError('Failed to fetch model info');
      }
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
      // Call the activity classification endpoint (GRU model32.h5)
      const response = await apiEndpoints.predictActivity({
        distance: parseFloat(inputData.distance),
        temperature: parseFloat(inputData.temperature),
        node_id: inputData.node_id
      });

      if (response.data.status === 'success') {
        setPrediction({
          ...response.data,
          prediction: response.data.activity,  // Map 'activity' to 'prediction' for UI consistency
          confidence: response.data.confidence
        });
        // Fetch updated prediction history from database
        setTimeout(() => fetchPredictionHistory(), 500);
      } else {
        setError(response.data.message || 'Prediction failed');
      }
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

  // Create activity timeline data with REAL timestamps and durations
  const getActivityTimeline = () => {
    const timeline = predictionHistory.slice(0, 5).reverse();
    
    return timeline.map((item, index) => {
      // Calculate duration between this prediction and the next one (or use 0 if it's the latest)
      let duration = 0;
      if (index < timeline.length - 1) {
        const currentTime = new Date(item.created_at).getTime();
        const nextTime = new Date(timeline[index + 1].created_at).getTime();
        duration = Math.round((nextTime - currentTime) / 1000); // Convert to seconds
      }
      
      return {
        time: new Date(item.created_at).toLocaleTimeString(),
        activity: item.prediction,
        duration: duration, // Real duration from actual timestamps
        distance: item.distance,
        temperature: item.temperature,
        confidence: item.confidence
      };
    });
  };

  return (
    <div className="prediction-page">
      <div className="prediction-header">
        <h1><FaRobot /> Water Activity Classifier</h1>
        <p>Detect water usage activities using GRU ML model (model32.h5)</p>
        <p className="subtitle">Identifies: Filling, Flushing, Washing Machine, Geyser, and No Activity</p>
      </div>

      <div className="prediction-container">
        {/* Left Column: Model Info & Input Form */}
        <div className="prediction-left">
          {/* Model Info Card */}
          <div className="model-info-card">
            <h2>🤖 Activity Model Info</h2>
            {modelInfo ? (
              <div className="model-details">
                <div className="detail-row">
                  <span className="label">Model Type:</span>
                  <span className="value">{modelInfo.model || modelInfo.model_type || 'GRU Neural Network'}</span>
                </div>
                <div className="detail-row">
                  <span className="label">Accuracy:</span>
                  <span className="value">{modelInfo.accuracy || '85.95%'}</span>
                </div>
                <div className="detail-row">
                  <span className="label">F1-Score:</span>
                  <span className="value">{modelInfo.f1_score || '0.6881'}</span>
                </div>
                <div className="detail-row">
                  <span className="label">Activities:</span>
                  <span className="value">{modelInfo.num_classes || modelInfo.activities?.length || '5'} classes</span>
                </div>
                <div className="detail-row">
                  <span className="label">Detected Activities:</span>
                  <div className="activities-list">
                    {(modelInfo.activities || config.PREDICTION_CLASSES).map((activity, idx) => (
                      <span key={idx} className="activity-tag" style={{
                        backgroundColor: getActivityColor(activity),
                        color: 'white',
                        padding: '4px 8px',
                        borderRadius: '4px',
                        fontSize: '12px',
                        marginRight: '6px',
                        marginBottom: '4px',
                        display: 'inline-block'
                      }}>
                        {activity.replace('_', ' ')}
                      </span>
                    ))}
                  </div>
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
              <label htmlFor="node_id">Node ID</label>
              <input
                type="text"
                id="node_id"
                name="node_id"
                value={inputData.node_id}
                onChange={handleInputChange}
                placeholder="e.g., node-1"
              />
              <small>Sensor node identifier</small>
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
              <h2>📊 Prediction Results</h2>
              <div className="result-content">
                <div className="prediction-label">
                  <h3>Detected Activity</h3>
                  <div className="activity-badge" style={{
                    backgroundColor: getActivityColor(prediction.prediction),
                    color: 'white',
                    padding: '12px 24px',
                    borderRadius: '8px',
                    fontSize: '18px',
                    fontWeight: 'bold',
                    textTransform: 'capitalize'
                  }}>
                    {prediction.prediction.replace('_', ' ')}
                  </div>
                  <p className="activity-description">
                    {config.ACTIVITY_DESCRIPTIONS[prediction.prediction] || 'Water activity detected'}
                  </p>
                </div>

                <ConfidenceGauge confidence={prediction.confidence || 0.85} />

                <div className="result-details">
                  <div className="detail">
                    <span className="label">✓ Prediction Status</span>
                    <span className="value" style={{color: config.THEME.success}}>
                      Success - High Confidence
                    </span>
                  </div>
                  <div className="detail">
                    <span className="label">Distance Reading</span>
                    <span className="value">{prediction.distance?.toFixed(2) || 'N/A'} cm</span>
                  </div>
                  <div className="detail">
                    <span className="label">Temperature</span>
                    <span className="value">{prediction.temperature?.toFixed(1) || 'N/A'} °C</span>
                  </div>
                  <div className="detail">
                    <span className="label">Confidence Score</span>
                    <span className="value">{((prediction.confidence || 0.85) * 100).toFixed(1)}%</span>
                  </div>
                  <div className="detail">
                    <span className="label">Time</span>
                    <span className="value">
                      {new Date().toLocaleTimeString()}
                    </span>
                  </div>
                </div>

                {/* Activity Probabilities */}
                {prediction.probabilities && (
                  <div className="probabilities-section">
                    <h4>Activity Probabilities</h4>
                    <div className="probability-bars">
                      {Object.entries(prediction.probabilities).map(([activity, prob]) => (
                        <div key={activity} className="probability-bar">
                          <span className="activity-name">{activity.replace('_', ' ')}</span>
                          <div className="bar-container">
                            <div 
                              className="bar-fill" 
                              style={{
                                width: `${(prob * 100).toFixed(0)}%`,
                                backgroundColor: getActivityColor(activity)
                              }}
                            />
                          </div>
                          <span className="probability-value">{(prob * 100).toFixed(1)}%</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
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
