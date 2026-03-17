import { useState, useEffect } from 'react';
import { API_ENDPOINTS, fetchAPI } from '../api/config';

export const useSensorData = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        
        // Check connection status first
        const statusResponse = await fetchAPI(API_ENDPOINTS.STATUS);
        setIsConnected(statusResponse.status === 'running');

        // Fetch latest sensor data
        const sensorResponse = await fetchAPI(API_ENDPOINTS.SENSOR_LATEST);
        
        if (sensorResponse.status === 'success') {
          setData(sensorResponse.data);
          setError(null);
        } else {
          setError(sensorResponse.message || 'Failed to fetch sensor data');
        }
      } catch (err) {
        setError(err.message);
        setIsConnected(false);
        console.error('Error fetching sensor data:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
    
    // Refresh data every 5 seconds
    const interval = setInterval(fetchData, 5000);
    
    return () => clearInterval(interval);
  }, []);

  return { data, loading, error, isConnected };
};

export const useServerStatus = () => {
  const [status, setStatus] = useState(null);
  const [isConnected, setIsConnected] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const checkStatus = async () => {
      try {
        const response = await fetchAPI(API_ENDPOINTS.STATUS);
        setStatus(response);
        setIsConnected(response.status === 'running');
        setLoading(false);
      } catch (err) {
        setIsConnected(false);
        setLoading(false);
      }
    };

    checkStatus();
    const interval = setInterval(checkStatus, 3000);
    
    return () => clearInterval(interval);
  }, []);

  return { status, isConnected, loading };
};
