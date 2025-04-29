import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Button,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton,
  Alert,
  CircularProgress,
  Link,
  Chip,
} from '@mui/material';
import { Upload as UploadIcon, Delete as DeleteIcon, BugReport as IssuesIcon } from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';
import api from '../services/api';
import { useNavigate } from 'react-router-dom';

export default function Traces() {
  const [traces, setTraces] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();
  const { user } = useAuth();

  useEffect(() => {
    if (user) {
      fetchTraces();
    }
  }, [user]);

  const fetchTraces = async () => {
    try {
      setLoading(true);
      const { data } = await api.get('/logs/traces');
      setTraces(data);
    } catch (err) {
      console.error('Error fetching traces:', err);
      setError('Failed to fetch traces');
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    if (file.type !== 'application/json') {
      setError('Please upload a JSON file');
      return;
    }

    try {
      setLoading(true);
      setError('');

      const formData = new FormData();
      formData.append('file', file);

      await api.post('/logs/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      // Refresh the traces list
      await fetchTraces();
    } catch (err) {
      console.error('Error uploading trace:', err);
      setError(err.response?.data?.detail || 'Failed to upload trace');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (traceId) => {
    try {
      setLoading(true);
      await api.delete(`/logs/traces/${traceId}`);
      await fetchTraces();
    } catch (err) {
      console.error('Error deleting trace:', err);
      setError('Failed to delete trace');
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'analyzing':
        return 'info';
      case 'completed':
        return 'success';
      case 'failed':
        return 'error';
      default:
        return 'default';
    }
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
        <Typography variant="h4">Traces</Typography>
        <Button
          variant="contained"
          component="label"
          startIcon={<UploadIcon />}
          disabled={loading}
        >
          {loading ? <CircularProgress size={24} /> : 'Upload Trace'}
          <input
            type="file"
            hidden
            accept=".json"
            onChange={handleFileUpload}
            disabled={loading}
          />
        </Button>
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
              <TableCell>File Name</TableCell>
              <TableCell>Upload Date</TableCell>
              <TableCell>Size</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {loading ? (
              <TableRow>
                <TableCell colSpan={5} align="center">
                  <CircularProgress />
                </TableCell>
              </TableRow>
            ) : traces.length === 0 ? (
              <TableRow>
                <TableCell colSpan={5} align="center">
                  No traces uploaded yet
                </TableCell>
              </TableRow>
            ) : (
              traces.map((trace) => (
                <TableRow key={trace.id}>
                  <TableCell>{trace.file_name}</TableCell>
                  <TableCell>{new Date(trace.created_at).toLocaleString()}</TableCell>
                  <TableCell>{trace.file_size} bytes</TableCell>
                  <TableCell>
                    <Chip
                      label={trace.status || 'pending'}
                      color={getStatusColor(trace.status)}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    <IconButton
                      color="primary"
                      onClick={() => navigate(`/issues?trace_id=${trace.id}`)}
                      title="View Issues"
                    >
                      <IssuesIcon />
                    </IconButton>
                    <IconButton 
                      color="error" 
                      onClick={() => handleDelete(trace.id)}
                      disabled={loading}
                    >
                      <DeleteIcon />
                    </IconButton>
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