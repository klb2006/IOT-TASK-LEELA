import React, { useState, useEffect, useRef } from 'react';
import '../styles/SystemAssistant.css';

const SystemAssistant = ({ theme }) => {
  const [isOpen, setIsOpen] = useState(true);
  const [messages, setMessages] = useState([
    {
      id: 1,
      text: 'System Online',
      subtext: 'All sensors connected',
      type: 'success',
      icon: '●',
      timestamp: new Date(),
      delay: 0
    }
  ]);
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Simulate intelligent system messages
  useEffect(() => {
    const messageSequence = [
      {
        text: 'Water Level Stable',
        subtext: '72% — Within optimal range',
        type: 'success',
        icon: '✓',
        delay: 1500
      },
      {
        text: 'Temperature Normal',
        subtext: '28.5°C — Ideal conditions',
        type: 'info',
        icon: '↓',
        delay: 3000
      },
      {
        text: 'Sensor Data Fresh',
        subtext: 'Last update: 15 seconds ago',
        type: 'success',
        icon: '↻',
        delay: 4500
      },
      {
        text: 'ML Model Ready',
        subtext: 'Accuracy: 94.2% — Ready for predictions',
        type: 'success',
        icon: '◆',
        delay: 6000
      },
      {
        text: 'System Healthy',
        subtext: 'All systems operating optimally',
        type: 'success',
        icon: '★',
        delay: 7500
      }
    ];

    const timers = messageSequence.map(msg =>
      setTimeout(() => {
        setIsTyping(true);
        setTimeout(() => {
          setMessages(prev => [...prev, {
            id: prev.length + 1,
            ...msg,
            timestamp: new Date()
          }]);
          setIsTyping(false);
        }, 800);
      }, msg.delay)
    );

    return () => timers.forEach(timer => clearTimeout(timer));
  }, []);

  const getMessageStyles = (type) => {
    const styles = {
      success: { bgColor: 'rgba(16, 185, 129, 0.08)', borderColor: 'rgba(16, 185, 129, 0.3)', iconColor: '#10b981' },
      error: { bgColor: 'rgba(239, 68, 68, 0.08)', borderColor: 'rgba(239, 68, 68, 0.3)', iconColor: '#ef4444' },
      warning: { bgColor: 'rgba(245, 158, 11, 0.08)', borderColor: 'rgba(245, 158, 11, 0.3)', iconColor: '#f59e0b' },
      info: { bgColor: 'rgba(59, 130, 246, 0.08)', borderColor: 'rgba(59, 130, 246, 0.3)', iconColor: '#3b82f6' }
    };
    return styles[type] || styles.info;
  };

  return (
    <div className={`system-assistant ${!isOpen ? 'collapsed' : ''}`} data-theme={theme}>
      <div className="assistant-header" onClick={() => setIsOpen(!isOpen)}>
        <div className="assistant-header-content">
          <div className="assistant-pulse"></div>
          <div>
            <h3>System Intel</h3>
            <span className="assistant-status">Live</span>
          </div>
        </div>
        <button className="assistant-toggle">{isOpen ? '−' : '+'}</button>
      </div>

      {isOpen && (
        <div className="assistant-content">
          <div className="messages-stream">
            {messages.map((msg, idx) => {
              const styles = getMessageStyles(msg.type);
              return (
                <div
                  key={msg.id}
                  className="message-item"
                  style={{
                    backgroundColor: styles.bgColor,
                    borderColor: styles.borderColor,
                    animationDelay: `${idx * 100}ms`
                  }}
                  data-animation="slide-in"
                >
                  <div className="message-icon" style={{ color: styles.iconColor }}>
                    {msg.icon}
                  </div>
                  <div className="message-content">
                    <p className="message-title">{msg.text}</p>
                    <p className="message-subtext">{msg.subtext}</p>
                    <span className="message-timestamp">{msg.timestamp.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })}</span>
                  </div>
                </div>
              );
            })}

            {isTyping && (
              <div className="message-item typing-indicator" style={{
                backgroundColor: 'rgba(59, 130, 246, 0.05)',
                borderColor: 'rgba(59, 130, 246, 0.2)'
              }}>
                <div className="message-icon">
                  <span className="typing-dot"></span>
                  <span className="typing-dot"></span>
                  <span className="typing-dot"></span>
                </div>
                <div className="message-content">
                  <p className="message-title">Analyzing</p>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          <div className="assistant-footer">
            <p>Real-time system insights & alerts</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default SystemAssistant;
