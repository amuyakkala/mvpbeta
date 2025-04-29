import React, { useEffect } from 'react';
import { Grid, Paper, Typography, Box, Avatar, Divider, Alert } from '@mui/material';
import {
  BugReport as IssuesIcon,
  Upload as UploadIcon,
  History as AuditIcon,
  Notifications as NotificationsIcon,
  Person as PersonIcon,
} from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';

export default function Dashboard() {
  const { currentUser, loading, error } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    console.log('Dashboard mounted');
    console.log('Current user:', currentUser);
    console.log('Loading state:', loading);
    console.log('Error state:', error);
  }, [currentUser, loading, error]);

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <Typography>Loading dashboard...</Typography>
      </Box>
    );
  }

  if (error) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert severity="error">{error}</Alert>
      </Box>
    );
  }

  if (!currentUser) {
    navigate('/login');
    return null;
  }

  // Sample data for demonstration
  const dashboardData = {
    traces: 5,
    issues: 3,
    auditLogs: 12,
    notifications: 2
  };

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" gutterBottom>
          Welcome back, {currentUser?.full_name || 'User'}!
        </Typography>
        <Typography variant="subtitle1" color="text.secondary">
          Here's what's happening with your account today
        </Typography>
      </Box>

      <Grid container spacing={3}>
        <Grid item xs={12} sm={6} md={3}>
          <Paper sx={{ p: 2, display: 'flex', flexDirection: 'column', height: '100%' }}>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
              <UploadIcon color="primary" sx={{ mr: 1 }} />
              <Typography variant="h6">Traces</Typography>
            </Box>
            <Typography variant="h4">{dashboardData.traces}</Typography>
            <Typography color="text.secondary">Total traces uploaded</Typography>
          </Paper>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Paper sx={{ p: 2, display: 'flex', flexDirection: 'column', height: '100%' }}>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
              <IssuesIcon color="error" sx={{ mr: 1 }} />
              <Typography variant="h6">Issues</Typography>
            </Box>
            <Typography variant="h4">{dashboardData.issues}</Typography>
            <Typography color="text.secondary">Active issues</Typography>
          </Paper>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Paper sx={{ p: 2, display: 'flex', flexDirection: 'column', height: '100%' }}>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
              <AuditIcon color="info" sx={{ mr: 1 }} />
              <Typography variant="h6">Audit Logs</Typography>
            </Box>
            <Typography variant="h4">{dashboardData.auditLogs}</Typography>
            <Typography color="text.secondary">Recent activities</Typography>
          </Paper>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Paper sx={{ p: 2, display: 'flex', flexDirection: 'column', height: '100%' }}>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
              <NotificationsIcon color="warning" sx={{ mr: 1 }} />
              <Typography variant="h6">Notifications</Typography>
            </Box>
            <Typography variant="h4">{dashboardData.notifications}</Typography>
            <Typography color="text.secondary">Unread notifications</Typography>
          </Paper>
        </Grid>
      </Grid>

      <Paper sx={{ p: 3, mt: 4 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <Avatar sx={{ bgcolor: 'primary.main', mr: 2 }}>
            <PersonIcon />
          </Avatar>
          <Box>
            <Typography variant="h6">Your Account</Typography>
            <Typography color="text.secondary">Manage your profile and settings</Typography>
          </Box>
        </Box>
        <Divider sx={{ my: 2 }} />
        <Grid container spacing={2}>
          <Grid item xs={12} sm={6}>
            <Typography variant="subtitle2" color="text.secondary">Email</Typography>
            <Typography>{currentUser?.email || 'Not available'}</Typography>
          </Grid>
          <Grid item xs={12} sm={6}>
            <Typography variant="subtitle2" color="text.secondary">Full Name</Typography>
            <Typography>{currentUser?.full_name || 'Not available'}</Typography>
          </Grid>
          <Grid item xs={12} sm={6}>
            <Typography variant="subtitle2" color="text.secondary">Account Status</Typography>
            <Typography color="success.main">Active</Typography>
          </Grid>
        </Grid>
      </Paper>
    </Box>
  );
} 