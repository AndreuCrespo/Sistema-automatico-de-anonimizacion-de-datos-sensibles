import { useState } from 'react';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import {
  Box,
  Drawer,
  AppBar,
  Toolbar,
  List,
  Typography,
  Divider,
  IconButton,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Container,
  Switch,
  Tooltip,
  Avatar
} from '@mui/material';
import {
  Menu as MenuIcon,
  Home as HomeIcon,
  Image as ImageIcon,
  VideoLibrary as VideoIcon,
  TextFields as TextIcon,
  Settings as SettingsIcon,
  Brightness4 as DarkModeIcon,
  Brightness7 as LightModeIcon,
  Security as SecurityIcon
} from '@mui/icons-material';

const drawerWidth = 260;

const menuItems = [
  { text: 'Home', icon: <HomeIcon />, path: '/' },
  { text: 'Images', icon: <ImageIcon />, path: '/images' },
  { text: 'Videos', icon: <VideoIcon />, path: '/videos' },
  { text: 'Text Analysis', icon: <TextIcon />, path: '/text' },
  { text: 'Settings', icon: <SettingsIcon />, path: '/settings' },
];

export default function MainLayout({ darkMode, toggleTheme }) {
  const [mobileOpen, setMobileOpen] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  const handleNavigation = (path) => {
    navigate(path);
    setMobileOpen(false);
  };

  const drawer = (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Logo Section */}
      <Box sx={{ p: 3, display: 'flex', alignItems: 'center', gap: 2 }}>
        <Avatar
          sx={{
            width: 44,
            height: 44,
            background: 'linear-gradient(135deg, #3b82f6 0%, #0ea5e9 100%)',
            boxShadow: '0 4px 14px rgba(59, 130, 246, 0.35)',
          }}
        >
          <SecurityIcon sx={{ fontSize: 24 }} />
        </Avatar>
        <Box>
          <Typography
            variant="h6"
            sx={{
              fontWeight: 700,
              background: 'linear-gradient(135deg, #3b82f6 0%, #0ea5e9 100%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
            }}
          >
            TFM
          </Typography>
          <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 500 }}>
            Anonimización
          </Typography>
        </Box>
      </Box>

      <Divider sx={{ opacity: 0.1 }} />

      {/* Navigation */}
      <List sx={{ px: 2, py: 3, flexGrow: 1 }}>
        {menuItems.map((item) => {
          const isSelected = location.pathname === item.path;
          return (
            <ListItem key={item.text} disablePadding sx={{ mb: 1 }}>
              <ListItemButton
                selected={isSelected}
                onClick={() => handleNavigation(item.path)}
                sx={{
                  borderRadius: 3,
                  py: 1.5,
                  transition: 'all 0.2s ease',
                  '&.Mui-selected': {
                    background: 'linear-gradient(135deg, rgba(59, 130, 246, 0.15) 0%, rgba(14, 165, 233, 0.15) 100%)',
                    '& .MuiListItemIcon-root': {
                      color: '#60a5fa',
                    },
                    '&:hover': {
                      background: 'linear-gradient(135deg, rgba(59, 130, 246, 0.25) 0%, rgba(14, 165, 233, 0.25) 100%)',
                    },
                  },
                  '&:hover': {
                    background: 'rgba(59, 130, 246, 0.1)',
                    transform: 'translateX(4px)',
                  },
                }}
              >
                <ListItemIcon
                  sx={{
                    minWidth: 40,
                    color: isSelected ? '#60a5fa' : 'text.secondary',
                    transition: 'color 0.2s ease',
                  }}
                >
                  {item.icon}
                </ListItemIcon>
                <ListItemText
                  primary={item.text}
                  primaryTypographyProps={{
                    fontWeight: isSelected ? 600 : 400,
                    fontSize: '0.95rem',
                  }}
                />
              </ListItemButton>
            </ListItem>
          );
        })}
      </List>

      <Divider sx={{ opacity: 0.1 }} />

      {/* Theme Toggle */}
      <Box sx={{ p: 2 }}>
        <ListItem
          sx={{
            px: 2,
            py: 1.5,
            borderRadius: 3,
            background: 'rgba(59, 130, 246, 0.05)',
          }}
        >
          <ListItemIcon sx={{ minWidth: 40, color: 'text.secondary' }}>
            {darkMode ? <LightModeIcon /> : <DarkModeIcon />}
          </ListItemIcon>
          <ListItemText
            primary="Dark Mode"
            primaryTypographyProps={{ fontSize: '0.9rem' }}
          />
          <Switch
            checked={darkMode}
            onChange={toggleTheme}
            size="small"
            sx={{
              '& .MuiSwitch-switchBase.Mui-checked': {
                color: '#60a5fa',
              },
              '& .MuiSwitch-switchBase.Mui-checked + .MuiSwitch-track': {
                backgroundColor: '#3b82f6',
              },
            }}
          />
        </ListItem>
      </Box>
    </Box>
  );

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh' }}>
      {/* AppBar */}
      <AppBar
        position="fixed"
        sx={{
          width: { sm: `calc(100% - ${drawerWidth}px)` },
          ml: { sm: `${drawerWidth}px` },
        }}
      >
        <Toolbar sx={{ justifyContent: 'space-between' }}>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <IconButton
              color="inherit"
              aria-label="open drawer"
              edge="start"
              onClick={handleDrawerToggle}
              sx={{ mr: 2, display: { sm: 'none' } }}
            >
              <MenuIcon />
            </IconButton>
            <Typography
              variant="h6"
              noWrap
              component="div"
              sx={{ fontWeight: 600, color: 'text.primary' }}
            >
              {menuItems.find(item => item.path === location.pathname)?.text || 'TFM Anonimización'}
            </Typography>
          </Box>
          <Tooltip title={darkMode ? "Switch to Light Mode" : "Switch to Dark Mode"}>
            <IconButton
              onClick={toggleTheme}
              sx={{
                display: { xs: 'none', sm: 'flex' },
                color: 'text.primary',
                '&:hover': {
                  background: 'rgba(59, 130, 246, 0.1)',
                },
              }}
            >
              {darkMode ? <LightModeIcon /> : <DarkModeIcon />}
            </IconButton>
          </Tooltip>
        </Toolbar>
      </AppBar>

      {/* Drawer */}
      <Box
        component="nav"
        sx={{ width: { sm: drawerWidth }, flexShrink: { sm: 0 } }}
      >
        {/* Mobile drawer */}
        <Drawer
          variant="temporary"
          open={mobileOpen}
          onClose={handleDrawerToggle}
          ModalProps={{ keepMounted: true }}
          sx={{
            display: { xs: 'block', sm: 'none' },
            '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
          }}
        >
          {drawer}
        </Drawer>

        {/* Desktop drawer */}
        <Drawer
          variant="permanent"
          sx={{
            display: { xs: 'none', sm: 'block' },
            '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
          }}
          open
        >
          {drawer}
        </Drawer>
      </Box>

      {/* Main content */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          width: { sm: `calc(100% - ${drawerWidth}px)` },
          minHeight: '100vh',
          display: 'flex',
          flexDirection: 'column',
        }}
      >
        <Toolbar />
        <Container
          maxWidth="xl"
          sx={{
            mt: 4,
            mb: 4,
            flexGrow: 1,
            px: { xs: 2, sm: 4 },
          }}
        >
          <Outlet />
        </Container>

        {/* Footer */}
        <Box
          sx={{
            mt: 'auto',
            py: 3,
            px: 2,
            textAlign: 'center',
          }}
        >
          <Typography variant="body2" color="text.secondary" sx={{ fontWeight: 500 }}>
            TFM - Master en Inteligencia Artificial - UNIR
          </Typography>
          <Typography variant="caption" color="text.secondary">
            Andreu Crespo Barberá © 2025
          </Typography>
        </Box>
      </Box>
    </Box>
  );
}

