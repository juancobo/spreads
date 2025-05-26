import { useState, useEffect } from 'react';
import axios from 'axios';

const API_BASE = '/api';

/**
 * Custom hook for managing application configuration
 */
export function useConfiguration() {
  const [configuration, setConfiguration] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchConfiguration = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_BASE}/config`);
      setConfiguration(response.data);
      setError(null);
    } catch (err) {
      setError(err.message || 'Failed to fetch configuration');
      console.error('Error fetching configuration:', err);
    } finally {
      setLoading(false);
    }
  };

  const updateConfiguration = async (configData) => {
    try {
      const response = await axios.post(`${API_BASE}/config`, configData);
      setConfiguration(response.data);
      return response.data;
    } catch (err) {
      setError(err.message || 'Failed to update configuration');
      console.error('Error updating configuration:', err);
      throw err;
    }
  };

  useEffect(() => {
    fetchConfiguration();
  }, []);

  return {
    configuration,
    loading,
    error,
    fetchConfiguration,
    updateConfiguration
  };
}
