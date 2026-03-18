import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { FaChartBar, FaBrain, FaChartLine, FaCog } from 'react-icons/fa';
import config from '../config';
import '../styles/Navbar.css';

const Navbar = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  return (
    <nav className="navbar">
      <div className="navbar-container">
        {/* Logo and College Name */}
        <div className="navbar-brand">
          <img 
            src={config.COLLEGE_LOGO} 
            alt="College Logo" 
            className="navbar-logo"
            onError={(e) => e.target.style.display = 'none'}
          />
          <Link to="/" className="navbar-title">
            <h1>{config.COLLEGE_NAME}</h1>
            <p>Water Tank Monitoring System</p>
          </Link>
        </div>

        {/* Mobile Menu Toggle */}
        <button 
          className="menu-toggle"
          onClick={() => setIsMenuOpen(!isMenuOpen)}
        >
          <span></span>
          <span></span>
          <span></span>
        </button>

        {/* Navigation Links */}
        <div className={`navbar-links ${isMenuOpen ? 'active' : ''}`}>
          <Link to="/" className="nav-link"><FaChartBar /> Dashboard</Link>
          <Link to="/prediction" className="nav-link"><FaBrain /> Predictions</Link>
          <Link to="/history" className="nav-link"><FaChartLine /> History</Link>
          <Link to="/settings" className="nav-link"><FaCog /> Settings</Link>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
