// Simple Clean Configuration
const config = {
  API_BASE_URL: process.env.REACT_APP_API_BASE_URL || 'https://iot-task-leela.onrender.com',
  API_TIMEOUT: 10000,
  
  // College Branding
  COLLEGE_NAME: 'KIET',
  COLLEGE_LOGO: '/logo.png',
  
  // Premium Theme System - Multiple professional themes
  THEMES: {
    light: {
      name: 'Light',
      bg: '#ffffff',
      bgSecondary: '#f8f9fb',
      bgTertiary: '#f0f1f5',
      text: '#111827',
      textSecondary: '#6b7280',
      textTertiary: '#9ca3af',
      border: '#e5e7eb',
      card: '#ffffff',
      cardHover: '#f9fafb',
      primary: '#1e3a8a',
      primaryLight: '#eff6ff',
      secondary: '#dc2626',
      success: '#10b981',
      warning: '#f59e0b',
      error: '#ef4444',
      info: '#3b82f6',
      accent: '#8b5cf6',
      shadow: 'rgba(0, 0, 0, 0.08)',
      shadowHover: 'rgba(0, 0, 0, 0.12)',
    },
    dark: {
      name: 'Dark',
      bg: '#0f172a',
      bgSecondary: '#1e293b',
      bgTertiary: '#334155',
      text: '#f1f5f9',
      textSecondary: '#cbd5e1',
      textTertiary: '#94a3b8',
      border: '#334155',
      card: '#1e293b',
      cardHover: '#334155',
      primary: '#60a5fa',
      primaryLight: '#1e3a5f',
      secondary: '#f87171',
      success: '#4ade80',
      warning: '#fbbf24',
      error: '#f87171',
      info: '#60a5fa',
      accent: '#a78bfa',
      shadow: 'rgba(0, 0, 0, 0.3)',
      shadowHover: 'rgba(0, 0, 0, 0.5)',
    },
    blue: {
      name: 'Professional Blue',
      bg: '#f0f4f8',
      bgSecondary: '#ffffff',
      bgTertiary: '#e8eef8',
      text: '#001a4d',
      textSecondary: '#4a5f7f',
      textTertiary: '#7a8fa3',
      border: '#d0dce6',
      card: '#ffffff',
      cardHover: '#f5f9ff',
      primary: '#0052cc',
      primaryLight: '#e6f0ff',
      secondary: '#0066ff',
      success: '#28a745',
      warning: '#ff9800',
      error: '#dc3545',
      info: '#17a2b8',
      accent: '#6c5ce7',
      shadow: 'rgba(0, 52, 204, 0.1)',
      shadowHover: 'rgba(0, 52, 204, 0.15)',
    },
    eco: {
      name: 'Eco Green',
      bg: '#f0fdf4',
      bgSecondary: '#ffffff',
      bgTertiary: '#e0fce0',
      text: '#1b3a1b',
      textSecondary: '#4a6f4a',
      textTertiary: '#7a9f7a',
      border: '#bbf7d0',
      card: '#ffffff',
      cardHover: '#f5fffb',
      primary: '#059669',
      primaryLight: '#ecfdf5',
      secondary: '#10b981',
      success: '#34d399',
      warning: '#f59e0b',
      error: '#ef4444',
      info: '#06b6d4',
      accent: '#14b8a6',
      shadow: 'rgba(16, 185, 129, 0.1)',
      shadowHover: 'rgba(16, 185, 129, 0.15)',
    }
  },
  
  // Default active theme
  DEFAULT_THEME: 'light',
  
  // Get theme configuration
  get THEME() {
    return this.THEMES[this.DEFAULT_THEME];
  },
  
  // Prediction Classes
  PREDICTION_CLASSES: [
    'no_activity',
    'shower',
    'faucet',
    'toilet',
    'dishwasher'
  ],
  
  // Metric configurations
  METRICS: {
    distance: {
      name: 'Distance',
      unit: 'cm',
      icon: 'FaRuler',
      min: 0,
      max: 200,
      color: '#3b82f6'
    },
    temperature: {
      name: 'Temperature',
      unit: '°C',
      icon: 'FaThermometerHalf',
      min: 0,
      max: 40,
      color: '#ef4444'
    },
    water_level: {
      name: 'Water Level',
      unit: '%',
      icon: 'FaTint',
      min: 0,
      max: 100,
      color: '#10b981'
    },
    water_volume: {
      name: 'Water Volume',
      unit: 'L',
      icon: 'FaVial',
      min: 0,
      max: 10000,
      color: '#8b5cf6'
    }
  }
};

export default config;
