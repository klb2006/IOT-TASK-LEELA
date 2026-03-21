import React from 'react';
import { FaInfoCircle, FaEnvelope, FaBuilding, FaLink } from 'react-icons/fa';
import '../styles/About.css';
import config from '../config';

const About = () => {
  return (
    <div className="about-page">
      <div className="about-header">
        <h1><FaInfoCircle /> About Water Tank Monitoring System</h1>
        <p>Smart IoT Solution for Real-time Water Quality Assessment</p>
      </div>

      <div className="about-container">
        <div className="about-section">
          <h2>System Overview</h2>
          <p>
            The Water Tank Monitoring System is an intelligent IoT solution that combines
            sensor data analysis with machine learning to predict water activities and 
            monitor tank levels in real-time.
          </p>
          <p>
            This system uses advanced LSTM neural networks to predict water usage patterns
            and activities, enabling efficient resource management and early anomaly detection.
          </p>
        </div>

        <div className="about-section">
          <h2>Key Features</h2>
          <ul className="features-list">
            <li>✓ Real-time sensor data collection</li>
            <li>✓ ML-powered activity prediction</li>
            <li>✓ Historical data tracking</li>
            <li>✓ Interactive dashboards</li>
            <li>✓ RESTful API backend</li>
            <li>✓ Multi-node support</li>
            <li>✓ Responsive web interface</li>
            <li>✓ PostgreSQL database</li>
          </ul>
        </div>

        <div className="about-section">
          <h2>Technology Stack</h2>
          <div className="tech-stack">
            <div className="tech-category">
              <h3>Frontend</h3>
              <p>React.js • CSS3 • Responsive Design</p>
            </div>
            <div className="tech-category">
              <h3>Backend</h3>
              <p>FastAPI • Python • PostgreSQL</p>
            </div>
            <div className="tech-category">
              <h3>Machine Learning</h3>
              <p>TensorFlow • Keras • LSTM Networks</p>
            </div>
            <div className="tech-category">
              <h3>IoT & Sensors</h3>
              <p>Ultrasonic Sensors • Temperature Sensors</p>
            </div>
          </div>
        </div>

        <div className="about-section">
          <h2>System Information</h2>
          <div className="system-info">
            <div className="info-row">
              <span className="label">College:</span>
              <span className="value">{config.COLLEGE_NAME}</span>
            </div>
            <div className="info-row">
              <span className="label">System Version:</span>
              <span className="value">1.0.0</span>
            </div>
            <div className="info-row">
              <span className="label">API Version:</span>
              <span className="value">v1</span>
            </div>
            <div className="info-row">
              <span className="label">Database:</span>
              <span className="value">PostgreSQL</span>
            </div>
            <div className="info-row">
              <span className="label">ML Model:</span>
              <span className="value">LSTM Neural Network</span>
            </div>
          </div>
        </div>

        <div className="about-section">
          <h2>Contact & Support</h2>
          <p>
            For issues, feature requests, or general inquiries, please contact the
            development team through the official channels.
          </p>
          <div className="contact-info">
            <p><FaEnvelope /> Email: support@college.edu</p>
            <p><FaBuilding /> College: {config.COLLEGE_NAME}</p>
            <p><FaLink /> Repository: GitHub</p>
          </div>
        </div>

        <div className="about-footer">
          <p>&copy; 2026 {config.COLLEGE_NAME}. All rights reserved.</p>
        </div>
      </div>
    </div>
  );
};

export default About;
