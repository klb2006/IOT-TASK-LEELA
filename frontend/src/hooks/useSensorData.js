import { useState, useEffect } from 'react';
import { apiEndpoints } from '../utils/api';

export const useSensorData = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    const fetchData = async (isInitial = false) => {
      try {
        if (isInitial) setLoading(true);
        
        // Fetch latest sensor data
        const sensorResponse = await apiEndpoints.getLatestSensorData();
        
        if (sensorResponse.data) {
          setData(sensorResponse.data.data);
          setIsConnected(true);
          setError(null);
        } else {
          setError('Failed to fetch sensor data');
          setIsConnected(false);
        }
      } catch (err) {
        setError(err.message);
        setIsConnected(false);
        console.error('Error fetching sensor data:', err);
      } finally {
        if (isInitial) setLoading(false);
      }
    };

    // Initial fetch
    fetchData(true);
    
    // Refresh data every 15 seconds silently (no loading state)
    const interval = setInterval(() => fetchData(false), 15000);
    
    return () => clearInterval(interval);
  }, []);

  return { data, loading, error, isConnected };
};

export const useServerStatus = () => {
  const [status, setStatus] = useState(null);
  const [isConnected, setIsConnected] = useState(true);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const checkStatus = async () => {
      try {
        await apiEndpoints.getLatestSensorData();
        setIsConnected(true);
        setLoading(false);
      } catch (err) {
        setIsConnected(false);
        setLoading(false);
      }
    };

    checkStatus();
    const interval = setInterval(checkStatus, 15000);
    
    return () => clearInterval(interval);
  }, []);

  return { status, isConnected, loading };
};
