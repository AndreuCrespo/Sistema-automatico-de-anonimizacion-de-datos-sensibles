import { useState } from 'react';
import { Box, Button, Typography, Paper } from '@mui/material';
import { CloudUpload as CloudUploadIcon } from '@mui/icons-material';

/**
 * Componente para subir imagenes.
 * Permite drag & drop o seleccion manual.
 */
function ImageUpload({ onImageSelect }) {
  const [isDragging, setIsDragging] = useState(false);

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);

    const files = e.dataTransfer.files;
    if (files.length > 0) {
      handleFile(files[0]);
    }
  };

  const handleFileInput = (e) => {
    const files = e.target.files;
    if (files.length > 0) {
      handleFile(files[0]);
    }
  };

  const handleFile = (file) => {
    // Validar que sea una imagen
    if (!file.type.startsWith('image/')) {
      alert('Por favor selecciona un archivo de imagen');
      return;
    }

    // Validar tamano (max 10MB)
    const maxSize = 10 * 1024 * 1024;
    if (file.size > maxSize) {
      alert('El archivo es demasiado grande. Maximo 10MB');
      return;
    }

    onImageSelect(file);
  };

  return (
    <Paper
      elevation={isDragging ? 8 : 3}
      sx={{
        p: 4,
        textAlign: 'center',
        backgroundColor: isDragging ? 'action.hover' : 'background.paper',
        border: '2px dashed',
        borderColor: isDragging ? 'primary.main' : 'divider',
        transition: 'all 0.3s ease',
        cursor: 'pointer'
      }}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
    >
      <CloudUploadIcon sx={{ fontSize: 64, color: 'primary.main', mb: 2 }} />

      <Typography variant="h6" gutterBottom>
        Arrastra una imagen aqui
      </Typography>

      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
        o haz clic en el boton para seleccionar
      </Typography>

      <Button
        variant="contained"
        component="label"
        startIcon={<CloudUploadIcon />}
      >
        Seleccionar Imagen
        <input
          type="file"
          hidden
          accept="image/*"
          onChange={handleFileInput}
        />
      </Button>

      <Typography variant="caption" display="block" sx={{ mt: 2 }} color="text.secondary">
        Formatos aceptados: JPG, PNG, BMP (Max 10MB)
      </Typography>
    </Paper>
  );
}

export default ImageUpload;
