import {
  Box,
  Typography,
  Paper,
  List,
  ListItem,
  ListItemText,
  Divider,
  Chip
} from '@mui/material';
import {
  Speed as SpeedIcon,
  Memory as MemoryIcon,
  Storage as StorageIcon,
  CloudOff as LocalIcon
} from '@mui/icons-material';

export default function Settings() {
  const systemInfo = [
    { label: 'Backend Status', value: 'Running', icon: <SpeedIcon />, color: 'success' },
    { label: 'GPU', value: 'NVIDIA RTX 5080', icon: <MemoryIcon />, color: 'primary' },
    { label: 'Model', value: 'YOLOv8n Unified (6.0 MB)', icon: <StorageIcon />, color: 'primary' },
    { label: 'Processing', value: '100% Local', icon: <LocalIcon />, color: 'success' }
  ];

  const models = [
    { name: 'Unified Detector', classes: 2, status: 'Loaded', f1_faces: '90.49%', f1_plates: '89.97%' },
    { name: 'COCO Detector', classes: 80, status: 'Available', f1: 'Variable' }
  ];

  return (
    <Box>
      <Typography variant="h4" gutterBottom sx={{ fontWeight: 600 }}>
        Settings
      </Typography>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
        System configuration and information
      </Typography>

      {/* System Info */}
      <Paper sx={{ p: 3, mb: 3, borderRadius: 3 }}>
        <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
          System Information
        </Typography>
        <List>
          {systemInfo.map((item, index) => (
            <Box key={index}>
              <ListItem>
                <Box sx={{ mr: 2 }}>{item.icon}</Box>
                <ListItemText
                  primary={item.label}
                  secondary={item.value}
                />
                <Chip label={item.value} color={item.color} size="small" />
              </ListItem>
              {index < systemInfo.length - 1 && <Divider />}
            </Box>
          ))}
        </List>
      </Paper>

      {/* Models Info */}
      <Paper sx={{ p: 3, borderRadius: 3 }}>
        <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
          Loaded Models
        </Typography>
        <List>
          {models.map((model, index) => (
            <Box key={index}>
              <ListItem>
                <ListItemText
                  primary={model.name}
                  secondary={`${model.classes} classes | ${model.f1_faces || model.f1}`}
                />
                <Chip
                  label={model.status}
                  color={model.status === 'Loaded' ? 'success' : 'default'}
                  size="small"
                />
              </ListItem>
              {index < models.length - 1 && <Divider />}
            </Box>
          ))}
        </List>
      </Paper>
    </Box>
  );
}
