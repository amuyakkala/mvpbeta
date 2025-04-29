import React from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Button,
  Container,
  Typography,
  Grid,
  Paper,
  Card,
  CardContent,
  Stack,
  useTheme,
  useMediaQuery,
  IconButton,
  alpha,
} from '@mui/material';
import { styled } from '@mui/material/styles';
import ArrowForwardIcon from '@mui/icons-material/ArrowForward';
import SecurityIcon from '@mui/icons-material/Security';
import AnalyticsIcon from '@mui/icons-material/Analytics';
import NotificationsActiveIcon from '@mui/icons-material/NotificationsActive';
import TimelineIcon from '@mui/icons-material/Timeline';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';

const HeroSection = styled(Box)(({ theme }) => ({
  background: `linear-gradient(135deg, ${alpha(theme.palette.primary.main, 0.95)} 0%, ${alpha(theme.palette.primary.light, 0.95)} 100%)`,
  color: 'white',
  padding: theme.spacing(15, 0),
  marginBottom: theme.spacing(8),
  position: 'relative',
  overflow: 'hidden',
  '&::before': {
    content: '""',
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    background: 'url("https://source.unsplash.com/random/1920x1080/?technology,abstract")',
    backgroundSize: 'cover',
    backgroundPosition: 'center',
    opacity: 0.15,
    zIndex: 0,
  },
}));

const FeatureCard = styled(Card)(({ theme }) => ({
  height: '100%',
  display: 'flex',
  flexDirection: 'column',
  transition: 'all 0.3s ease-in-out',
  border: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
  '&:hover': {
    transform: 'translateY(-8px)',
    boxShadow: theme.shadows[8],
    borderColor: theme.palette.primary.main,
  },
}));

const StatCard = styled(Paper)(({ theme }) => ({
  padding: theme.spacing(4),
  textAlign: 'center',
  background: `linear-gradient(45deg, ${alpha(theme.palette.primary.main, 0.9)} 30%, ${alpha(theme.palette.primary.light, 0.9)} 90%)`,
  color: 'white',
  borderRadius: theme.shape.borderRadius * 2,
  transition: 'transform 0.3s ease-in-out',
  '&:hover': {
    transform: 'scale(1.05)',
  },
}));

const features = [
  {
    title: 'Trace Analysis',
    description: 'Automated analysis of system traces to identify patterns and anomalies with AI-powered insights.',
    icon: <AnalyticsIcon sx={{ fontSize: 40 }} />,
    color: 'primary.main',
  },
  {
    title: 'Issue Management',
    description: 'Track and manage issues with detailed categorization, prioritization, and resolution tracking.',
    icon: <TimelineIcon sx={{ fontSize: 40 }} />,
    color: 'secondary.main',
  },
  {
    title: 'Audit Trail',
    description: 'Comprehensive logging of all system activities with advanced search and filtering capabilities.',
    icon: <SecurityIcon sx={{ fontSize: 40 }} />,
    color: 'success.main',
  },
  {
    title: 'Real-time Notifications',
    description: 'Stay informed with instant alerts and customizable notification preferences.',
    icon: <NotificationsActiveIcon sx={{ fontSize: 40 }} />,
    color: 'warning.main',
  },
];

const stats = [
  { value: '99.9%', label: 'System Uptime' },
  { value: '24/7', label: 'Support' },
  { value: '1000+', label: 'Active Users' },
  { value: '50+', label: 'Features' },
];

const benefits = [
  {
    title: 'Intelligent Analysis',
    description: 'Our AI-powered system automatically analyzes traces and identifies potential issues before they become problems, saving you time and resources.',
    icon: <AnalyticsIcon />,
  },
  {
    title: 'Comprehensive Management',
    description: 'Manage all your system issues in one place with powerful categorization, prioritization, and collaboration tools for your entire team.',
    icon: <TimelineIcon />,
  },
  {
    title: 'Secure & Reliable',
    description: 'Enterprise-grade security with comprehensive audit trails, real-time notifications, and 24/7 monitoring to ensure your system\'s integrity.',
    icon: <SecurityIcon />,
  },
];

export default function Home() {
  const navigate = useNavigate();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));

  return (
    <Box>
      <HeroSection>
        <Container maxWidth="lg" sx={{ position: 'relative', zIndex: 1 }}>
          <Grid container spacing={6} alignItems="center">
            <Grid item xs={12} md={6}>
              <Typography
                variant={isMobile ? 'h3' : 'h2'}
                component="h1"
                gutterBottom
                sx={{ 
                  fontWeight: 800,
                  background: `linear-gradient(45deg, ${theme.palette.common.white} 30%, ${alpha(theme.palette.common.white, 0.8)} 90%)`,
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                }}
              >
                EchosysAI
              </Typography>
              <Typography 
                variant="h5" 
                paragraph 
                sx={{ 
                  opacity: 0.9,
                  fontWeight: 500,
                  mb: 3,
                }}
              >
                Intelligent System Analysis and Issue Management Platform
              </Typography>
              <Typography 
                variant="body1" 
                paragraph 
                sx={{ 
                  mb: 4, 
                  opacity: 0.8,
                  fontSize: '1.1rem',
                  lineHeight: 1.7,
                }}
              >
                Transform your system monitoring with AI-powered insights, comprehensive issue tracking,
                and real-time notifications. EchosysAI helps you maintain system health and security
                with advanced analytics and automated workflows.
              </Typography>
              <Stack 
                direction={isMobile ? 'column' : 'row'} 
                spacing={2}
                sx={{ mb: 4 }}
              >
                <Button
                  variant="contained"
                  color="primary"
                  size="large"
                  endIcon={<ArrowForwardIcon />}
                  onClick={() => navigate('/login')}
                  sx={{ 
                    px: 4,
                    py: 1.5,
                    borderRadius: 2,
                    textTransform: 'none',
                    fontSize: '1.1rem',
                    fontWeight: 600,
                    boxShadow: theme.shadows[4],
                    '&:hover': {
                      boxShadow: theme.shadows[8],
                    },
                  }}
                >
                  Get Started
                </Button>
                <Button
                  variant="outlined"
                  color="inherit"
                  size="large"
                  onClick={() => navigate('/register')}
                  sx={{ 
                    px: 4,
                    py: 1.5,
                    borderRadius: 2,
                    textTransform: 'none',
                    fontSize: '1.1rem',
                    fontWeight: 600,
                    borderWidth: 2,
                    '&:hover': {
                      borderWidth: 2,
                      backgroundColor: alpha(theme.palette.common.white, 0.1),
                    },
                  }}
                >
                  Sign Up
                </Button>
              </Stack>
              <Stack direction="row" spacing={2} alignItems="center">
                <CheckCircleIcon color="success" />
                <Typography variant="body2" sx={{ opacity: 0.8 }}>
                  Trusted by leading enterprises worldwide
                </Typography>
              </Stack>
            </Grid>
            <Grid item xs={12} md={6}>
              <Paper
                elevation={6}
                sx={{
                  p: 4,
                  background: alpha(theme.palette.common.white, 0.1),
                  backdropFilter: 'blur(10px)',
                  borderRadius: 4,
                  border: `1px solid ${alpha(theme.palette.common.white, 0.2)}`,
                }}
              >
                <Typography 
                  variant="h6" 
                  gutterBottom 
                  sx={{ 
                    fontWeight: 600,
                    mb: 3,
                  }}
                >
                  Key Features
                </Typography>
                <Stack spacing={2}>
                  {[
                    'AI-powered trace analysis',
                    'Automated issue detection',
                    'Real-time system monitoring',
                    'Comprehensive audit trails',
                    'Customizable alerts',
                    'Team collaboration tools',
                  ].map((feature, index) => (
                    <Box 
                      key={index} 
                      sx={{ 
                        display: 'flex', 
                        alignItems: 'center',
                        transition: 'transform 0.2s ease-in-out',
                        '&:hover': {
                          transform: 'translateX(8px)',
                        },
                      }}
                    >
                      <IconButton 
                        size="small" 
                        sx={{ 
                          color: 'white', 
                          mr: 2,
                          background: alpha(theme.palette.common.white, 0.1),
                          '&:hover': {
                            background: alpha(theme.palette.common.white, 0.2),
                          },
                        }}
                      >
                        <CheckCircleIcon fontSize="small" />
                      </IconButton>
                      <Typography>{feature}</Typography>
                    </Box>
                  ))}
                </Stack>
              </Paper>
            </Grid>
          </Grid>
        </Container>
      </HeroSection>

      <Container maxWidth="lg" sx={{ mb: 12 }}>
        <Typography
          variant="h4"
          align="center"
          gutterBottom
          sx={{ 
            fontWeight: 700,
            mb: 8,
            position: 'relative',
            '&::after': {
              content: '""',
              position: 'absolute',
              bottom: -16,
              left: '50%',
              transform: 'translateX(-50%)',
              width: 80,
              height: 4,
              background: `linear-gradient(45deg, ${theme.palette.primary.main}, ${theme.palette.primary.light})`,
              borderRadius: 2,
            },
          }}
        >
          Features
        </Typography>
        <Grid container spacing={4}>
          {features.map((feature, index) => (
            <Grid item xs={12} sm={6} md={3} key={index}>
              <FeatureCard>
                <CardContent sx={{ textAlign: 'center', p: 4 }}>
                  <Box
                    sx={{
                      color: feature.color,
                      mb: 3,
                      display: 'flex',
                      justifyContent: 'center',
                      '& svg': {
                        fontSize: 48,
                      },
                    }}
                  >
                    {feature.icon}
                  </Box>
                  <Typography 
                    variant="h6" 
                    component="h2" 
                    gutterBottom 
                    sx={{ 
                      fontWeight: 600,
                      mb: 2,
                    }}
                  >
                    {feature.title}
                  </Typography>
                  <Typography 
                    variant="body2" 
                    color="text.secondary"
                    sx={{
                      lineHeight: 1.6,
                    }}
                  >
                    {feature.description}
                  </Typography>
                </CardContent>
              </FeatureCard>
            </Grid>
          ))}
        </Grid>
      </Container>

      <Box sx={{ bgcolor: 'grey.50', py: 12 }}>
        <Container maxWidth="lg">
          <Typography
            variant="h4"
            align="center"
            gutterBottom
            sx={{ 
              fontWeight: 700,
              mb: 8,
              position: 'relative',
              '&::after': {
                content: '""',
                position: 'absolute',
                bottom: -16,
                left: '50%',
                transform: 'translateX(-50%)',
                width: 80,
                height: 4,
                background: `linear-gradient(45deg, ${theme.palette.primary.main}, ${theme.palette.primary.light})`,
                borderRadius: 2,
              },
            }}
          >
            Why Choose EchosysAI?
          </Typography>
          <Grid container spacing={4}>
            {benefits.map((benefit, index) => (
              <Grid item xs={12} md={4} key={index}>
                <Paper 
                  sx={{ 
                    p: 4, 
                    height: '100%', 
                    borderRadius: 4,
                    transition: 'all 0.3s ease-in-out',
                    '&:hover': {
                      transform: 'translateY(-8px)',
                      boxShadow: theme.shadows[8],
                    },
                  }}
                >
                  <Box
                    sx={{
                      color: theme.palette.primary.main,
                      mb: 2,
                      '& svg': {
                        fontSize: 40,
                      },
                    }}
                  >
                    {benefit.icon}
                  </Box>
                  <Typography 
                    variant="h6" 
                    gutterBottom 
                    sx={{ 
                      fontWeight: 600,
                      mb: 2,
                    }}
                  >
                    {benefit.title}
                  </Typography>
                  <Typography
                    sx={{
                      lineHeight: 1.7,
                      color: 'text.secondary',
                    }}
                  >
                    {benefit.description}
                  </Typography>
                </Paper>
              </Grid>
            ))}
          </Grid>
        </Container>
      </Box>

      <Container maxWidth="lg" sx={{ py: 12 }}>
        <Typography
          variant="h4"
          align="center"
          gutterBottom
          sx={{ 
            fontWeight: 700,
            mb: 8,
            position: 'relative',
            '&::after': {
              content: '""',
              position: 'absolute',
              bottom: -16,
              left: '50%',
              transform: 'translateX(-50%)',
              width: 80,
              height: 4,
              background: `linear-gradient(45deg, ${theme.palette.primary.main}, ${theme.palette.primary.light})`,
              borderRadius: 2,
            },
          }}
        >
          Our Numbers
        </Typography>
        <Grid container spacing={4}>
          {stats.map((stat, index) => (
            <Grid item xs={6} sm={3} key={index}>
              <StatCard>
                <Typography 
                  variant="h3" 
                  component="div" 
                  sx={{ 
                    fontWeight: 800,
                    mb: 1,
                  }}
                >
                  {stat.value}
                </Typography>
                <Typography 
                  variant="h6" 
                  sx={{ 
                    opacity: 0.9,
                    fontWeight: 500,
                  }}
                >
                  {stat.label}
                </Typography>
              </StatCard>
            </Grid>
          ))}
        </Grid>
      </Container>

      <Box 
        sx={{ 
          background: `linear-gradient(135deg, ${alpha(theme.palette.primary.main, 0.95)} 0%, ${alpha(theme.palette.primary.light, 0.95)} 100%)`,
          color: 'white', 
          py: 12,
          position: 'relative',
          overflow: 'hidden',
          '&::before': {
            content: '""',
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: 'url("https://source.unsplash.com/random/1920x1080/?technology,abstract")',
            backgroundSize: 'cover',
            backgroundPosition: 'center',
            opacity: 0.1,
            zIndex: 0,
          },
        }}
      >
        <Container 
          maxWidth="md" 
          sx={{ 
            textAlign: 'center',
            position: 'relative',
            zIndex: 1,
          }}
        >
          <Typography 
            variant="h4" 
            gutterBottom 
            sx={{ 
              fontWeight: 700,
              mb: 3,
            }}
          >
            Ready to Get Started?
          </Typography>
          <Typography 
            variant="body1" 
            paragraph 
            sx={{ 
              mb: 4, 
              opacity: 0.9,
              fontSize: '1.1rem',
              lineHeight: 1.7,
            }}
          >
            Join thousands of satisfied users who trust EchosysAI for their system monitoring needs.
            Start your free trial today and experience the difference.
          </Typography>
          <Button
            variant="contained"
            color="secondary"
            size="large"
            endIcon={<ArrowForwardIcon />}
            onClick={() => navigate('/register')}
            sx={{
              px: 6,
              py: 1.5,
              borderRadius: 2,
              textTransform: 'none',
              fontSize: '1.1rem',
              fontWeight: 600,
              boxShadow: theme.shadows[4],
              '&:hover': {
                boxShadow: theme.shadows[8],
              },
            }}
          >
            Start Free Trial
          </Button>
        </Container>
      </Box>
    </Box>
  );
} 