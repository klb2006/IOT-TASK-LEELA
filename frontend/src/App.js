import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Sidebar from './components/Sidebar';
import Home from './pages/Home';
import Prediction from './pages/Prediction';
import History from './pages/History';
import Settings from './pages/Settings';
import About from './pages/About';
import './styles/App.css';

function App() {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const toggleSidebar = () => {
    setSidebarOpen(!sidebarOpen);
  };

  return (
    <Router>
      <div className="app-layout">
        <Navbar onMenuClick={toggleSidebar} />
        <div className="main-container">
          <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />
          <main className="content">
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/prediction" element={<Prediction />} />
              <Route path="/history" element={<History />} />
              <Route path="/settings" element={<Settings />} />
              <Route path="/about" element={<About />} />
            </Routes>
          </main>
        </div>
      </div>
    </Router>
  );
}

export default App;
