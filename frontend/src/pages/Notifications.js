import React, { useState } from 'react';
import {
  Box,
  Typography,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Chip,
  IconButton,
} from '@mui/material';
import {
  Notifications as NotificationsIcon,
  Check as CheckIcon,
} from '@mui/icons-material';

export default function Notifications() {
  const [notifications, setNotifications] = useState([]);

  const getNotificationColor = (type) => {
    switch (type) {
      case 'error':
        return 'error';
      case 'warning':
        return 'warning';
      case 'info':
        return 'info';
      case 'success':
        return 'success';
      default:
        return 'default';
    }
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
        <Typography variant="h4">Notifications</Typography>
        <Chip
          label={`${notifications.length} unread`}
          color="primary"
          variant="outlined"
        />
      </Box>

      <List>
        {notifications.length === 0 ? (
          <ListItem>
            <ListItemText primary="No notifications" />
          </ListItem>
        ) : (
          notifications.map((notification) => (
            <ListItem
              key={notification.id}
              secondaryAction={
                <IconButton edge="end" aria-label="mark as read">
                  <CheckIcon />
                </IconButton>
              }
            >
              <ListItemIcon>
                <NotificationsIcon color={getNotificationColor(notification.type)} />
              </ListItemIcon>
              <ListItemText
                primary={notification.title}
                secondary={notification.message}
              />
              <Chip
                label={notification.type}
                color={getNotificationColor(notification.type)}
                size="small"
                sx={{ ml: 2 }}
              />
            </ListItem>
          ))
        )}
      </List>
    </Box>
  );
} 