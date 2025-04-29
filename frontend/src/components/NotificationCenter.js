import React, { useState, useEffect } from 'react';
import { 
    Badge, 
    IconButton, 
    Popover, 
    List, 
    ListItem, 
    ListItemText, 
    Typography, 
    Box,
    Button
} from '@mui/material';
import NotificationsIcon from '@mui/icons-material/Notifications';
import { useAuth } from '../contexts/AuthContext';
import { api } from '../services/api';

const NotificationCenter = () => {
    const [anchorEl, setAnchorEl] = useState(null);
    const [notifications, setNotifications] = useState([]);
    const [unreadCount, setUnreadCount] = useState(0);
    const { isAuthenticated } = useAuth();

    useEffect(() => {
        if (isAuthenticated) {
            fetchNotifications();
        }
    }, [isAuthenticated]);

    const fetchNotifications = async () => {
        try {
            const response = await api.get('/notifications', {
                params: { unread_only: true }
            });
            setNotifications(response.data);
            setUnreadCount(response.data.length);
        } catch (error) {
            console.error('Error fetching notifications:', error);
        }
    };

    const handleClick = (event) => {
        setAnchorEl(event.currentTarget);
    };

    const handleClose = () => {
        setAnchorEl(null);
    };

    const markAsRead = async (notificationIds) => {
        try {
            await api.post('/notifications/read', { notification_ids: notificationIds });
            fetchNotifications();
        } catch (error) {
            console.error('Error marking notifications as read:', error);
        }
    };

    const open = Boolean(anchorEl);
    const id = open ? 'notification-popover' : undefined;

    return (
        <>
            <IconButton
                color="inherit"
                onClick={handleClick}
                aria-describedby={id}
            >
                <Badge badgeContent={unreadCount} color="error">
                    <NotificationsIcon />
                </Badge>
            </IconButton>
            <Popover
                id={id}
                open={open}
                anchorEl={anchorEl}
                onClose={handleClose}
                anchorOrigin={{
                    vertical: 'bottom',
                    horizontal: 'right',
                }}
                transformOrigin={{
                    vertical: 'top',
                    horizontal: 'right',
                }}
            >
                <Box sx={{ width: 360, p: 2 }}>
                    <Typography variant="h6" gutterBottom>
                        Notifications
                    </Typography>
                    {notifications.length === 0 ? (
                        <Typography variant="body2" color="text.secondary">
                            No new notifications
                        </Typography>
                    ) : (
                        <>
                            <List>
                                {notifications.map((notification) => (
                                    <ListItem key={notification.id}>
                                        <ListItemText
                                            primary={notification.title}
                                            secondary={notification.message}
                                        />
                                    </ListItem>
                                ))}
                            </List>
                            <Button
                                fullWidth
                                onClick={() => markAsRead(notifications.map(n => n.id))}
                            >
                                Mark all as read
                            </Button>
                        </>
                    )}
                </Box>
            </Popover>
        </>
    );
};

export default NotificationCenter; 