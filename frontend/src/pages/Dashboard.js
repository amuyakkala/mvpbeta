import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Paper,
  Typography,
  Card,
  CardContent,
  CardHeader,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
  useTheme,
  useMediaQuery,
  LinearProgress,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  TrendingUp as TrendingUpIcon,
  Warning as WarningIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Refresh as RefreshIcon,
  ArrowUpward as ArrowUpwardIcon,
  ArrowDownward as ArrowDownwardIcon,
} from '@mui/icons-material';
import { format } from 'date-fns';
import api from '../services/api';

const StatCard = ({ title, value, change, icon, color }) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));

  return (
    <Card
      sx={{
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        transition: 'all 0.3s ease-in-out',
        '&:hover': {
          transform: 'translateY(-4px)',
          boxShadow: theme.shadows[8],
        },
      }}
    >
      <CardContent sx={{ flexGrow: 1, p: isMobile ? 2 : 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <Box
            sx={{
              backgroundColor: `${color}20`,
              color: color,
              borderRadius: '50%',
              p: 1,
              mr: 2,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            {icon}
          </Box>
          <Typography variant="h6" color="text.secondary">
            {title}
          </Typography>
        </Box>
        <Typography variant="h4" component="div" sx={{ mb: 1, fontWeight: 600 }}>
          {value}
        </Typography>
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          {change >= 0 ? (
            <ArrowUpwardIcon color="success" fontSize="small" />
          ) : (
            <ArrowDownwardIcon color="error" fontSize="small" />
          )}
          <Typography
            variant="body2"
            color={change >= 0 ? 'success.main' : 'error.main'}
            sx={{ ml: 0.5 }}
          >
            {Math.abs(change)}% from last week
          </Typography>
        </Box>
      </CardContent>
    </Card>
  );
};

const RecentActivityCard = ({ activities }) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));

  const getActivityIcon = (type) => {
    switch (type) {
      case 'success':
        return <CheckCircleIcon color="success" />;
      case 'warning':
        return <WarningIcon color="warning" />;
      case 'error':
        return <ErrorIcon color="error" />;
      default:
        return <TrendingUpIcon color="primary" />;
    }
  };

  return (
    <Card sx={{ height: '100%' }}>
      <CardHeader
        title="Recent Activities"
        action={
          <Tooltip title="Refresh">
            <IconButton>
              <RefreshIcon />
            </IconButton>
          </Tooltip>
        }
      />
      <Divider />
      <CardContent sx={{ p: 0 }}>
        <List>
          {activities.map((activity, index) => (
            <React.Fragment key={index}>
              <ListItem>
                <ListItemIcon>{getActivityIcon(activity.type)}</ListItemIcon>
                <ListItemText
                  primary={activity.message}
                  secondary={format(new Date(activity.timestamp), 'PPpp')}
                />
              </ListItem>
              {index < activities.length - 1 && <Divider />}
            </React.Fragment>
          ))}
        </List>
      </CardContent>
    </Card>
  );
};

const SystemHealthCard = ({ healthData }) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));

  return (
    <Card sx={{ height: '100%' }}>
      <CardHeader title="System Health" />
      <Divider />
      <CardContent>
        {healthData.map((item, index) => (
          <Box key={index} sx={{ mb: 2 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
              <Typography variant="body2">{item.name}</Typography>
              <Typography variant="body2" color="text.secondary">
                {item.value}%
              </Typography>
            </Box>
            <LinearProgress
              variant="determinate"
              value={item.value}
              sx={{
                height: 8,
                borderRadius: 4,
                backgroundColor: theme.palette.grey[200],
                '& .MuiLinearProgress-bar': {
                  backgroundColor:
                    item.value > 80
                      ? theme.palette.success.main
                      : item.value > 50
                      ? theme.palette.warning.main
                      : theme.palette.error.main,
                },
              }}
            />
          </Box>
        ))}
      </CardContent>
    </Card>
  );
};

export default function Dashboard() {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const [stats, setStats] = useState({
    totalTraces: 0,
    activeIssues: 0,
    systemHealth: 0,
    responseTime: 0,
  });
  const [activities, setActivities] = useState([]);
  const [healthData, setHealthData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        // Fetch dashboard data from API
        const [statsResponse, activitiesResponse, healthResponse] = await Promise.all([
          api.get('/dashboard/stats'),
          api.get('/dashboard/activities'),
          api.get('/dashboard/health'),
        ]);

        setStats(statsResponse.data);
        setActivities(activitiesResponse.data);
        setHealthData(healthResponse.data);
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  if (loading) {
    return (
      <Box sx={{ width: '100%', p: 3 }}>
        <LinearProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ p: isMobile ? 2 : 3 }}>
      <Typography variant="h4" gutterBottom sx={{ mb: 4, fontWeight: 600 }}>
        Dashboard Overview
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Traces"
            value={stats.totalTraces}
            change={12}
            icon={<TrendingUpIcon />}
            color={theme.palette.primary.main}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Active Issues"
            value={stats.activeIssues}
            change={-5}
            icon={<WarningIcon />}
            color={theme.palette.warning.main}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="System Health"
            value={`${stats.systemHealth}%`}
            change={2}
            icon={<CheckCircleIcon />}
            color={theme.palette.success.main}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Avg Response Time"
            value={`${stats.responseTime}ms`}
            change={-8}
            icon={<TrendingUpIcon />}
            color={theme.palette.info.main}
          />
        </Grid>

        <Grid item xs={12} md={8}>
          <RecentActivityCard activities={activities} />
        </Grid>
        <Grid item xs={12} md={4}>
          <SystemHealthCard healthData={healthData} />
        </Grid>
      </Grid>
    </Box>
  );
} 