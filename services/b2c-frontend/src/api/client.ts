import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for adding session/user headers
apiClient.interceptors.request.use(
  (config) => {
    const sessionId = localStorage.getItem('sessionId');
    const userId = localStorage.getItem('userId');

    if (userId) {
      config.headers['X-User-Id'] = userId;
    } else if (sessionId) {
      config.headers['X-Session-Id'] = sessionId;
    } else {
      // Generate session ID if none exists
      const newSessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      localStorage.setItem('sessionId', newSessionId);
      config.headers['X-Session-Id'] = newSessionId;
    }

    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      // Server responded with error status
      console.error('API Error:', error.response.data);
    } else if (error.request) {
      // Request made but no response
      console.error('Network Error:', error.message);
    } else {
      console.error('Error:', error.message);
    }
    return Promise.reject(error);
  }
);

export default apiClient;
