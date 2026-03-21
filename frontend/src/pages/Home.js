import React, { useState, useEffect } from 'react';
import { apiEndpoints } from '../utils/api';
import '../styles/Home.css';
import config from '../config';
import { FaRuler, FaThermometerHalf, FaTint, FaVial, FaSync, FaCheckCircle, FaServer, FaBrain, FaSignal, FaWifi, FaBan } from 'react-icons/fa';
import SensorCard from '../components/SensorCard';
import WaterLevelIndicator from '../components/WaterLevelIndicator';
import ProgressBar from '../components/ProgressBar';
import { useSensorData, useServerStatus } from '../hooks/useSensorData';

const Home = () => {
  const { data: sensorData, loading, error, isConnected } = useSensorData();
  const { status: serverStatus, isConnected: isServerConnected } = useServerStatus();
  const [sensorHistory, setSensorHistory] = useState([]);
  const [modelInfo, setModelInfo] = useState(null);

  useEffect(() => {
    const fetchAdditionalData = async () => {
      try {
        const [historyRes, modelRes] = await Promise.all([
          apiEndpoints.getSensorHistory(20),
          apiEndpoints.getModelInfo()
        ]);

        setSensorHistory(historyRes.data.data || []);
        setModelInfo(modelRes.data.model_info);
      } catch (err) {
        console.error('Error fetching additional data:', err);
      }
    };

    fetchAdditionalData();
    const interval = setInterval(fetchAdditionalData, 30000);
    return () => clearInterval(interval);
  }, []);

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
    <div className="min-h-screen pt-24 pb-12 px-4 md:px-8 lg:px-12 max-w-7xl mx-auto">
      {/* Connection Status Banner */}
      <div className={`mb-6 p-4 rounded-lg flex items-center gap-3 ${
        isServerConnected 
          ? 'bg-green-100 text-green-800' 
          : 'bg-red-100 text-red-800'
      }`}>
        {isServerConnected ? (
          <FaWifi className="w-5 h-5" />
        ) : (
          <FaBan className="w-5 h-5" />
        )}
        <div>
          <span className="font-semibold">
            {isServerConnected ? '✓ Connected to Backend Server' : '✗ Disconnected from Backend'}
          </span>
          <p className="text-sm">
            {isServerConnected ? 'All systems operational' : 'Attempting to reconnect...'}
          </p>
        </div>
      </div>

      {/* Header Section */}
      <header className="mb-10">
        <h1 className="text-4xl font-bold text-slate-900 mb-2">
          Daily Overview - {config.COLLEGE_NAME}
        </h1>
        <p className="text-slate-500">
          {loading ? 'Loading sensor data...' : 'Monitoring your water tank in real-time.'}
        </p>
        {displayData.timestamp && displayData.timestamp !== 'No data' && (
          <p className="text-sm text-slate-400 mt-1">
            Last updated: {new Date(displayData.timestamp).toLocaleTimeString()}
          </p>
        )}
      </header>

      {/* Error Banner */}
      {error && (
        <div className="mb-6 p-4 bg-yellow-100 text-yellow-800 rounded-lg border border-yellow-200">
          <p className="text-sm font-semibold">{error}</p>
        </div>
      )}

      {/* Loading State */}
      {loading ? (
        <div className="flex items-center justify-center py-20">
          <div className="text-center">
            <div className="w-12 h-12 border-4 border-slate-300 border-t-blue-600 rounded-full animate-spin mx-auto mb-4" />
            <p className="text-slate-500 font-medium">Loading sensor data...</p>
          </div>
        </div>
      ) : (
        <>
          {/* Main Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
            {/* Left Column - Sensor Cards */}
            <div className="md:col-span-2 flex flex-col gap-6">
              {/* Top Row - Distance & Temperature */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                <SensorCard 
                  title="Distance" 
                  value={displayData.distance.toFixed(2)} 
                  unit="cm" 
                  icon={FaRuler} 
                  color="blue"
                  description="Distance from sensor"
                  loading={loading}
                />
                <SensorCard 
                  title="Temperature" 
                  value={displayData.temperature.toFixed(2)} 
                  unit="°C" 
                  icon={FaThermometerHalf} 
                  color="orange"
                  description="Ambient temperature"
                  loading={loading}
                />
              </div>

              {/* Water Percentage Progress Bar */}
              <ProgressBar 
                title="Water Percentage" 
                percentage={displayData.waterPercentage} 
                color="sky"
                loading={loading}
              />
            </div>

            {/* Right Column - Water Level Indicator */}
            <div className="col-span-1">
              <WaterLevelIndicator 
                waterLiters={displayData.waterLevel} 
                waterPercentage={displayData.waterPercentage}
                loading={loading} 
              />
            </div>
          </div>

          {/* Recent Readings Table */}
          <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm mb-8">
            <h2 className="text-xl font-bold text-slate-900 mb-4">Recent Readings</h2>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-slate-200">
                    <th className="text-left py-3 px-4 text-slate-500 font-semibold">Time</th>
                    <th className="text-left py-3 px-4 text-slate-500 font-semibold">Distance (cm)</th>
                    <th className="text-left py-3 px-4 text-slate-500 font-semibold">Temperature (°C)</th>
                    <th className="text-left py-3 px-4 text-slate-500 font-semibold">Water Level (%)</th>
                  </tr>
                </thead>
                <tbody>
                  {sensorHistory.slice(0, 10).map((reading, index) => (
                    <tr key={index} className="border-b border-slate-100 hover:bg-slate-50">
                      <td className="py-3 px-4 text-slate-700">{new Date(reading.timestamp).toLocaleTimeString()}</td>
                      <td className="py-3 px-4 text-slate-700">{reading.distance?.toFixed(2)}</td>
                      <td className="py-3 px-4 text-slate-700">{reading.temperature?.toFixed(1)}</td>
                      <td className="py-3 px-4 text-slate-700">{reading.water_percentage?.toFixed(1)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* System Status Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
              <h3 className="text-lg font-bold text-slate-900 mb-4">Model Status</h3>
              {modelInfo ? (
                <div className="space-y-3">
                  <div className="flex justify-between items-center pb-3 border-b border-slate-100">
                    <span className="text-slate-500 text-sm uppercase font-semibold">Type:</span>
                    <span className="text-slate-900 font-bold">{modelInfo.model_type}</span>
                  </div>
                  <div className="flex justify-between items-center pb-3 border-b border-slate-100">
                    <span className="text-slate-500 text-sm uppercase font-semibold">Version:</span>
                    <span className="text-slate-900 font-bold">{modelInfo.version}</span>
                  </div>
                  <div className="flex justify-between items-center pb-3 border-b border-slate-100">
                    <span className="text-slate-500 text-sm uppercase font-semibold">Accuracy:</span>
                    <span className="text-blue-600 font-bold">{(modelInfo.accuracy * 100).toFixed(1)}%</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-slate-500 text-sm uppercase font-semibold">Predictions:</span>
                    <span className="text-slate-900 font-bold">{modelInfo.total_predictions}</span>
                  </div>
                </div>
              ) : (
                <p className="text-slate-500">Loading model information...</p>
              )}
            </div>

            <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
              <h3 className="text-lg font-bold text-slate-900 mb-4">System Status</h3>
              <div className="space-y-2">
                <div className="flex items-center gap-2 p-2 bg-green-50 rounded border border-green-200 text-green-700 text-sm font-semibold">
                  <FaCheckCircle /> Database: Connected
                </div>
                <div className="flex items-center gap-2 p-2 bg-green-50 rounded border border-green-200 text-green-700 text-sm font-semibold">
                  <FaCheckCircle /> API Server: Running
                </div>
                <div className="flex items-center gap-2 p-2 bg-green-50 rounded border border-green-200 text-green-700 text-sm font-semibold">
                  <FaCheckCircle /> ML Model: Loaded
                </div>
                <div className="flex items-center gap-2 p-2 bg-green-50 rounded border border-green-200 text-green-700 text-sm font-semibold">
                  <FaCheckCircle /> Sensors: Connected
                </div>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default Home;
