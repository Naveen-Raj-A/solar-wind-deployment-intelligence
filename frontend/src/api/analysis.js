import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 300000, // 5 minutes
  headers: {
    'Content-Type': 'application/json',
  },
});

export const analyzeSite = async (data) => {
  try {
    if (import.meta.env.MODE === 'development') {
      console.log('API Request:', JSON.stringify(data, null, 2));
    }
    
    const response = await apiClient.post('/analysis', data);
    
    if (import.meta.env.MODE === 'development') {
      console.log('API Response:', JSON.stringify(response.data, null, 2));
    }
    
    return response.data;
  } catch (error) {
    console.error('API Error details:', {
      message: error.message,
      response: error.response?.data,
      status: error.response?.status,
    });
    
    // Improved error handling
    let errorMessage = 'An error occurred during analysis.';
    if (error.response) {
      // Backend returned an error (e.g., 400, 422, 500)
      errorMessage = error.response.data?.detail || `Error ${error.response.status}: ${JSON.stringify(error.response.data)}`;
    } else if (error.request) {
      // No response received
      errorMessage = 'No response from the analysis service. Please check if it is running.';
    } else {
      // Other error
      errorMessage = error.message;
    }
    
    throw new Error(errorMessage);
  }
};

export default apiClient;
