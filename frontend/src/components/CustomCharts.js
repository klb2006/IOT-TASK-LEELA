import React from 'react';
import '../styles/Charts.css';
import config from '../config';

// Confidence Gauge Component
export const ConfidenceGauge = ({ confidence = 0.85 }) => {
  const percentage = (confidence * 100).toFixed(1);
  const radius = 45;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (percentage / 100) * circumference;

  const getColor = () => {
    if (percentage >= 80) return config.THEME.success;
    if (percentage >= 60) return config.THEME.info;
    if (percentage >= 40) return config.THEME.warning;
    return config.THEME.warning;
  };

  return (
    <div className="confidence-gauge">
      <svg width="150" height="150" viewBox="0 0 150 150">
        {/* Background circle */}
        <circle
          cx="75"
          cy="75"
          r={radius}
          fill="none"
          stroke={config.THEME.light}
          strokeWidth="8"
        />
        {/* Progress circle */}
        <circle
          cx="75"
          cy="75"
          r={radius}
          fill="none"
          stroke={getColor()}
          strokeWidth="8"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
          transform="rotate(-90 75 75)"
          style={{ transition: 'stroke-dashoffset 0.5s ease' }}
        />
        {/* Text */}
        <text
          x="75"
          y="75"
          textAnchor="middle"
          dy="0.3em"
          className="gauge-text"
          fill={config.THEME.dark}
        >
          {percentage}%
        </text>
      </svg>
      <p className="gauge-label">Confidence</p>
    </div>
  );
};

// Activity Timeline Chart
export const ActivityTimeline = ({ data = [] }) => {
  if (data.length === 0) {
    return (
      <div className="chart-container">
        <p className="no-data">No activity data available</p>
      </div>
    );
  }

  const maxDuration = Math.max(...data.map(d => d.duration || 0));

  return (
    <div className="activity-timeline">
      <h3>Activity Timeline</h3>
      <div className="timeline-bars">
        {data.map((item, index) => (
          <div key={index} className="timeline-item">
            <div className="timeline-label">{item.time || `Event ${index + 1}`}</div>
            <div className="bar-container">
              <div
                className="bar"
                style={{
                  width: `${(item.duration / maxDuration) * 100}%`,
                  backgroundColor: config.THEME.primary
                }}
              >
                <span className="bar-value">{item.duration}s</span>
              </div>
            </div>
            <div className="bar-label">{item.activity || 'Unknown'}</div>
          </div>
        ))}
      </div>
    </div>
  );
};

// Prediction Distribution Pie Chart
export const PredictionDistribution = ({ data = {} }) => {
  const chartData = Object.entries(data).map(([key, value]) => ({
    name: key,
    value: value
  }));

  if (chartData.length === 0) {
    return (
      <div className="chart-container">
        <p className="no-data">No prediction data available</p>
      </div>
    );
  }

  const total = chartData.reduce((sum, item) => sum + item.value, 0);
  const colors = [
    config.THEME.primary,
    config.THEME.secondary,
    config.THEME.accent,
    config.THEME.success,
    config.THEME.info
  ];

  return (
    <div className="prediction-distribution">
      <h3>Prediction Distribution</h3>
      <div className="pie-chart">
        <svg width="200" height="200" viewBox="0 0 200 200">
          {chartData.map((item, index) => {
            const percentage = (item.value / total) * 100;
            const radius = 80;
            const angle = (percentage / 100) * Math.PI * 2;
            const x = 100 + radius * Math.cos(angle - Math.PI / 2);
            const y = 100 + radius * Math.sin(angle - Math.PI / 2);
            
            return (
              <g key={index}>
                <circle
                  cx="100"
                  cy="100"
                  r={radius}
                  fill={colors[index % colors.length]}
                  opacity={0.8}
                />
              </g>
            );
          })}
        </svg>
      </div>
      <div className="legend">
        {chartData.map((item, index) => (
          <div key={index} className="legend-item">
            <span
              className="legend-color"
              style={{ backgroundColor: colors[index % colors.length] }}
            ></span>
            <span className="legend-text">{item.name}: {item.value}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default { ConfidenceGauge, ActivityTimeline, PredictionDistribution };
