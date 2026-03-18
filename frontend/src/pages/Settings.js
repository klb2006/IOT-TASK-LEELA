import React from 'react';
import { FaCog, FaSave, FaClock } from 'react-icons/fa';
import '../styles/Settings.css';

const Settings = () => {
  return (
    <div className="settings-page">
      <div className="page-header">
        <h1><FaCog /> Settings</h1>
        <p>Configure system settings and preferences</p>
      </div>

      <div className="settings-container">
        <div className="settings-section">
          <h2>Backend Configuration</h2>
          <div className="setting-item">
            <label>API Base URL:</label>
            <input 
              type="text" 
              value={process.env.REACT_APP_API_BASE_URL || 'http://127.0.0.1:8000'} 
              readOnly 
            />
          </div>
          <div className="setting-item">
            <label>Auto Refresh Interval:</label>
            <select>
              <option>30 seconds</option>
              <option>1 minute</option>
              <option>5 minutes</option>
              <option>Disabled</option>
            </select>
          </div>
        </div>

        <div className="settings-section">
          <h2>Display Settings</h2>
          <div className="setting-item">
            <label>Theme:</label>
            <select>
              <option>Light</option>
              <option>Dark</option>
              <option>Auto</option>
            </select>
          </div>
          <div className="setting-item">
            <label>Language:</label>
            <select>
              <option>English</option>
              <option>Hindi</option>
              <option>Spanish</option>
            </select>
          </div>
        </div>

        <div className="settings-section">
          <h2>Prediction Settings</h2>
          <div className="setting-item">
            <label>Default Node ID:</label>
            <input type="text" placeholder="node-1" defaultValue="node-1" />
          </div>
          <div className="setting-item">
            <label>History Limit:</label>
            <input type="number" placeholder="100" defaultValue="100" />
          </div>
        </div>

        <div className="settings-actions">
          <button className="btn-save"><FaSave /> Save Settings</button>
          <button className="btn-reset"><FaClock /> Reset to Defaults</button>
        </div>
      </div>
    </div>
  );
};

export default Settings;
