import { useState } from 'react';
import {
  Box,
  Typography,
  Alert,
  AlertTitle,
  Paper
} from '@mui/material';

import ImageUpload from '../components/ImageUpload';
import ImagePreview from '../components/ImagePreview';
import Controls from '../components/Controls';
import ClassSelector from '../components/ClassSelector';
import { anonymizeImage } from '../services/api';

export default function ImageProcessing() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [originalImageUrl, setOriginalImageUrl] = useState(null);
  const [anonymizedImage, setAnonymizedImage] = useState(null);
  const [metadata, setMetadata] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [selectedClasses, setSelectedClasses] = useState(['face', 'plate']);

  const handleImageSelect = (file) => {
    setSelectedFile(file);
    setOriginalImageUrl(URL.createObjectURL(file));
    setAnonymizedImage(null);
    setMetadata(null);
    setError(null);
  };

  const handleProcess = async (options) => {
    if (!selectedFile) {
      setError('No hay imagen seleccionada');
      return;
    }

    if (selectedClasses.length === 0) {
      setError('Selecciona al menos una clase para detectar');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      // Mapear clases seleccionadas a opciones del backend
      const processOptions = {
        ...options,
        detectFaces: selectedClasses.includes('face'),
        detectPlates: selectedClasses.includes('plate'),
        // Aquí se añadirían más opciones para COCO classes cuando estén implementadas
      };

      const result = await anonymizeImage(selectedFile, processOptions);
      setAnonymizedImage(result.blob);
      setMetadata(result.metadata);
    } catch (err) {
      console.error('Error al anonimizar imagen:', err);
      setError(
        err.response?.data?.detail ||
        'Error al procesar la imagen. Por favor intenta de nuevo.'
      );
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setSelectedFile(null);
    setOriginalImageUrl(null);
    setAnonymizedImage(null);
    setMetadata(null);
    setError(null);
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom sx={{ fontWeight: 600 }}>
        Image Processing
      </Typography>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
        Upload an image to detect and anonymize sensitive data
      </Typography>

      {/* Mensaje de error */}
      {error && (
        <Alert severity="error" sx={{ mb: 3, borderRadius: 3 }} onClose={() => setError(null)}>
          <AlertTitle>Error</AlertTitle>
          {error}
        </Alert>
      )}

      {/* Upload de imagen */}
      {!selectedFile ? (
        <ImageUpload onImageSelect={handleImageSelect} />
      ) : (
        <Box>
          {/* Selector de clases */}
          <Paper sx={{ p: 3, mb: 3, borderRadius: 3 }}>
            <ClassSelector
              selectedClasses={selectedClasses}
              onSelectionChange={setSelectedClasses}
              disabled={loading}
            />
            <Alert severity="info" sx={{ mt: 2, borderRadius: 2 }}>
              <AlertTitle>Note</AlertTitle>
              Currently, only <strong>Face</strong> and <strong>License Plate</strong> detection are available.
              Other COCO classes will be enabled in future updates.
            </Alert>
          </Paper>

          {/* Controles y preview */}
          <Paper sx={{ p: 3 }}>
            <Controls
              onProcess={handleProcess}
              onReset={handleReset}
              disabled={!selectedFile}
              loading={loading}
            />

            <ImagePreview
              originalImage={originalImageUrl}
              anonymizedImage={anonymizedImage}
              metadata={metadata}
            />
          </Paper>
        </Box>
      )}
    </Box>
  );
}
