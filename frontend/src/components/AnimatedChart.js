import React from 'react';
import '../styles/AnimatedChart.css';

const AnimatedChart = ({ type = 'line', data = [], title, theme }) => {
  // Generate simple SVG chart
  const width = 100;
  const height = 60;
  const padding = 4;
  const chartWidth = width - padding * 2;
  const chartHeight = height - padding * 2;

  // Normalize data to fit in chart
  const maxValue = Math.max(...data.map(d => d.value), 100);
  const points = data.map((d, i) => {
    const x = padding + (i / Math.max(data.length - 1, 1)) * chartWidth;
    const y = height - padding - (d.value / maxValue) * chartHeight;
    return { x, y, value: d.value };
  });

  // Create SVG path
  const pathD = points.length > 1
    ? `M ${points[0].x},${points[0].y} ${points.map(p => `L ${p.x},${p.y}`).join(' ')}`
    : '';

  // Create gradient area
  const areaD = points.length > 1
    ? `M ${points[0].x},${points[0].y} ${points.map(p => `L ${p.x},${p.y}`).join(' ')} L ${points[points.length - 1].x},${height - padding} L ${points[0].x},${height - padding} Z`
    : '';

  const getThemeColors = () => {
    const colors = {
      light: { line: '#1e3a8a', fill: 'rgba(30, 58, 138, 0.1)', text: '#111827' },
      dark: { line: '#60a5fa', fill: 'rgba(96, 165, 250, 0.1)', text: '#f1f5f9' },
      blue: { line: '#0052cc', fill: 'rgba(0, 82, 204, 0.1)', text: '#001a4d' },
      eco: { line: '#059669', fill: 'rgba(5, 150, 105, 0.1)', text: '#1b3a1b' }
    };
    return colors[theme] || colors.light;
  };

  const colors = getThemeColors();

  return (
    <div className="chart-wrapper">
      {title && <h4 className="chart-title">{title}</h4>}
      
      <div className="chart-container">
        <svg viewBox={`0 0 ${width} ${height}`} className="chart-svg">
          <defs>
            <linearGradient id="chartGradient" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stopColor={colors.line} stopOpacity="0.3" />
              <stop offset="100%" stopColor={colors.line} stopOpacity="0" />
            </linearGradient>
          </defs>

          {/* Grid lines */}
          <line x1={padding} y1={padding} x2={width - padding} y2={padding} stroke={colors.fill} strokeWidth="0.3" />
          <line x1={padding} y1={height - padding} x2={width - padding} y2={height - padding} stroke={colors.fill} strokeWidth="0.3" />

          {/* Area fill */}
          {areaD && (
            <path d={areaD} fill="url(#chartGradient)" />
          )}

          {/* Line */}
          {pathD && (
            <path
              d={pathD}
              fill="none"
              stroke={colors.line}
              strokeWidth="1.5"
              strokeLinecap="round"
              strokeLinejoin="round"
              className="chart-line"
            />
          )}

          {/* Data points */}
          {points.map((p, i) => (
            <circle key={i} cx={p.x} cy={p.y} r="0.8" fill={colors.line} className="chart-point" />
          ))}
        </svg>
      </div>

      {/* Data labels */}
      <div className="chart-labels">
        {data.slice(0, 3).map((d, i) => (
          <span key={i} className="chart-label">
            {d.label}: <strong>{d.value}</strong>{d.unit}
          </span>
        ))}
      </div>
    </div>
  );
};

export default AnimatedChart;
