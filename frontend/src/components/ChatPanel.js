import React, { useState, useEffect, useRef } from 'react';
import { FaComment } from 'react-icons/fa';
import '../styles/ChatPanel.css';

const ChatPanel = ({ theme }) => {
  const [isOpen, setIsOpen] = useState(true);
  const [messages, setMessages] = useState([
    { id: 1, text: 'System initialized successfully', timestamp: new Date(), type: 'info' },
    { id: 2, text: 'Connecting to sensor network...', timestamp: new Date(), type: 'loading' }
  ]);
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Simulate incoming messages
  useEffect(() => {
    const simulateMessages = [
      { text: 'Sensor connected successfully', type: 'success', delay: 2000 },
      { text: 'Receiving real-time data...', type: 'info', delay: 4000 },
      { text: 'Water level updated: 72%', type: 'update', delay: 6000 },
      { text: 'Temperature: 28.5°C', type: 'update', delay: 8000 },
      { text: 'ML model ready for predictions', type: 'success', delay: 10000 }
    ];

    const timers = simulateMessages.map(msg => 
      setTimeout(() => {
        setIsTyping(true);
        setTimeout(() => {
          setMessages(prev => [...prev, {
            id: prev.length + 1,
            text: msg.text,
            timestamp: new Date(),
            type: msg.type
          }]);
          setIsTyping(false);
        }, 1200);
      }, msg.delay)
    );

    return () => timers.forEach(timer => clearTimeout(timer));
  }, []);

  const getMessageIcon = (type) => {
    const icons = {
      success: '✓',
      error: '✕',
      warning: '!',
      info: 'i',
      loading: '»',
      update: '●'
    };
    return icons[type] || '●';
  };

  const formatTime = (date) => {
    return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <div className={`chat-panel ${!isOpen ? 'collapsed' : ''}`} data-theme={theme}>
      <div className="chat-header" onClick={() => setIsOpen(!isOpen)}>
        <div className="chat-title">
          <span className="chat-icon"><FaComment /></span>
          <div>
            <h3>System Monitor</h3>
            <span className="chat-status">Live Updates</span>
          </div>
        </div>
        <button className="chat-toggle">{isOpen ? '−' : '+'}</button>
      </div>

      {isOpen && (
        <div className="chat-content">
          <div className="messages-container">
            {messages.map(msg => (
              <div key={msg.id} className={`message message-${msg.type}`} data-animation="slide-in">
                <div className="message-icon">{getMessageIcon(msg.type)}</div>
                <div className="message-body">
                  <p className="message-text">{msg.text}</p>
                  <span className="message-time">{formatTime(msg.timestamp)}</span>
                </div>
              </div>
            ))}

            {isTyping && (
              <div className="message message-loading">
                <div className="message-icon">⟳</div>
                <div className="message-body">
                  <div className="typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          <div className="chat-footer">
            <p className="footer-text">Real-time system notifications</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default ChatPanel;
