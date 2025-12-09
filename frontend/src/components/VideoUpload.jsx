import { useState } from 'react';
import {
  Box,
  Button,
  Paper,
  Typography,
  LinearProgress,
  Alert
} from '@mui/material';
import {
  CloudUpload as UploadIcon,
  VideoFile as VideoIcon
} from '@mui/icons-material';

export default function VideoUpload({ onVideoSelect, disabled = false }) {
  const [dragActive, setDragActive] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0]);
    }
  };

  const handleChange = (e) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0]);
    }
  };

  const handleFile = (file) => {
    // Validar que sea un video
    const validTypes = ['video/mp4', 'video/avi', 'video/mov', 'video/quicktime', 'video/x-matroska'];
    if (!validTypes.includes(file.type)) {
      alert('Por favor selecciona un archivo de video válido (MP4, AVI, MOV, MKV)');
      return;
    }

    // Validar tamaño (máximo 500MB)
    const maxSize = 500 * 1024 * 1024; // 500MB
    if (file.size > maxSize) {
      alert('El archivo es demasiado grande. Tamaño máximo: 500MB');
      return;
    }

    setSelectedFile(file);
    onVideoSelect(file);
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
  };

  return (
    <Paper
      sx={{
        p: 4,
        textAlign: 'center',
        border: dragActive ? '2px dashed' : '2px dashed',
        borderColor: dragActive ? 'primary.main' : 'grey.300',
        backgroundColor: dragActive ? 'action.hover' : 'background.paper',
        cursor: disabled ? 'not-allowed' : 'pointer',
        transition: 'all 0.3s',
        '&:hover': !disabled ? {
          borderColor: 'primary.main',
          backgroundColor: 'action.hover'
        } : {}
      }}
      onDragEnter={handleDrag}
      onDragLeave={handleDrag}
      onDragOver={handleDrag}
      onDrop={handleDrop}
    >
      <input
        type="file"
        id="video-upload"
        accept="video/*"
        style={{ display: 'none' }}
        onChange={handleChange}
        disabled={disabled}
      />

      {selectedFile ? (
        <Box>
          <VideoIcon sx={{ fontSize: 80, color: 'primary.main', mb: 2 }} />
          <Typography variant="h6" gutterBottom>
            {selectedFile.name}
          </Typography>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            Tamaño: {formatFileSize(selectedFile.size)}
          </Typography>
          <Button
            variant="outlined"
            onClick={() => {
              setSelectedFile(null);
              document.getElementById('video-upload').value = '';
            }}
            sx={{ mt: 2 }}
            disabled={disabled}
          >
            Cambiar video
          </Button>
        </Box>
      ) : (
        <Box>
          <UploadIcon sx={{ fontSize: 80, color: 'text.secondary', mb: 2 }} />
          <Typography variant="h6" gutterBottom>
            Arrastra un video aquí
          </Typography>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            o
          </Typography>
          <label htmlFor="video-upload">
            <Button
              variant="contained"
              component="span"
              sx={{ mt: 2 }}
              disabled={disabled}
            >
              Seleccionar video
            </Button>
          </label>
          <Typography variant="caption" display="block" sx={{ mt: 2 }} color="text.secondary">
            Formatos soportados: MP4, AVI, MOV, MKV (máx. 500MB)
          </Typography>
        </Box>
      )}
    </Paper>
  );
}
