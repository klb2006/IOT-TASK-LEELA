import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Ruler, Thermometer, Droplets, Waves, Wifi, WifiOff } from 'lucide-react';
import SensorCard from '../components/SensorCard';
import WaterLevelIndicator from '../components/WaterLevelIndicator';
import ProgressBar from '../components/ProgressBar';
import PredictionCard from '../components/PredictionCard';
import { useSensorData, useServerStatus } from '../hooks/useSensorData';

const Dashboard = () => {
  const { data: sensorData, loading, error, isConnected } = useSensorData();
  const { status: serverStatus, isConnected: isServerConnected } = useServerStatus();
  
  // Default values while loading
  const displayData = sensorData ? {
    distance: parseFloat(sensorData.distance) || 0,
    temperature: parseFloat(sensorData.temperature) || 0,
    waterPercentage: parseFloat(sensorData.water_percentage) || 0,
    waterLevel: parseFloat(sensorData.water_liters) || 0,
    timestamp: sensorData.timestamp || 'N/A'
  } : {
    distance: 0,
    temperature: 0,
    waterPercentage: 0,
    waterLevel: 0,
    timestamp: 'No data'
  };

  return (
    <div className="min-h-screen pt-28 pb-12 px-6 lg:px-12 max-w-7xl mx-auto">
      {/* Connection Status Banner */}
      <motion.div 
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        className={`mb-6 p-4 rounded-lg flex items-center gap-3 ${
          isServerConnected 
            ? 'bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-100' 
            : 'bg-red-100 dark:bg-red-900 text-red-800 dark:text-red-100'
        }`}
      >
        {isServerConnected ? (
          <Wifi className="w-5 h-5" />
        ) : (
          <WifiOff className="w-5 h-5" />
        )}
        <div>
          <span className="font-semibold">
            {isServerConnected ? '✓ Connected to Backend Server' : '✗ Disconnected from Backend'}
          </span>
          <p className="text-sm">
            {isServerConnected ? 'Database: Connected' : 'Attempting to connect...'}
          </p>
        </div>
      </motion.div>

      <header className="mb-10">
        <motion.h1 
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          className="text-4xl font-outfit font-bold text-slate-900 dark:text-white"
        >
          Daily Overview
        </motion.h1>
        <motion.p 
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.1 }}
          className="text-slate-500 dark:text-slate-400 mt-2"
        >
          {loading ? 'Loading sensor data...' : 'Monitoring your IoT sensors in real-time.'}
        </motion.p>
        {displayData.timestamp && displayData.timestamp !== 'No data' && (
          <p className="text-sm text-slate-400 mt-1">
            Last updated: {new Date(displayData.timestamp).toLocaleTimeString()}
          </p>
        )}
      </header>

      {error && (
        <motion.div 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="mb-6 p-4 bg-yellow-100 dark:bg-yellow-900 text-yellow-800 dark:text-yellow-100 rounded-lg"
        >
          <p className="text-sm font-semibold">{error}</p>
        </motion.div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div className="grid grid-cols-1 gap-6 md:col-span-2">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
            <SensorCard 
              title="Distance" 
              value={displayData.distance.toFixed(2)} 
              unit="cm" 
              icon={Ruler} 
              color="blue"
              description="Distance from sensor object"
              loading={loading}
            />
            <SensorCard 
              title="Temperature" 
              value={displayData.temperature.toFixed(2)} 
              unit="°C" 
              icon={Thermometer} 
              color="orange"
              description="Ambient room temperature"
              loading={loading}
            />
          </div>
          <ProgressBar 
            title="Water Percentage" 
            percentage={displayData.waterPercentage} 
            color="sky"
            loading={loading}
          />
          <PredictionCard sensorData={displayData} isConnected={isServerConnected} />
        </div>

        <div className="lg:col-span-1">
          <WaterLevelIndicator 
            waterLiters={displayData.waterLevel} 
            waterPercentage={displayData.waterPercentage}
            loading={loading} 
          />
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
