import { useState, useEffect } from 'react';

export default function useDeployment() {
  const [deployment, setDeployment] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const saveDeployment = async (deploymentData) => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch('/api/deployment', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(deploymentData),
      });
      const result = await response.json();
      setDeployment(result);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const getDeploymentStatus = async (id) => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`/api/deployment/${id}`);
      const result = await response.json();
      setDeployment(result);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return { deployment, loading, error, saveDeployment, getDeploymentStatus };
}