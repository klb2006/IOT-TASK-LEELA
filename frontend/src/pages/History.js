import React, { useState, useEffect } from 'react';
import { FaChartLine, FaClock } from 'react-icons/fa';
import { apiEndpoints } from '../utils/api';
import '../styles/History.css';
import config from '../config';

const History = () => {
  const [predictions, setPredictions] = useState([]);
  const [sensorHistory, setSensorHistory] = useState([]);
  const [filter, setFilter] = useState('all');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [predRes, sensorRes] = await Promise.all([
        apiEndpoints.getPredictionsHistory(200),
        apiEndpoints.getSensorHistory(200)
      ]);
      setPredictions(predRes.data.data || []);
      setSensorHistory(sensorRes.data.data || []);
    } catch (err) {
      console.error('Error fetching history:', err);
    } finally {
      setLoading(false);
    }
  };

  const filteredPredictions = filter === 'all' 
    ? predictions 
    : predictions.filter(p => p.prediction === filter);

  const getPredictionStats = () => {
    const stats = {};
    config.PREDICTION_CLASSES.forEach(cls => {
      stats[cls] = predictions.filter(p => p.prediction === cls).length;
    });
    return stats;
  };

  return (
    <div className="history-page">
      <div className="page-header">
        <h1><FaChartLine /> Prediction & Sensor History</h1>
        <p>View historical data and predictions</p>
        <button className="refresh-button" onClick={fetchData}>
          <FaClock /> Refresh Data
        </button>
      </div>

      {loading ? (
        <div className="loading-spinner">Loading history...</div>
      ) : (
        <div className="history-container">
          {/* Stats Row */}
          <div className="history-stats">
            <div className="stat-item">
              <span className="stat-label">Total Predictions</span>
              <span className="stat-value">{predictions.length}</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Sensor Readings</span>
              <span className="stat-value">{sensorHistory.length}</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Avg Confidence</span>
              <span className="stat-value">
                {(predictions.reduce((sum, p) => sum + p.confidence, 0) / predictions.length * 100).toFixed(1)}%
              </span>
            </div>
          </div>

          {/* Prediction Activity Distribution */}
          <div className="distribution-section">
            <h2>Prediction Distribution</h2>
            <div className="distribution-bars">
              {Object.entries(getPredictionStats()).map(([activity, count]) => (
                <div key={activity} className="distribution-bar">
                  <div className="bar-label">{activity}</div>
                  <div className="bar-container">
                    <div
                      className="bar"
                      style={{
                        width: `${(count / predictions.length) * 100}%`,
                        backgroundColor: [
                          config.THEME.primary,
                          config.THEME.secondary,
                          config.THEME.accent,
                          config.THEME.success,
                          config.THEME.info
                        ][config.PREDICTION_CLASSES.indexOf(activity)]
                      }}
                    >
                      <span className="count">{count}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Filter & Tables */}
          <div className="history-content">
            {/* Predictions Table */}
            <div className="table-section">
              <div className="section-header">
                <h2>Prediction Records</h2>
                <select 
                  value={filter} 
                  onChange={(e) => setFilter(e.target.value)}
                  className="filter-select"
                >
                  <option value="all">All Activities</option>
                  {config.PREDICTION_CLASSES.map(cls => (
                    <option key={cls} value={cls}>{cls}</option>
                  ))}
                </select>
              </div>

              <table className="history-table">
                <thead>
                  <tr>
                    <th>#</th>
                    <th>Prediction</th>
                    <th>Confidence</th>
                    <th>Distance</th>
                    <th>Temperature</th>
                    <th>Timestamp</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredPredictions.slice(0, 50).map((pred, index) => (
                    <tr key={index}>
                      <td>{index + 1}</td>
                      <td>
                        <span className="prediction-badge">
                          {pred.prediction}
                        </span>
                      </td>
                      <td>
                        <div className="confidence-bar">
                          <div
                            className="confidence-fill"
                            style={{width: `${pred.confidence * 100}%`}}
                          ></div>
                          <span className="confidence-text">
                            {(pred.confidence * 100).toFixed(1)}%
                          </span>
                        </div>
                      </td>
                      <td>{pred.distance?.toFixed(2)} cm</td>
                      <td>{pred.temperature?.toFixed(1)}°C</td>
                      <td>{new Date(pred.created_at).toLocaleString()}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Sensor History Table */}
            <div className="table-section">
              <h2>Sensor Readings ({sensorHistory.length})</h2>
              <table className="history-table">
                <thead>
                  <tr>
                    <th>#</th>
                    <th>Distance</th>
                    <th>Temperature</th>
                    <th>Water %</th>
                    <th>Volume</th>
                    <th>Timestamp</th>
                  </tr>
                </thead>
                <tbody>
                  {sensorHistory.slice(0, 50).map((reading, index) => (
                    <tr key={index}>
                      <td>{index + 1}</td>
                      <td>{reading.distance?.toFixed(2)} cm</td>
                      <td>{reading.temperature?.toFixed(1)}°C</td>
                      <td>{reading.water_percentage?.toFixed(1)}%</td>
                      <td>{reading.water_liters?.toFixed(2)} L</td>
                      <td>{new Date(reading.timestamp).toLocaleString()}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default History;
