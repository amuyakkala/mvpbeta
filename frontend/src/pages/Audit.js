import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  TextField,
  MenuItem,
  FormControl,
  InputLabel,
  Select,
  CircularProgress,
  Alert,
} from '@mui/material';
import { useAuth } from '../contexts/AuthContext';
import api from '../services/api';

export default function Audit() {
  const [auditLogs, setAuditLogs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [filters, setFilters] = useState({
    actionType: '',
    resourceType: '',
    startDate: '',
    endDate: '',
  });

  useEffect(() => {
    fetchAuditLogs();
  }, [filters]);

  const fetchAuditLogs = async () => {
    try {
      setLoading(true);
      setError('');
      const params = new URLSearchParams();
      if (filters.actionType) params.append('action_type', filters.actionType);
      if (filters.resourceType) params.append('resource_type', filters.resourceType);
      if (filters.startDate) params.append('start_date', filters.startDate);
      if (filters.endDate) params.append('end_date', filters.endDate);

      const response = await api.get(`/audit?${params.toString()}`);
      
      // Handle potential validation error response
      if (response.data && typeof response.data === 'object') {
        // Check if it's a Pydantic validation error array
        if (Array.isArray(response.data) && response.data.length > 0 && 'type' in response.data[0]) {
          const errorMessages = response.data.map(err => err.msg).join(', ');
          throw new Error(errorMessages);
        }
        // Check if it's a single error object
        if ('type' in response.data || 'msg' in response.data || 'loc' in response.data || 'input' in response.data || 'url' in response.data) {
          throw new Error(response.data.msg || response.data.type || 'Unknown error');
        }
        // Check if it's a detail error
        if ('detail' in response.data) {
          throw new Error(response.data.detail);
        }
      }

      // Ensure we're working with an array of logs
      const logs = Array.isArray(response.data) ? response.data : [];
      setAuditLogs(logs);
    } catch (err) {
      console.error('Error fetching audit logs:', err);
      // Extract error message from different possible error structures
      let errorMessage = 'Failed to fetch audit logs';
      if (err.response?.data) {
        if (Array.isArray(err.response.data)) {
          errorMessage = err.response.data.map(e => e.msg).join(', ');
        } else if (typeof err.response.data === 'object') {
          errorMessage = err.response.data.detail || 
                        err.response.data.msg || 
                        err.response.data.type || 
                        'Unknown error';
        }
      } else if (err.message) {
        errorMessage = err.message;
      }
      setError(errorMessage);
      setAuditLogs([]);
    } finally {
      setLoading(false);
    }
  };

  const getActionColor = (action) => {
    if (!action || typeof action !== 'string') return 'default';
    
    switch (action.toLowerCase()) {
      case 'create':
        return 'success';
      case 'update':
        return 'info';
      case 'delete':
        return 'error';
      case 'login':
        return 'primary';
      case 'logout':
        return 'secondary';
      default:
        return 'default';
    }
  };

  const handleFilterChange = (event) => {
    const { name, value } = event.target;
    setFilters(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const formatMetaData = (metaData) => {
    if (!metaData) return '-';
    try {
      // If metaData is already a string, parse it first
      const data = typeof metaData === 'string' ? JSON.parse(metaData) : metaData;
      
      // Check if it's an error object
      if (data && typeof data === 'object') {
        if ('type' in data || 'msg' in data || 'loc' in data || 'input' in data || 'url' in data) {
          // If it's an error object, return a formatted string
          return `Error: ${data.msg || data.type || 'Unknown error'}`;
        }
        // If it's a regular object, stringify it
        return JSON.stringify(data, null, 2);
      }
      return String(data);
    } catch (e) {
      console.error('Error formatting meta data:', e);
      return '-';
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return '-';
    try {
      return new Date(dateString).toLocaleString();
    } catch (e) {
      console.error('Error formatting date:', e);
      return '-';
    }
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Audit Logs
      </Typography>

      <Box sx={{ mb: 3, display: 'flex', gap: 2 }}>
        <FormControl sx={{ minWidth: 200 }}>
          <InputLabel>Action Type</InputLabel>
          <Select
            name="actionType"
            value={filters.actionType}
            onChange={handleFilterChange}
            label="Action Type"
          >
            <MenuItem value="">All</MenuItem>
            <MenuItem value="create">Create</MenuItem>
            <MenuItem value="update">Update</MenuItem>
            <MenuItem value="delete">Delete</MenuItem>
            <MenuItem value="login">Login</MenuItem>
            <MenuItem value="logout">Logout</MenuItem>
          </Select>
        </FormControl>

        <FormControl sx={{ minWidth: 200 }}>
          <InputLabel>Resource Type</InputLabel>
          <Select
            name="resourceType"
            value={filters.resourceType}
            onChange={handleFilterChange}
            label="Resource Type"
          >
            <MenuItem value="">All</MenuItem>
            <MenuItem value="trace">Trace</MenuItem>
            <MenuItem value="issue">Issue</MenuItem>
            <MenuItem value="user">User</MenuItem>
          </Select>
        </FormControl>

        <TextField
          name="startDate"
          label="Start Date"
          type="date"
          value={filters.startDate}
          onChange={handleFilterChange}
          InputLabelProps={{ shrink: true }}
        />

        <TextField
          name="endDate"
          label="End Date"
          type="date"
          value={filters.endDate}
          onChange={handleFilterChange}
          InputLabelProps={{ shrink: true }}
        />
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Timestamp</TableCell>
              <TableCell>User</TableCell>
              <TableCell>Action</TableCell>
              <TableCell>Resource</TableCell>
              <TableCell>Details</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {loading ? (
              <TableRow>
                <TableCell colSpan={5} align="center">
                  <CircularProgress />
                </TableCell>
              </TableRow>
            ) : auditLogs.length === 0 ? (
              <TableRow>
                <TableCell colSpan={5} align="center">
                  No audit logs found
                </TableCell>
              </TableRow>
            ) : (
              auditLogs.map((log) => (
                <TableRow key={log.id}>
                  <TableCell>{formatDate(log.created_at)}</TableCell>
                  <TableCell>{log.user_id || '-'}</TableCell>
                  <TableCell>
                    <Chip
                      label={log.action_type || '-'}
                      color={getActionColor(log.action_type)}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    {log.resource_type || '-'} {log.resource_id ? `#${log.resource_id}` : ''}
                  </TableCell>
                  <TableCell>
                    <pre style={{ margin: 0, whiteSpace: 'pre-wrap' }}>
                      {formatMetaData(log.meta_data)}
                    </pre>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
} 