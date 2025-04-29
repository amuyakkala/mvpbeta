import React, { useState, useEffect } from 'react';
import {
  Container,
  Grid,
  Paper,
  Typography,
  Card,
  CardContent,
  Chip,
  Box,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
} from '@mui/material';
import axios from 'axios';

const IssuesPage = () => {
  const [issues, setIssues] = useState([]);
  const [openDialog, setOpenDialog] = useState(false);
  const [selectedIssue, setSelectedIssue] = useState(null);
  const [updateData, setUpdateData] = useState({
    status: '',
    assigned_to: '',
  });

  useEffect(() => {
    fetchIssues();
    const interval = setInterval(fetchIssues, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchIssues = async () => {
    try {
      const response = await axios.get('/api/issues');
      setIssues(response.data);
    } catch (error) {
      console.error('Error fetching issues:', error);
    }
  };

  const handleOpenDialog = (issue) => {
    setSelectedIssue(issue);
    setUpdateData({
      status: issue.status,
      assigned_to: issue.assigned_to_user_id || '',
    });
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setSelectedIssue(null);
  };

  const handleUpdateIssue = async () => {
    try {
      await axios.put(`/api/issues/${selectedIssue.id}`, updateData);
      handleCloseDialog();
      fetchIssues();
    } catch (error) {
      console.error('Error updating issue:', error);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'open':
        return 'error';
      case 'assigned':
        return 'warning';
      case 'resolved':
        return 'success';
      case 'closed':
        return 'default';
      default:
        return 'default';
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
    <Container maxWidth="lg" sx={{ mt: 4 }}>
      <Typography variant="h4" gutterBottom>
        Issues Board
      </Typography>
      <Grid container spacing={3}>
        {['open', 'assigned', 'resolved', 'closed'].map((status) => (
          <Grid item xs={12} sm={6} md={3} key={status}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>
                {status.charAt(0).toUpperCase() + status.slice(1)}
              </Typography>
              {issues
                .filter((issue) => issue.status === status)
                .map((issue) => (
                  <Card key={issue.id} sx={{ mb: 2 }}>
                    <CardContent>
                      <Typography variant="h6">{issue.title}</Typography>
                      <Typography variant="body2" color="text.secondary">
                        {issue.description}
                      </Typography>
                      <Box sx={{ mt: 1 }}>
                        <Chip
                          label={issue.severity}
                          color={getSeverityColor(issue.severity)}
                          size="small"
                          sx={{ mr: 1 }}
                        />
                        <Chip
                          label={issue.status}
                          color={getStatusColor(issue.status)}
                          size="small"
                        />
                      </Box>
                      <Button
                        size="small"
                        onClick={() => handleOpenDialog(issue)}
                        sx={{ mt: 1 }}
                      >
                        Update
                      </Button>
                    </CardContent>
                  </Card>
                ))}
            </Paper>
          </Grid>
        ))}
      </Grid>

      <Dialog open={openDialog} onClose={handleCloseDialog}>
        <DialogTitle>Update Issue</DialogTitle>
        <DialogContent>
          <FormControl fullWidth sx={{ mt: 2 }}>
            <InputLabel>Status</InputLabel>
            <Select
              value={updateData.status}
              onChange={(e) =>
                setUpdateData({ ...updateData, status: e.target.value })
              }
            >
              <MenuItem value="open">Open</MenuItem>
              <MenuItem value="assigned">Assigned</MenuItem>
              <MenuItem value="resolved">Resolved</MenuItem>
              <MenuItem value="closed">Closed</MenuItem>
            </Select>
          </FormControl>
          <TextField
            fullWidth
            label="Assigned To"
            value={updateData.assigned_to}
            onChange={(e) =>
              setUpdateData({ ...updateData, assigned_to: e.target.value })
            }
            sx={{ mt: 2 }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button onClick={handleUpdateIssue} variant="contained">
            Update
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default IssuesPage; 