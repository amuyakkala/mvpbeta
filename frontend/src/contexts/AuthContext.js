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
    if (token) {
      fetchUser();
    } else {
      setCurrentUser(null);
      setLoading(false);
    }
  }, []);

  const fetchUser = async () => {
    try {
      const response = await api.get('/auth/me');
      setCurrentUser(response.data);
    } catch (err) {
      console.error('Error fetching user:', err);
      localStorage.removeItem('token');
      setCurrentUser(null);
    } finally {
      setLoading(false);
    }
  };

  const login = async (email, password) => {
    try {
      setError('');
      setLoading(true);
      
      const formData = new URLSearchParams();
      formData.append('username', email);
      formData.append('password', password);
      
      const response = await api.post('/auth/login', formData, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      });
      
      const { token, user } = response.data;
      localStorage.setItem('token', token);
      setCurrentUser(user);
      return true;
    } catch (err) {
      console.error('Login error:', err);
      if (err.response?.data) {
        if (Array.isArray(err.response.data)) {
          setError(err.response.data.map(e => e.msg).join(', '));
        } else if (typeof err.response.data === 'object') {
          setError(err.response.data.detail || 'Failed to login');
        }
      } else {
        setError('Failed to login');
      }
      return false;
    } finally {
      setLoading(false);
    }
  };

  const register = async (userData) => {
    try {
      setError('');
      setLoading(true);
      const response = await api.post('/auth/register', userData);
      const { token, user } = response.data;
      localStorage.setItem('token', token);
      setCurrentUser(user);
      return true;
    } catch (err) {
      console.error('Registration error:', err);
      if (err.response?.data) {
        if (Array.isArray(err.response.data)) {
          setError(err.response.data.map(e => e.msg).join(', '));
        } else if (typeof err.response.data === 'object') {
          setError(err.response.data.detail || 'Failed to register');
        }
      } else {
        setError('Failed to register');
      }
      return false;
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    setCurrentUser(null);
  };

  const value = {
    currentUser,
    loading,
    error,
    login,
    register,
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
} 