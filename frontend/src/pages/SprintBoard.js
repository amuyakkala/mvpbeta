import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  Grid,
  Card,
  CardContent,
  Button,
  CircularProgress,
  Alert,
  Chip,
} from '@mui/material';
import { DragDropContext, Droppable, Draggable } from 'react-beautiful-dnd';
import { useAuth } from '../contexts/AuthContext';
import api from '../services/api';

export default function SprintBoard() {
  const [issues, setIssues] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [pollingInterval, setPollingInterval] = useState(null);

  useEffect(() => {
    fetchIssues();
    
    // Start polling for new issues
    const interval = setInterval(fetchIssues, 5000); // Poll every 5 seconds
    setPollingInterval(interval);

    return () => {
      if (interval) clearInterval(interval);
    };
  }, []);

  const fetchIssues = async () => {
    try {
      setLoading(true);
      const { data } = await api.get('/issues');
      setIssues(data);
    } catch (err) {
      console.error('Error fetching issues:', err);
      setError('Failed to fetch issues');
    } finally {
      setLoading(false);
    }
  };

  const handleDragEnd = async (result) => {
    if (!result.destination) return;

    const { source, destination } = result;
    if (source.droppableId === destination.droppableId) return;

    const issueId = result.draggableId;
    const newStatus = destination.droppableId;

    try {
      await api.patch(`/issues/${issueId}`, {
        status: newStatus
      });
      await fetchIssues();
    } catch (err) {
      console.error('Error updating issue status:', err);
      setError('Failed to update issue status');
    }
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Sprint Board
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <DragDropContext onDragEnd={handleDragEnd}>
        <Grid container spacing={2}>
          {['todo', 'in_progress', 'done'].map((status) => (
            <Grid item xs={4} key={status}>
              <Paper sx={{ p: 2, minHeight: '70vh' }}>
                <Typography variant="h6" gutterBottom>
                  {status.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')}
                </Typography>
                <Droppable droppableId={status}>
                  {(provided) => (
                    <Box
                      ref={provided.innerRef}
                      {...provided.droppableProps}
                      sx={{ minHeight: '60vh' }}
                    >
                      {loading ? (
                        <Box display="flex" justifyContent="center" p={2}>
                          <CircularProgress />
                        </Box>
                      ) : (
                        issues
                          .filter(issue => issue.status === status)
                          .map((issue, index) => (
                            <Draggable
                              key={issue.id}
                              draggableId={issue.id.toString()}
                              index={index}
                            >
                              {(provided) => (
                                <Card
                                  ref={provided.innerRef}
                                  {...provided.draggableProps}
                                  {...provided.dragHandleProps}
                                  sx={{ mb: 2 }}
                                >
                                  <CardContent>
                                    <Typography variant="h6">{issue.title}</Typography>
                                    <Typography variant="body2" color="text.secondary">
                                      {issue.description}
                                    </Typography>
                                    <Box sx={{ mt: 1 }}>
                                      <Chip
                                        label={issue.severity}
                                        size="small"
                                        color={
                                          issue.severity === 'high' ? 'error' :
                                          issue.severity === 'medium' ? 'warning' :
                                          'success'
                                        }
                                      />
                                    </Box>
                                  </CardContent>
                                </Card>
                              )}
                            </Draggable>
                          ))
                      )}
                      {provided.placeholder}
                    </Box>
                  )}
                </Droppable>
              </Paper>
            </Grid>
          ))}
        </Grid>
      </DragDropContext>
    </Box>
  );
} 