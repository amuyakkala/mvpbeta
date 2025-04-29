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
  Card,
  CardContent,
  Grid,
  IconButton,
  Collapse,
  Tooltip,
  Divider,
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
  Info as InfoIcon,
  Error as ErrorIcon,
  Warning as WarningIcon,
  CheckCircle as CheckCircleIcon,
} from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';
import api from '../services/api';

export default function Audit() {
  const [auditLogs, setAuditLogs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [expandedRows, setExpandedRows] = useState({});
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

  const getActionIcon = (action) => {
    switch (action?.toLowerCase()) {
      case 'create':
        return <CheckCircleIcon color="success" />;
      case 'update':
        return <InfoIcon color="info" />;
      case 'delete':
        return <ErrorIcon color="error" />;
      case 'login':
        return <CheckCircleIcon color="primary" />;
      case 'logout':
        return <InfoIcon color="secondary" />;
      default:
        return <InfoIcon />;
    }
  };

  const getActionColor = (action) => {
    switch (action?.toLowerCase()) {
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

  const handleRowExpand = (id) => {
    setExpandedRows(prev => ({
      ...prev,
      [id]: !prev[id]
    }));
  };

  const formatMetaData = (metaData) => {
    if (!metaData) return null;
    try {
      const data = typeof metaData === 'string' ? JSON.parse(metaData) : metaData;
      return (
        <Box sx={{ mt: 1 }}>
          {Object.entries(data).map(([key, value]) => (
            <Box key={key} sx={{ mb: 1 }}>
              <Typography variant="subtitle2" color="text.secondary">
                {key}:
              </Typography>
              <Typography variant="body2">
                {typeof value === 'object' ? JSON.stringify(value, null, 2) : String(value)}
              </Typography>
            </Box>
          ))}
        </Box>
      );
    } catch (e) {
      console.error('Error formatting meta data:', e);
      return null;
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Audit Logs
      </Typography>

      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6} md={3}>
              <FormControl fullWidth>
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
                  <MenuItem value="trace_analysis_start">Trace Analysis Start</MenuItem>
                  <MenuItem value="issue_detected">Issue Detected</MenuItem>
                  <MenuItem value="performance_issue_detected">Performance Issue</MenuItem>
                </Select>
              </FormControl>
            </Grid>

            <Grid item xs={12} sm={6} md={3}>
              <FormControl fullWidth>
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
            </Grid>

            <Grid item xs={12} sm={6} md={3}>
              <TextField
                fullWidth
                name="startDate"
                label="Start Date"
                type="date"
                value={filters.startDate}
                onChange={handleFilterChange}
                InputLabelProps={{ shrink: true }}
              />
            </Grid>

            <Grid item xs={12} sm={6} md={3}>
              <TextField
                fullWidth
                name="endDate"
                label="End Date"
                type="date"
                value={filters.endDate}
                onChange={handleFilterChange}
                InputLabelProps={{ shrink: true }}
              />
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
          <CircularProgress />
        </Box>
      ) : error ? (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      ) : (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Action</TableCell>
                <TableCell>Resource</TableCell>
                <TableCell>User</TableCell>
                <TableCell>Timestamp</TableCell>
                <TableCell>Details</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {auditLogs.map((log) => (
                <React.Fragment key={log.id}>
                  <TableRow hover>
                    <TableCell>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        {getActionIcon(log.action_type)}
                        <Chip
                          label={log.action_type}
                          color={getActionColor(log.action_type)}
                          size="small"
                        />
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Chip
                          label={log.resource_type}
                          variant="outlined"
                          size="small"
                        />
                        {log.resource_id && (
                          <Typography variant="caption" color="text.secondary">
                            ID: {log.resource_id}
                          </Typography>
                        )}
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2">
                        {log.user?.email || 'System'}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2">
                        {new Date(log.created_at).toLocaleString()}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <IconButton
                        size="small"
                        onClick={() => handleRowExpand(log.id)}
                      >
                        {expandedRows[log.id] ? <ExpandLessIcon /> : <ExpandMoreIcon />}
                      </IconButton>
                    </TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell style={{ paddingBottom: 0, paddingTop: 0 }} colSpan={5}>
                      <Collapse in={expandedRows[log.id]} timeout="auto" unmountOnExit>
                        <Box sx={{ margin: 2 }}>
                          <Typography variant="h6" gutterBottom>
                            Metadata
                          </Typography>
                          <Divider sx={{ mb: 2 }} />
                          {formatMetaData(log.meta_data)}
                        </Box>
                      </Collapse>
                    </TableCell>
                  </TableRow>
                </React.Fragment>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}
    </Box>
  );
} 