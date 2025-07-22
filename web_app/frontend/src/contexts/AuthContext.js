import React, { createContext, useContext, useState, useEffect } from 'react';
import { api } from '../services/api';

// Helper function to decode JWT token
const decodeToken = (token) => {
  try {
    const base64Url = token.split('.')[1];
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = decodeURIComponent(atob(base64).split('').map(function(c) {
      return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
    }).join(''));
    return JSON.parse(jsonPayload);
  } catch (error) {
    return null;
  }
};

// Helper function to check if token expires soon (within 1 hour)
const isTokenExpiringSoon = (token) => {
  const decoded = decodeToken(token);
  if (!decoded || !decoded.exp) return true;
  
  const currentTime = Math.floor(Date.now() / 1000);
  const expirationTime = decoded.exp;
  const oneHourInSeconds = 60 * 60;
  
  return (expirationTime - currentTime) <= oneHourInSeconds;
};

const AuthContext = createContext();

export function useAuth() {
  return useContext(AuthContext);
}

export function AuthProvider({ children }) {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);
  const [user, setUser] = useState(null);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      api.setAuthToken(token);
      verifyToken(token);
    } else {
      setLoading(false);
    }

    // Set up periodic token check (every 30 minutes)
    const tokenCheckInterval = setInterval(() => {
      const currentToken = localStorage.getItem('token');
      if (currentToken && isTokenExpiringSoon(currentToken)) {
        console.log('Token expires soon, refreshing...');
        refreshToken();
      }
    }, 30 * 60 * 1000); // Check every 30 minutes

    return () => clearInterval(tokenCheckInterval);
  }, []);

  const verifyToken = async (token) => {
    try {
      const response = await api.get('/auth/verify');
      setIsAuthenticated(true);
      setUser(response.data.user);
    } catch (error) {
      localStorage.removeItem('token');
      api.setAuthToken(null);
      setIsAuthenticated(false);
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  const refreshToken = async () => {
    try {
      // For now, we'll use the verify endpoint to "refresh" the token
      // In a production app, you'd typically have a separate refresh endpoint
      const response = await api.get('/auth/verify');
      
      if (response.data.token) {
        // If the backend sends a new token, use it
        localStorage.setItem('token', response.data.token);
        api.setAuthToken(response.data.token);
      }
      
      console.log('Token refreshed successfully');
    } catch (error) {
      console.log('Token refresh failed, logging out...');
      logout();
    }
  };

  const login = async (username, password) => {
    try {
      const response = await api.post('/auth/login', { username, password });
      const { access_token } = response.data;
      
      localStorage.setItem('token', access_token);
      api.setAuthToken(access_token);
      
      setIsAuthenticated(true);
      setUser(username);
      
      return { success: true };
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Login failed' 
      };
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    api.setAuthToken(null);
    setIsAuthenticated(false);
    setUser(null);
  };

  const value = {
    isAuthenticated,
    user,
    loading,
    login,
    logout
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}