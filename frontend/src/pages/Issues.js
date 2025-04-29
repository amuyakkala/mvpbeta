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
  IconButton,
  CircularProgress,
  Button,
} from '@mui/material';
import { Edit as EditIcon, Delete as DeleteIcon, ArrowBack as BackIcon } from '@mui/icons-material';
import api from '../services/api';
import { useNavigate, useLocation } from 'react-router-dom';

export default function Issues() {
  const [issues, setIssues] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();
  const location = useLocation();
  const traceId = new URLSearchParams(location.search).get('trace_id');

  useEffect(() => {
    fetchIssues();
  }, [traceId]);

  const fetchIssues = async () => {
    try {
      setLoading(true);
      setError('');
      const url = traceId ? `/issues?trace_id=${traceId}` : '/issues';
      const response = await api.get(url);
      setIssues(response.data.items || []);
    } catch (err) {
      console.error('Error fetching issues:', err);
      setError('Failed to fetch issues');
    } finally {
      setLoading(false);
    }
  };

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'critical':
        return 'error';
      case 'high':
        return 'warning';
      case 'medium':
        return 'info';
      case 'low':
        return 'success';
      default:
        return 'default';
    }
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
        <Typography variant="h4">
          {traceId ? `Issues for Trace #${traceId}` : 'All Issues'}
        </Typography>
        {traceId && (
          <Button
            variant="outlined"
            startIcon={<BackIcon />}
            onClick={() => navigate('/traces')}
          >
            Back to Traces
          </Button>
        )}
      </Box>
      
      {error && (
        <Typography color="error" sx={{ mb: 2 }}>
          {error}
        </Typography>
      )}

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Title</TableCell>
              <TableCell>Severity</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Created</TableCell>
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
            ) : issues.length === 0 ? (
              <TableRow>
                <TableCell colSpan={5} align="center">
                  No issues found
                </TableCell>
              </TableRow>
            ) : (
              issues.map((issue) => (
                <TableRow key={issue.id}>
                  <TableCell>{issue.title}</TableCell>
                  <TableCell>
                    <Chip
                      label={issue.severity}
                      color={getSeverityColor(issue.severity)}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={issue.status}
                      color={issue.status === 'open' ? 'error' : 'success'}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>{new Date(issue.created_at).toLocaleString()}</TableCell>
                  <TableCell>
                    <IconButton color="primary" size="small">
                      <EditIcon />
                    </IconButton>
                    <IconButton color="error" size="small">
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