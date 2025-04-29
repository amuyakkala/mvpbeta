import React, { createContext, useContext, useState, useEffect } from 'react';
import api, { API_URL } from '../services/api';

const AuthContext = createContext();

export function useAuth() {
  return useContext(AuthContext);
}

export function AuthProvider({ children }) {
  const [currentUser, setCurrentUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const token = localStorage.getItem('token');
    console.log('AuthProvider mounted, token exists:', !!token);
    if (token) {
      fetchUser();
    } else {
      setLoading(false);
    }
  }, []);

  const fetchUser = async () => {
    try {
      console.log('Fetching user data...');
      const response = await api.get('/auth/me');
      console.log('User data received:', response.data);
      setCurrentUser(response.data);
    } catch (err) {
      console.error('Error fetching user:', err);
      console.error('Error response:', err.response?.data);
      localStorage.removeItem('token');
      setCurrentUser(null);
    } finally {
      setLoading(false);
    }
  };

  const login = async (email, password) => {
    try {
      setError('');
      console.log('AuthContext login called with:', { email });
      
      // Create FormData object for OAuth2 password flow
      const formData = new FormData();
      formData.append('username', email);
      formData.append('password', password);
      
      const response = await api.post('/auth/login', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      
      console.log('Login API response:', response.data);
      
      const { token, user } = response.data;
      console.log('Setting token and user:', { token, user });
      localStorage.setItem('token', token);
      setCurrentUser(user);
      return true;
    } catch (err) {
      console.error('AuthContext login error:', err);
      console.error('Error response:', err.response?.data);
      
      // Handle Pydantic validation errors
      if (err.response?.data) {
        if (Array.isArray(err.response.data)) {
          // Join all error messages with commas
          const errorMessages = err.response.data.map(e => e.msg).join(', ');
          setError(errorMessages);
        } else if (typeof err.response.data === 'object') {
          setError(err.response.data.detail || 'Failed to login');
        }
      } else {
        setError('Failed to login');
      }
      return false;
    }
  };

  const register = async (userData) => {
    console.log('Starting registration process...');
    try {
      console.log('Making registration request to:', `${API_URL}/auth/register`);
      console.log('Registration data:', userData);
      const response = await api.post('/auth/register', userData);
      console.log('Registration response:', response.data);
      
      const { token, user } = response.data;
      console.log('Registration successful, token received');
      localStorage.setItem('token', token);
      setCurrentUser(user);
      return true;
    } catch (err) {
      console.error('Registration error details:', {
        message: err.message,
        response: err.response?.data,
        status: err.response?.status,
        headers: err.response?.headers
      });
      setError(err.response?.data?.detail || 'Failed to register');
      return false;
    }
  };

  const logout = () => {
    console.log('Logging out...');
    localStorage.removeItem('token');
    setCurrentUser(null);
  };

  const value = {
    currentUser,
    loading,
    error,
    isAuthenticated: !!currentUser,
    login,
    register,
    logout,
  };

  console.log('AuthContext value:', { currentUser, loading, error, isAuthenticated: !!currentUser });

  return (
    <AuthContext.Provider value={value}>
      {!loading && children}
    </AuthContext.Provider>
  );
} 