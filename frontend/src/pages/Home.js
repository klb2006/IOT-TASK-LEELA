import React, { useState, useEffect } from 'react';
import { apiEndpoints } from '../utils/api';
import '../styles/Home.css';
import config from '../config';
import { FaRuler, FaThermometerHalf, FaTint, FaVial, FaSync, FaCheckCircle, FaServer, FaBrain, FaSignal } from 'react-icons/fa';

const Home = () => {
  const [sensorData, setSensorData] = useState(null);
  const [sensorHistory, setSensorHistory] = useState([]);
  const [modelInfo, setModelInfo] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isRefreshing, setIsRefreshing] = useState(false);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchData = async () => {
    setIsRefreshing(true);
    try {
      const [sensorRes, historyRes, modelRes] = await Promise.all([
        apiEndpoints.getLatestSensorData(),
        apiEndpoints.getSensorHistory(20),
        apiEndpoints.getModelInfo()
      ]);

      setSensorData(sensorRes.data.data);
      setSensorHistory(historyRes.data.data || []);
      setModelInfo(modelRes.data.model_info);
      setError(null);
    } catch (err) {
      setError('Unable to fetch data. Please ensure backend is running.');
      console.error('Error:', err);
    } finally {
      setLoading(false);
      setIsRefreshing(false);
    }
  };

  const getStatusLevel = (value, min, max) => {
    const percentage = ((value - min) / (max - min)) * 100;
    if (percentage >= 80) return 'High';
    if (percentage >= 50) return 'Normal';
    if (percentage >= 20) return 'Warning';
    return 'Critical';
  };

  return (
    <div className="home-page">
      {/* Header Section */}
      <div className="dashboard-header">
        <div className="header-left">
          <h1 className="header-title">Water Tank Monitoring - {config.COLLEGE_NAME}</h1>
          <p className="header-subtitle">Real-time sensor data and analytics</p>
        </div>
        <div className="header-right">
          <button 
            className="refresh-btn"
            onClick={fetchData}
            disabled={isRefreshing}
          >
            {isRefreshing ? 'Refreshing...' : 'Refresh'}
          </button>
        </div>
      </div>

      {/* Error Banner */}
      {error && (
        <div className="error-banner">
          {error}
        </div>
      )}

      {/* Loading State */}
      {loading ? (
        <div className="loading">Loading data...</div>
      ) : (
        <>
          {/* Metric Cards */}
          <div className="metrics-grid">
            <div className="metric-card">
              <div className="metric-icon"><FaRuler /></div>
              <div className="metric-label">Distance</div>
              <div className="metric-value">
                {sensorData?.distance?.toFixed(2) || '—'} cm
              </div>
              <div className="metric-status">
                {getStatusLevel(sensorData?.distance || 0, 0, 200)}
              </div>
              <div className="progress-bar">
                <div 
                  className="progress-fill"
                  style={{
                    width: `${Math.min((sensorData?.distance || 0) / 200 * 100, 100)}%`
                  }}
                ></div>
              </div>
            </div>

            <div className="metric-card">
              <div className="metric-icon"><FaThermometerHalf /></div>
              <div className="metric-label">Temperature</div>
              <div className="metric-value">
                {sensorData?.temperature?.toFixed(1) || '—'} °C
              </div>
              <div className="metric-status">
                {getStatusLevel(sensorData?.temperature || 0, 0, 40)}
              </div>
              <div className="progress-bar">
                <div 
                  className="progress-fill"
                  style={{
                    width: `${Math.min((sensorData?.temperature || 0) / 40 * 100, 100)}%`
                  }}
                ></div>
              </div>
            </div>

            <div className="metric-card">
              <div className="metric-icon"><FaTint /></div>
              <div className="metric-label">Water Level</div>
              <div className="metric-value">
                {sensorData?.water_percentage?.toFixed(1) || '—'} %
              </div>
              <div className="metric-status">
                {getStatusLevel(sensorData?.water_percentage || 0, 0, 100)}
              </div>
              <div className="progress-bar">
                <div 
                  className="progress-fill"
                  style={{
                    width: `${sensorData?.water_percentage || 0}%`
                  }}
                ></div>
              </div>
            </div>

            <div className="metric-card">
              <div className="metric-icon"><FaVial /></div>
              <div className="metric-label">Water Volume</div>
              <div className="metric-value">
                {sensorData?.water_liters?.toFixed(2) || '—'} L
              </div>
              <div className="metric-status">Active</div>
              <div className="progress-bar">
                <div 
                  className="progress-fill"
                  style={{
                    width: `${Math.min((sensorData?.water_liters || 0) / 100 * 100, 100)}%`
                  }}
                ></div>
              </div>
            </div>
          </div>

          {/* Recent Readings */}
          <div className="content-section">
            <h2>Recent Readings</h2>
            <div className="readings-table">
              <table>
                <thead>
                  <tr>
                    <th>Time</th>
                    <th>Distance (cm)</th>
                    <th>Temperature (C)</th>
                    <th>Water Level (%)</th>
                  </tr>
                </thead>
                <tbody>
                  {sensorHistory.slice(0, 10).map((reading, index) => (
                    <tr key={index}>
                      <td>{new Date(reading.timestamp).toLocaleTimeString()}</td>
                      <td>{reading.distance?.toFixed(2)}</td>
                      <td>{reading.temperature?.toFixed(1)}</td>
                      <td>{reading.water_percentage?.toFixed(1)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Model Status & System Health */}
          <div className="info-grid">
            <div className="info-card">
              <h3>Model Status</h3>
              {modelInfo ? (
                <div className="info-content">
                  <div className="info-row">
                    <span className="label">Type:</span>
                    <span className="value">{modelInfo.model_type}</span>
                  </div>
                  <div className="info-row">
                    <span className="label">Version:</span>
                    <span className="value">{modelInfo.version}</span>
                  </div>
                  <div className="info-row">
                    <span className="label">Accuracy:</span>
                    <span className="value">{(modelInfo.accuracy * 100).toFixed(1)}%</span>
                  </div>
                  <div className="info-row">
                    <span className="label">Predictions:</span>
                    <span className="value">{modelInfo.total_predictions}</span>
                  </div>
                </div>
              ) : (
                <p>Loading model information...</p>
              )}
            </div>

            <div className="info-card">
              <h3>System Status</h3>
              <div className="status-list">
                <div className="status-item ok"><FaServer /> Database: Connected</div>
                <div className="status-item ok"><FaServer /> API Server: Running</div>
                <div className="status-item ok"><FaBrain /> ML Model: Loaded</div>
                <div className="status-item ok"><FaSignal /> Sensors: Connected</div>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default Home;
