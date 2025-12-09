import { useNavigate } from 'react-router-dom';
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  CardActions,
  Button,
  Paper,
  Chip,
  Stack
} from '@mui/material';
import {
  Image as ImageIcon,
  VideoLibrary as VideoIcon,
  TextFields as TextIcon,
  CheckCircle as CheckIcon,
  ArrowForward as ArrowIcon
} from '@mui/icons-material';

export default function Home() {
  const navigate = useNavigate();

  const features = [
    {
      title: 'Image Processing',
      description: 'Detect and anonymize faces, license plates, and sensitive objects in images',
      icon: <ImageIcon sx={{ fontSize: 48 }} />,
      path: '/images',
      badge: 'Available',
      gradient: 'linear-gradient(135deg, #3b82f6 0%, #0ea5e9 100%)',
    },
    {
      title: 'Video processing',
      description: 'Process videos frame-by-frame with real-time visualization',
      icon: <VideoIcon sx={{ fontSize: 48 }} />,
      path: '/videos',
      badge: 'Available',
      gradient: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
    },
    {
      title: 'Text analysis',
      description: 'Detect sensitive text data using OCR and local AI',
      icon: <TextIcon sx={{ fontSize: 48 }} />,
      path: '/text',
      badge: 'AI Powered',
      gradient: 'linear-gradient(135deg, #10b981 0%, #34d399 100%)',
    }
  ];

  const stats = [
    { label: 'Detection Classes', value: '82+', gradient: 'linear-gradient(135deg, #3b82f6 0%, #0ea5e9 100%)' },
    { label: 'F1-Score (faces)', value: '90.49%', gradient: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)' },
    { label: 'F1-Score (plates)', value: '89.97%', gradient: 'linear-gradient(135deg, #10b981 0%, #34d399 100%)' },
    { label: 'Processing Speed', value: '~30 FPS', gradient: 'linear-gradient(135deg, #64748b 0%, #94a3b8 100%)' }
  ];

  const capabilities = [
    'Faces and license plates',
    'Vehicles and people',
    'Documents (DNI, passports)',
    'Text detection (phone, email)',
    'QR codes and barcodes',
    'Electronics (phones, screens)',
    '100% Local (GDPR)'
  ];

  return (
    <Box>
      {/* Hero Section */}
      <Paper
        elevation={0}
        sx={{
          p: { xs: 4, md: 6 },
          mb: 4,
          background: 'linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(14, 165, 233, 0.1) 50%, rgba(99, 102, 241, 0.08) 100%)',
          borderRadius: 4,
          position: 'relative',
          overflow: 'hidden',
          '&::before': {
            content: '""',
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: 'radial-gradient(circle at 20% 50%, rgba(59, 130, 246, 0.15) 0%, transparent 50%)',
            pointerEvents: 'none',
          },
        }}
      >
        <Box sx={{ position: 'relative', zIndex: 1 }}>
          <Typography
            variant="h3"
            gutterBottom
            sx={{
              fontWeight: 700,
              background: 'linear-gradient(135deg, #3b82f6 0%, #0ea5e9 50%, #6366f1 100%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              mb: 2,
            }}
          >
            TFM Anonymization System
          </Typography>
          <Typography
            variant="h6"
            sx={{
              mb: 2,
              color: 'text.secondary',
              fontWeight: 400,
              maxWidth: 600,
            }}
          >
            Automatic Detection and Anonymization of Sensitive Data in Images and Videos
          </Typography>
          <Chip
            label="AI-Powered • GDPR Compliant • 100% Local"
            sx={{
              background: 'linear-gradient(135deg, rgba(59, 130, 246, 0.15) 0%, rgba(14, 165, 233, 0.15) 100%)',
              fontWeight: 500,
              px: 1,
            }}
          />
        </Box>
      </Paper>

      {/* Stats */}
      <Grid container spacing={2} sx={{ mb: 5 }}>
        {stats.map((stat, index) => (
          <Grid item xs={6} sm={6} md={3} key={index}>
            <Card
              sx={{
                textAlign: 'center',
                height: '100%',
                position: 'relative',
                overflow: 'hidden',
                '&::before': {
                  content: '""',
                  position: 'absolute',
                  top: 0,
                  left: 0,
                  right: 0,
                  height: 4,
                  background: stat.gradient,
                },
              }}
            >
              <CardContent sx={{ pt: 3 }}>
                <Typography
                  variant="h4"
                  sx={{
                    fontWeight: 700,
                    background: stat.gradient,
                    WebkitBackgroundClip: 'text',
                    WebkitTextFillColor: 'transparent',
                  }}
                >
                  {stat.value}
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ fontWeight: 500 }}>
                  {stat.label}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Features */}
      <Typography variant="h5" gutterBottom sx={{ mb: 3, fontWeight: 600 }}>
        Get Started
      </Typography>
      <Grid container spacing={3} sx={{ mb: 5 }}>
        {features.map((feature, index) => (
          <Grid item xs={12} md={4} key={index}>
            <Card
              sx={{
                height: '100%',
                display: 'flex',
                flexDirection: 'column',
                cursor: 'pointer',
              }}
              onClick={() => navigate(feature.path)}
            >
              <CardContent sx={{ flexGrow: 1, textAlign: 'center', pt: 4 }}>
                <Box
                  sx={{
                    mb: 3,
                    width: 80,
                    height: 80,
                    borderRadius: 3,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    mx: 'auto',
                    background: feature.gradient,
                    color: 'white',
                    boxShadow: `0 8px 24px ${feature.gradient.includes('3b82f6') ? 'rgba(59, 130, 246, 0.3)' : feature.gradient.includes('6366f1') ? 'rgba(99, 102, 241, 0.3)' : 'rgba(16, 185, 129, 0.3)'}`,
                  }}
                >
                  {feature.icon}
                </Box>
                <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
                  {feature.title}
                </Typography>
                <Chip
                  label={feature.badge}
                  size="small"
                  sx={{
                    mb: 2,
                    fontWeight: 500,
                    background: 'rgba(59, 130, 246, 0.1)',
                    color: feature.badge === 'AI Powered' ? '#10b981' : '#3b82f6',
                  }}
                />
                <Typography variant="body2" color="text.secondary">
                  {feature.description}
                </Typography>
              </CardContent>
              <CardActions sx={{ justifyContent: 'center', pb: 3 }}>
                <Button
                  variant="contained"
                  endIcon={<ArrowIcon />}
                  onClick={(e) => { e.stopPropagation(); navigate(feature.path); }}
                  sx={{
                    background: feature.gradient,
                    px: 4,
                    '&:hover': {
                      background: feature.gradient,
                      filter: 'brightness(1.1)',
                    },
                  }}
                >
                  Start Processing
                </Button>
              </CardActions>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Capabilities */}
      <Paper sx={{ p: 4, mb: 4 }}>
        <Typography variant="h6" gutterBottom sx={{ fontWeight: 600, mb: 3 }}>
          Detection Capabilities
        </Typography>
        <Stack direction="row" flexWrap="wrap" gap={1.5}>
          {capabilities.map((capability, index) => (
            <Chip
              key={index}
              icon={<CheckIcon sx={{ fontSize: 18 }} />}
              label={capability}
              sx={{
                py: 0.5,
                fontWeight: 500,
                background: 'linear-gradient(135deg, rgba(59, 130, 246, 0.08) 0%, rgba(14, 165, 233, 0.08) 100%)',
                border: '1px solid rgba(59, 130, 246, 0.15)',
                '& .MuiChip-icon': {
                  color: '#10b981',
                },
              }}
            />
          ))}
        </Stack>
      </Paper>

      {/* Quick Info */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
                GDPR Compliance
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Fully compliant with GDPR requirements for personal data protection.
                All processing is done locally on your machine - no data leaves your system.
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={6}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
                High Performance
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Powered by YOLOv8 and running on your GPU for real-time processing.
                Process images at ~30 FPS and videos with minimal latency.
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
}

