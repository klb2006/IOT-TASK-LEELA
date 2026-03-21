import React, { useState } from 'react';
import { FaBrain, FaExclamationTriangle } from 'react-icons/fa';
import { apiEndpoints } from '../utils/api';

const PredictionCard = ({ sensorData, isConnected }) => {
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handlePredict = async () => {
    if (!sensorData) {
      setError('No sensor data available');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const now = new Date();
      const minute = now.getMinutes();
      const hour = now.getHours();

      const response = await apiEndpoints.predictWaterLevel({
        distance: parseFloat(sensorData.distance) || 0,
        temperature: parseFloat(sensorData.temperature) || 0,
        water_percent: parseFloat(sensorData.water_percentage) || 0,
        minute: minute,
        hour: hour,
        node_id: 'node-1',
      });

      if (response.data && response.data.predicted_water_percent !== undefined) {
        setPrediction({
          value: response.data.predicted_water_percent,
          timestamp: new Date().toLocaleTimeString(),
        });
      } else {
        setError('Prediction failed');
      }
    } catch (err) {
      setError('Unable to get prediction');
      console.error('Prediction error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-6 shadow-sm">
      <div className="flex items-center gap-3 mb-4">
        <FaBrain className="w-6 h-6 text-purple-600" />
        <h3 className="text-lg font-bold text-slate-900 dark:text-white">
          Water Level Prediction
        </h3>
      </div>

      {prediction ? (
        <div className="mb-4 p-4 bg-purple-50 dark:bg-purple-900/20 rounded-lg border border-purple-200 dark:border-purple-700">
          <div className="text-center">
            <div className="text-5xl font-bold text-purple-600 dark:text-purple-400">
              {prediction.value.toFixed(1)}%
            </div>
            <p className="text-sm text-slate-600 dark:text-slate-400 mt-2">
              Predicted water level
            </p>
            <p className="text-xs text-slate-500 dark:text-slate-500 mt-1">
              Predicted at: {prediction.timestamp}
            </p>
          </div>
          
          <div className="mt-3 p-2 bg-yellow-50 dark:bg-yellow-900/20 rounded border border-yellow-200 dark:border-yellow-700">
            <p className="text-xs text-yellow-700 dark:text-yellow-300 flex gap-2">
              <FaExclamationTriangle className="flex-shrink-0 mt-0.5" />
              <span><strong>Note:</strong> If water level stays the same, the motor might not be running. Prediction may be inaccurate.</span>
            </p>
          </div>
        </div>
      ) : null}

      {error && (
        <div className="mb-4 p-3 bg-red-50 dark:bg-red-900/20 rounded-lg border border-red-200 dark:border-red-700 text-sm text-red-700 dark:text-red-300">
          {error}
        </div>
      )}

      <button
        onClick={handlePredict}
        disabled={loading || !isConnected}
        className="w-full bg-purple-600 hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold py-2 px-4 rounded-lg transition-colors duration-200"
      >
        {loading ? 'Predicting...' : 'Predict Water Level'}
      </button>

      {!isConnected && (
        <p className="text-xs text-red-600 dark:text-red-400 mt-2">
          ✗ Backend disconnected
        </p>
      )}
    </div>
  );
};

export default PredictionCard;
