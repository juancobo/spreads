import { useState, useEffect } from 'react';
import axios from 'axios';

const API_BASE = '/api';

/**
 * Custom hook for managing workflows
 */
export function useWorkflows() {
  const [workflows, setWorkflows] = useState([]);
  const [selectedWorkflow, setSelectedWorkflow] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchWorkflows = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_BASE}/workflow`);
      setWorkflows(response.data);
      setError(null);
    } catch (err) {
      setError(err.message || 'Failed to fetch workflows');
      console.error('Error fetching workflows:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchWorkflow = async (id) => {
    try {
      const response = await axios.get(`${API_BASE}/workflow/${id}`);
      setSelectedWorkflow(response.data);
      return response.data;
    } catch (err) {
      setError(err.message || 'Failed to fetch workflow');
      console.error('Error fetching workflow:', err);
      throw err;
    }
  };

  const createWorkflow = async (workflowData) => {
    try {
      const response = await axios.post(`${API_BASE}/workflow`, workflowData);
      await fetchWorkflows(); // Refresh the list
      return response.data;
    } catch (err) {
      setError(err.message || 'Failed to create workflow');
      console.error('Error creating workflow:', err);
      throw err;
    }
  };

  const updateWorkflow = async (id, workflowData) => {
    try {
      const response = await axios.put(`${API_BASE}/workflow/${id}`, workflowData);
      await fetchWorkflows(); // Refresh the list
      if (selectedWorkflow && selectedWorkflow.id === id) {
        setSelectedWorkflow(response.data);
      }
      return response.data;
    } catch (err) {
      setError(err.message || 'Failed to update workflow');
      console.error('Error updating workflow:', err);
      throw err;
    }
  };

  const deleteWorkflow = async (id) => {
    try {
      await axios.delete(`${API_BASE}/workflow/${id}`);
      await fetchWorkflows(); // Refresh the list
      if (selectedWorkflow && selectedWorkflow.id === id) {
        setSelectedWorkflow(null);
      }
    } catch (err) {
      setError(err.message || 'Failed to delete workflow');
      console.error('Error deleting workflow:', err);
      throw err;
    }
  };

  useEffect(() => {
    fetchWorkflows();
  }, []);

  return {
    workflows,
    selectedWorkflow,
    loading,
    error,
    fetchWorkflows,
    fetchWorkflow,
    createWorkflow,
    updateWorkflow,
    deleteWorkflow,
    setSelectedWorkflow
  };
}
